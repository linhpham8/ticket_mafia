#!/usr/bin/env python3
"""
PRISM Token Tracker
Track token usage across all AI sessions for a PRISM project.

Storage: .prism/token-usage.json (inside the project)

Usage:
  # Auto-sync from Claude Code session files:
  python .prism/core/tools/token_tracker.py sync

  # Manually log a session (Copilot, Codex, Cursor, etc.):
  python .prism/core/tools/token_tracker.py log --agent copilot --input 5000 --output 1200
  python .prism/core/tools/token_tracker.py log --agent codex --input 8000 --output 2100 --model gpt-4o --note "sprint-v1 implement"

  # Show report:
  python .prism/core/tools/token_tracker.py report
  python .prism/core/tools/token_tracker.py report --detail

  # Install Claude Code Stop hook (auto-sync after every session):
  python .prism/core/tools/token_tracker.py install-hook
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

def find_project_root() -> Path:
    """Walk up from CWD until we find .prism/."""
    cwd = Path(os.getcwd()).resolve()
    for candidate in [cwd, *cwd.parents]:
        if (candidate / ".prism").is_dir():
            return candidate
    # fallback: use CWD
    return cwd


def token_usage_path(project_root: Path) -> Path:
    return project_root / ".prism" / "token-usage.json"


# ---------------------------------------------------------------------------
# Claude Code session path encoding
# Encodes an absolute path to the folder name Claude Code uses under
# ~/.claude/projects/  e.g. /home/user/my-proj → -home-user-my-proj
# ---------------------------------------------------------------------------

def encode_project_path(path: Path) -> str:
    # Claude Code replaces both '/' and '.' with '-'
    return str(path).replace("/", "-").replace(".", "-")


def find_claude_sessions(project_root: Path) -> list[Path]:
    """Return all *.jsonl session files for this project in Claude Code storage."""
    claude_projects_dir = Path.home() / ".claude" / "projects"
    if not claude_projects_dir.exists():
        return []
    encoded = encode_project_path(project_root)
    project_dir = claude_projects_dir / encoded
    if not project_dir.exists():
        return []
    return sorted(project_dir.glob("*.jsonl"))


def find_codex_sessions(project_root: Path) -> list[Path]:
    """Return Codex session files whose cwd matches project_root."""
    codex_sessions_dir = Path.home() / ".codex" / "sessions"
    if not codex_sessions_dir.exists():
        return []
    result = []
    for jf in sorted(codex_sessions_dir.rglob("*.jsonl")):
        # Peek at first few lines for session_meta cwd
        try:
            with open(jf, encoding="utf-8", errors="replace") as f:
                for raw in f:
                    raw = raw.strip()
                    if not raw:
                        continue
                    try:
                        obj = json.loads(raw)
                    except json.JSONDecodeError:
                        continue
                    if obj.get("type") == "session_meta":
                        cwd = obj.get("payload", {}).get("cwd", "")
                        if Path(cwd).resolve() == project_root.resolve():
                            result.append(jf)
                        break  # only need first session_meta
        except OSError:
            continue
    return result


# ---------------------------------------------------------------------------
# Parse a single Codex JSONL session file
# ---------------------------------------------------------------------------

def parse_codex_session(jsonl_path: Path) -> dict:
    """
    Read one Codex session .jsonl and return aggregated token counts.
    Uses the last 'token_count' event which carries cumulative totals.
    """
    totals = {
        "session_id": jsonl_path.stem,
        "agent": "codex",
        "model": "",
        "date": "",
        "input_tokens": 0,
        "cache_creation_tokens": 0,
        "cache_read_tokens": 0,
        "output_tokens": 0,
        "total_input_equiv": 0,
        "messages": 0,
        "source_file": str(jsonl_path),
    }

    last_token_usage: dict = {}
    earliest_ts = None

    with open(jsonl_path, encoding="utf-8", errors="replace") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError:
                continue

            ts = obj.get("timestamp", "")
            if ts and (earliest_ts is None or ts < earliest_ts):
                earliest_ts = ts

            payload = obj.get("payload", {})

            # model from response_item assistant messages
            if obj.get("type") == "response_item":
                if not totals["model"] and payload.get("role") == "assistant":
                    # model usually not in payload directly for codex,
                    # try session_meta or config
                    pass

            # cumulative token count events — keep the last one
            if obj.get("type") == "event_msg" and payload.get("type") == "token_count":
                usage = payload.get("info", {}).get("total_token_usage", {})
                if usage:
                    last_token_usage = usage

            # count assistant turns as messages
            if obj.get("type") == "response_item" and payload.get("role") == "assistant":
                totals["messages"] += 1

    # extract model from session files if available
    # try config.toml as fallback
    config_path = Path.home() / ".codex" / "config.toml"
    if config_path.exists():
        for line in config_path.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("model"):
                totals["model"] = line.split("=")[-1].strip().strip('"\'')
                break

    if earliest_ts:
        totals["date"] = earliest_ts[:10]

    if last_token_usage:
        totals["input_tokens"] = last_token_usage.get("input_tokens", 0)
        totals["cache_read_tokens"] = last_token_usage.get("cached_input_tokens", 0)
        totals["output_tokens"] = last_token_usage.get("output_tokens", 0)
        totals["total_input_equiv"] = (
            totals["input_tokens"] + totals["cache_read_tokens"]
        )

    return totals


# ---------------------------------------------------------------------------
# Parse a single Claude Code JSONL session file
# ---------------------------------------------------------------------------

def parse_claude_session(jsonl_path: Path) -> dict:
    """
    Read one Claude Code .jsonl file and return aggregated token counts.

    Returns:
    {
        "session_id": str,
        "agent": "claude-code",
        "model": str,
        "date": "YYYY-MM-DD",
        "input_tokens": int,          # real (non-cached) input
        "cache_creation_tokens": int,  # written to prompt cache
        "cache_read_tokens": int,      # read from prompt cache
        "output_tokens": int,
        "total_input_equiv": int,      # input + cache_creation + cache_read
        "messages": int,
        "source_file": str,
    }
    """
    totals = {
        "session_id": jsonl_path.stem,
        "agent": "claude-code",
        "model": "",
        "date": "",
        "input_tokens": 0,
        "cache_creation_tokens": 0,
        "cache_read_tokens": 0,
        "output_tokens": 0,
        "total_input_equiv": 0,
        "messages": 0,
        "source_file": str(jsonl_path),
    }
    earliest_ts = None

    with open(jsonl_path, encoding="utf-8", errors="replace") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError:
                continue

            msg = obj.get("message")
            if not isinstance(msg, dict):
                continue

            usage = msg.get("usage")
            if not isinstance(usage, dict):
                continue

            totals["messages"] += 1
            totals["input_tokens"] += usage.get("input_tokens", 0)
            totals["cache_creation_tokens"] += usage.get("cache_creation_input_tokens", 0)
            totals["cache_read_tokens"] += usage.get("cache_read_input_tokens", 0)
            totals["output_tokens"] += usage.get("output_tokens", 0)

            if not totals["model"] and msg.get("model"):
                totals["model"] = msg["model"]

            ts = obj.get("timestamp", "")
            if ts and (earliest_ts is None or ts < earliest_ts):
                earliest_ts = ts

    if earliest_ts:
        try:
            totals["date"] = earliest_ts[:10]
        except Exception:
            totals["date"] = ""

    totals["total_input_equiv"] = (
        totals["input_tokens"]
        + totals["cache_creation_tokens"]
        + totals["cache_read_tokens"]
    )
    return totals


# ---------------------------------------------------------------------------
# Storage helpers
# ---------------------------------------------------------------------------

def load_store(project_root: Path) -> dict:
    path = token_usage_path(project_root)
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    prism_config = project_root / "prism-config.md"
    project_name = project_root.name
    if prism_config.exists():
        for line in prism_config.read_text(encoding="utf-8").splitlines():
            m = re.search(r'name:\s*["\']?([^"\'\\n]+)["\']?', line)
            if m:
                project_name = m.group(1).strip()
                break
    return {
        "project": project_name,
        "project_root": str(project_root),
        "created": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "sessions": [],
    }


def save_store(project_root: Path, store: dict) -> None:
    path = token_usage_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    store["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(store, f, indent=2, ensure_ascii=False)


def existing_session_ids(store: dict) -> set:
    return {s.get("session_id", "") for s in store.get("sessions", [])}


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def _sync_sessions(
    session_files: list[Path],
    parser,
    store: dict,
    known: set,
) -> tuple[int, int]:
    added, updated = 0, 0
    for jf in session_files:
        parsed = parser(jf)
        if parsed["messages"] == 0 and parsed["output_tokens"] == 0:
            continue
        sid = parsed["session_id"]
        if sid in known:
            for i, s in enumerate(store["sessions"]):
                if s.get("session_id") == sid:
                    store["sessions"][i] = parsed
                    updated += 1
                    break
        else:
            store["sessions"].append(parsed)
            known.add(sid)
            added += 1
    return added, updated


def cmd_sync(args, project_root: Path) -> int:
    """Auto-sync from Claude Code and Codex session files."""
    quiet = getattr(args, "quiet", False)

    claude_files = find_claude_sessions(project_root)
    codex_files = find_codex_sessions(project_root)

    if not claude_files and not codex_files:
        if not quiet:
            print("No session files found for this project.")
            print(f"Claude Code path: ~/.claude/projects/{encode_project_path(project_root)}/")
            print("Codex path:       ~/.codex/sessions/ (filtered by cwd)")
        return 1

    store = load_store(project_root)
    known = existing_session_ids(store)
    total_added, total_updated = 0, 0

    if claude_files:
        a, u = _sync_sessions(claude_files, parse_claude_session, store, known)
        total_added += a
        total_updated += u

    if codex_files:
        a, u = _sync_sessions(codex_files, parse_codex_session, store, known)
        total_added += a
        total_updated += u

    save_store(project_root, store)
    if not quiet:
        print(f"Sync complete. Added: {total_added}  Updated: {total_updated}")
        print(f"  Claude Code sessions: {len(claude_files)}")
        print(f"  Codex sessions:       {len(codex_files)}")
        print(f"Saved → {token_usage_path(project_root)}")
        _print_summary(store)
    return 0


def cmd_log(args, project_root: Path) -> int:
    """Manually log a session from any AI tool."""
    store = load_store(project_root)

    session_id = f"manual-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    entry = {
        "session_id": session_id,
        "agent": args.agent,
        "model": args.model or "",
        "date": args.date or datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "input_tokens": args.input,
        "cache_creation_tokens": 0,
        "cache_read_tokens": 0,
        "output_tokens": args.output,
        "total_input_equiv": args.input,
        "messages": args.messages or 0,
        "note": args.note or "",
        "source_file": "manual",
    }
    store["sessions"].append(entry)
    save_store(project_root, store)
    print(f"Logged session {session_id}")
    print(f"  Agent:  {entry['agent']}  Model: {entry['model'] or '(not specified)'}")
    print(f"  Input:  {entry['input_tokens']:,} tokens")
    print(f"  Output: {entry['output_tokens']:,} tokens")
    print(f"Saved → {token_usage_path(project_root)}")
    return 0


def cmd_install_hook(args, project_root: Path) -> int:
    """Install Claude Code Stop hook to auto-sync tokens after each session."""
    import stat as stat_mod

    claude_dir = project_root / ".claude"
    settings_path = claude_dir / "settings.json"
    claude_dir.mkdir(exist_ok=True)

    # load or init settings
    if settings_path.exists():
        with open(settings_path, encoding="utf-8") as f:
            try:
                settings = json.load(f)
            except json.JSONDecodeError:
                settings = {}
    else:
        settings = {}

    hook_cmd = "python .prism/core/tools/token_tracker.py sync --quiet"

    hooks = settings.setdefault("hooks", {})
    stop_hooks = hooks.setdefault("Stop", [])

    # check if already installed
    for entry in stop_hooks:
        if isinstance(entry, dict):
            for h in entry.get("hooks", []):
                if "token_tracker" in h.get("command", ""):
                    print("Hook already installed.")
                    return 0

    stop_hooks.append({
        "matcher": "",
        "hooks": [{"type": "command", "command": hook_cmd}],
    })

    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)

    print(f"Hook installed → {settings_path}")
    print(f"Command: {hook_cmd}")
    print("Claude Code will now auto-sync tokens after every session.")
    return 0


def cmd_report(args, project_root: Path) -> int:
    """Print token usage report."""
    store = load_store(project_root)
    sessions = store.get("sessions", [])

    if not sessions:
        print("No sessions recorded yet.")
        print("  Run: python .prism/core/tools/token_tracker.py sync")
        print("  Or:  python .prism/core/tools/token_tracker.py log --agent <name> --input N --output N")
        return 0

    _print_summary(store)

    if args.detail:
        _print_detail(store)

    return 0


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def _aggregate(sessions: list) -> dict:
    a = {
        "input_tokens": 0,
        "cache_creation_tokens": 0,
        "cache_read_tokens": 0,
        "output_tokens": 0,
        "total_input_equiv": 0,
        "messages": 0,
        "sessions": len(sessions),
    }
    for s in sessions:
        a["input_tokens"] += s.get("input_tokens", 0)
        a["cache_creation_tokens"] += s.get("cache_creation_tokens", 0)
        a["cache_read_tokens"] += s.get("cache_read_tokens", 0)
        a["output_tokens"] += s.get("output_tokens", 0)
        a["total_input_equiv"] += s.get("total_input_equiv", s.get("input_tokens", 0))
        a["messages"] += s.get("messages", 0)
    return a


def _print_summary(store: dict) -> None:
    sessions = store.get("sessions", [])
    a = _aggregate(sessions)

    # group by agent
    agents: dict[str, list] = {}
    for s in sessions:
        ag = s.get("agent", "unknown")
        agents.setdefault(ag, []).append(s)

    print()
    print("=" * 58)
    print(f"  PRISM TOKEN USAGE — {store.get('project', '?')}")
    print("=" * 58)
    print(f"  Sessions  : {a['sessions']}")
    print(f"  Messages  : {a['messages']:,}")
    print()
    print("  INPUT")
    print(f"    Real input tokens     : {a['input_tokens']:>12,}")
    print(f"    Cache creation tokens : {a['cache_creation_tokens']:>12,}")
    print(f"    Cache read tokens     : {a['cache_read_tokens']:>12,}")
    print(f"    ─────────────────────────────────")
    print(f"    Total input equiv     : {a['total_input_equiv']:>12,}")
    print()
    print("  OUTPUT")
    print(f"    Output tokens         : {a['output_tokens']:>12,}")
    print()
    print(f"  GRAND TOTAL (input+output): {a['total_input_equiv'] + a['output_tokens']:>10,}")
    print()

    if len(agents) > 1:
        print("  BY AGENT")
        for ag, slist in sorted(agents.items()):
            aa = _aggregate(slist)
            print(f"    {ag:<18} input: {aa['total_input_equiv']:>10,}  output: {aa['output_tokens']:>9,}  sessions: {aa['sessions']}")
        print()

    print("=" * 58)


def _print_detail(store: dict) -> None:
    sessions = store.get("sessions", [])
    print()
    print("  SESSIONS DETAIL")
    print(f"  {'Date':<12} {'Agent':<14} {'Model':<26} {'Input-eq':>10} {'Output':>9} {'Msgs':>5}")
    print("  " + "-" * 80)
    for s in sorted(sessions, key=lambda x: x.get("date", "")):
        date = s.get("date", "?")[:10]
        agent = s.get("agent", "?")[:13]
        model = (s.get("model") or "?")[:25]
        inp = s.get("total_input_equiv", s.get("input_tokens", 0))
        out = s.get("output_tokens", 0)
        msgs = s.get("messages", 0)
        note = s.get("note", "")
        print(f"  {date:<12} {agent:<14} {model:<26} {inp:>10,} {out:>9,} {msgs:>5}", end="")
        if note:
            print(f"  # {note}", end="")
        print()
    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="PRISM Token Tracker — track AI token usage across project sessions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # sync
    p_sync = sub.add_parser("sync", help="Auto-sync from Claude Code session files")
    p_sync.add_argument("--project-root", help="Project root (default: auto-detect from CWD)")
    p_sync.add_argument("--quiet", action="store_true", help="Suppress output (for hook use)")

    # install-hook
    p_hook = sub.add_parser("install-hook", help="Install Claude Code Stop hook for auto-sync")
    p_hook.add_argument("--project-root", help="Project root (default: auto-detect from CWD)")

    # log
    p_log = sub.add_parser("log", help="Manually log a session (any AI tool)")
    p_log.add_argument("--agent", required=True,
                       help="AI tool name: copilot | codex | cursor | gemini | claude-code | ...")
    p_log.add_argument("--input", type=int, required=True, help="Input token count")
    p_log.add_argument("--output", type=int, required=True, help="Output token count")
    p_log.add_argument("--model", help="Model name (optional)")
    p_log.add_argument("--date", help="Date YYYY-MM-DD (default: today)")
    p_log.add_argument("--messages", type=int, help="Number of messages in session")
    p_log.add_argument("--note", help="Free-text note (e.g. phase, sprint, task)")
    p_log.add_argument("--project-root", help="Project root (default: auto-detect from CWD)")

    # report
    p_rep = sub.add_parser("report", help="Show token usage report")
    p_rep.add_argument("--detail", action="store_true", help="Show per-session breakdown")
    p_rep.add_argument("--project-root", help="Project root (default: auto-detect from CWD)")

    args = parser.parse_args()

    # resolve project root
    raw_root = getattr(args, "project_root", None)
    if raw_root:
        project_root = Path(raw_root).resolve()
    else:
        project_root = find_project_root()

    if not (project_root / ".prism").exists():
        print(f"ERROR: .prism/ not found in {project_root}")
        print("Run this script from inside a PRISM project, or pass --project-root.")
        return 1

    if args.command == "sync":
        return cmd_sync(args, project_root)
    elif args.command == "log":
        return cmd_log(args, project_root)
    elif args.command == "report":
        return cmd_report(args, project_root)
    elif args.command == "install-hook":
        return cmd_install_hook(args, project_root)

    return 0


if __name__ == "__main__":
    sys.exit(main())
