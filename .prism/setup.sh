#!/bin/sh
# PRISM Setup Script
# Installs PRISM adapter files to your project.
# Usage:
#   From the project root after unzipping a release to .prism:
#     ./.prism/setup.sh
#     ./.prism/setup.sh --style freedom
#   From inside the PRISM directory:
#     ./setup.sh [--style guided|freedom] [--project-root /path]
#   Upgrade:
#     ./.prism/setup.sh --upgrade
#     ./.prism/setup.sh --upgrade --force   # re-apply even at same version

set -e

# --- Configuration ---
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VERSION_FILE="$SCRIPT_DIR/VERSION"
PLATFORMS_HELPER="$SCRIPT_DIR/scripts/platforms.py"
PROJECT_ROOT=""
PLATFORM="core"
MODE="guided"
MODE_EXPLICIT=false
ACTION="install"  # install | upgrade
FORCE=false

# --- Colors (if terminal supports them) ---
if [ -t 1 ]; then
    BOLD="\033[1m"
    GREEN="\033[32m"
    YELLOW="\033[33m"
    RED="\033[31m"
    CYAN="\033[36m"
    RESET="\033[0m"
else
    BOLD="" GREEN="" YELLOW="" RED="" CYAN="" RESET=""
fi

# --- Helpers ---
info()  { printf "${CYAN}[PRISM]${RESET} %s\n" "$1"; }
warn()  { printf "${YELLOW}[WARN]${RESET} %s\n" "$1"; }
fail()  { printf "${RED}[ERROR]${RESET} %s\n" "$1" >&2; }
ok()    { printf "${GREEN}[OK]${RESET}   %s\n" "$1"; }
header() { printf "\n${BOLD}%s${RESET}\n" "$1"; }
escape_sed_replacement() { printf '%s' "$1" | sed 's/[\\/&]/\\&/g'; }
read_framework_version() {
    if [ -f "$VERSION_FILE" ]; then
        tr -d '[:space:]' < "$VERSION_FILE"
    fi
}

# --- Platform registry (loaded from adapters/platforms.json via scripts/platforms.py) ---
# PLATFORM_DATA is TSV: key<TAB>label<TAB>dest<TAB>guided_src<TAB>freedom_src<TAB>legacy_dests(comma)
if [ ! -f "$PLATFORMS_HELPER" ]; then
    fail "Platform registry helper missing: $PLATFORMS_HELPER"
    exit 1
fi
PLATFORM_DATA=$(python3 "$PLATFORMS_HELPER" tsv 2>/dev/null) || {
    fail "Failed to load platform registry. Is python3 available?"
    exit 1
}
ALL_PLATFORM_KEYS=$(python3 "$PLATFORMS_HELPER" keys 2>/dev/null | tr '\n' ' ')
CORE_PLATFORM_KEYS=" claude copilot codex cursor"  # Default 4-platform install set; other 7 platforms install only when explicitly requested via --platform

# Get a single field from platform registry by key.
# Args: $1 = platform key, $2 = field index (1=key, 2=label, 3=dest, 4=guided_src, 5=freedom_src, 6=legacy_dests, 7=size_warning_chars)
# The "-" sentinel emitted by platforms.py for missing optional values is translated to empty.
get_platform_field() {
    _value=$(printf '%s\n' "$PLATFORM_DATA" | awk -F'\t' -v key="$1" -v idx="$2" '$1==key{print $idx; exit}')
    if [ "$_value" = "-" ]; then
        echo ""
    else
        echo "$_value"
    fi
}

# Absolute path to the source adapter inside the PRISM package for (platform, mode).
adapter_src() {
    _platform="$1"
    _mode="$2"
    if [ "$_mode" = "freedom" ]; then
        _rel=$(get_platform_field "$_platform" 5)
    else
        _rel=$(get_platform_field "$_platform" 4)
    fi
    [ -z "$_rel" ] && return 1
    echo "$SCRIPT_DIR/$_rel"
}

# Absolute destination path inside the project root for a given platform.
adapter_dest() {
    _platform="$1"
    _rel=$(get_platform_field "$_platform" 3)
    [ -z "$_rel" ] && return 1
    echo "$PROJECT_ROOT/$_rel"
}

# Comma-separated legacy dest paths for a platform (e.g. ".cursorrules" for cursor).
adapter_legacy_dests() {
    get_platform_field "$1" 6
}

# Soft size limit (chars) for a platform's adapter file (e.g. 12000 for Windsurf).
# Empty means no limit declared.
adapter_size_warning() {
    get_platform_field "$1" 7
}

# Emit a one-line warning if the installed adapter exceeds the platform's
# documented size limit. Does NOT fail or truncate — the tool will silently
# truncate on its own; we just surface that fact to the user.
warn_if_oversize() {
    _platform="$1"
    _dest="$2"
    _limit=$(adapter_size_warning "$_platform")
    [ -z "$_limit" ] && return 0
    [ ! -f "$_dest" ] && return 0
    _size=$(wc -c < "$_dest" | tr -d ' ')
    if [ "$_size" -gt "$_limit" ]; then
        warn "$_platform: adapter is ${_size} chars; ${_platform} loader limit is ${_limit} chars — content past byte ${_limit} will be truncated by the tool."
        warn "  See README §'Supported AI Coding Tools' for per-tool size caveats."
    fi
}

# True if the given key is in the registry.
is_known_platform() {
    case " $ALL_PLATFORM_KEYS " in
        *" $1 "*) return 0 ;;
        *) return 1 ;;
    esac
}

normalize_mode() {
    case "$1" in
        ""|guided|freedom)
            printf '%s' "$1"
            ;;
        freestyle)
            printf '%s' guided
            ;;
        *)
            return 1
            ;;
    esac
}

is_managed_package_path() {
    case "$1" in
        adapters/*|core/*|docs/*|scripts/*|legacy/*|sessions/*|dist/*|vi/*|README.md|README_vi.md|diagram.xml|prism-config.md|prism.json|setup.sh|setup.ps1|VERSION|MANIFEST.txt)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

prune_stale_package_files() {
    MANIFEST="$SCRIPT_DIR/MANIFEST.txt"

    if [ ! -f "$MANIFEST" ]; then
        warn "Package manifest not found; skipping stale .prism file cleanup"
        return
    fi

    PRUNED_LIST="${TMPDIR:-/tmp}/prism-pruned-$$.txt"
    : > "$PRUNED_LIST"

    find "$SCRIPT_DIR" -type f ! -path "$SCRIPT_DIR/backups/*" | while IFS= read -r file; do
        rel="${file#"$SCRIPT_DIR"/}"
        if is_managed_package_path "$rel" && ! grep -Fx -- "$rel" "$MANIFEST" >/dev/null 2>&1; then
            rm -f "$file"
            printf '%s\n' "$rel" >> "$PRUNED_LIST"
        fi
    done

    PRUNED_COUNT=$(wc -l < "$PRUNED_LIST" | tr -d ' ')
    if [ "$PRUNED_COUNT" -gt 0 ]; then
        ok "Removed $PRUNED_COUNT stale managed .prism file(s)"
    else
        ok "No stale managed .prism files found"
    fi
    rm -f "$PRUNED_LIST"

    for dir in adapters core docs scripts legacy sessions dist vi; do
        if [ -d "$SCRIPT_DIR/$dir" ]; then
            find "$SCRIPT_DIR/$dir" -depth -type d -empty -exec rmdir {} \; 2>/dev/null || true
        fi
    done
}

migrate_legacy_prism_backups() {
    LEGACY_BACKUP_DIR="$SCRIPT_DIR/backups"
    BACKUP_ROOT="$PROJECT_ROOT/.prism-backups"

    if [ ! -d "$LEGACY_BACKUP_DIR" ]; then
        return
    fi

    mkdir -p "$BACKUP_ROOT"
    LEGACY_TARGET="$BACKUP_ROOT/legacy-prism-backups-$(date +%Y-%m-%d-%H%M%S)"
    mv "$LEGACY_BACKUP_DIR" "$LEGACY_TARGET"
    ok "Moved legacy .prism/backups to $LEGACY_TARGET"
}

# Backup + remove legacy adapter paths (e.g. cursor's old .cursorrules) for a given platform.
# Args: $1 = platform key, $2 = backup directory (absolute)
migrate_legacy_adapter_paths() {
    _platform="$1"
    _backup_dir="$2"
    _legacy=$(adapter_legacy_dests "$_platform")
    [ -z "$_legacy" ] && return 0

    OLD_IFS="$IFS"
    IFS=','
    for legacy_rel in $_legacy; do
        IFS="$OLD_IFS"
        _abs="$PROJECT_ROOT/$legacy_rel"
        if [ -f "$_abs" ]; then
            mkdir -p "$_backup_dir"
            cp "$_abs" "$_backup_dir/$(basename "$_abs").legacy"
            rm -f "$_abs"
            ok "$_platform: removed legacy $legacy_rel (backup: $(basename "$_abs").legacy)"
        fi
        IFS=','
    done
    IFS="$OLD_IFS"
}

install_guided_precommit_hook() {
    # Guided mode relies on this hook as defense-in-depth against direct edits
    # to Living Truth files. Do not alter Freedom installs.
    if [ "$1" != "guided" ]; then
        return
    fi
    if [ ! -d "$PROJECT_ROOT/.git" ]; then
        warn "No .git directory found; skipped PRISM Living Truth pre-commit hook install"
        return
    fi
    HOOK_SRC="$SCRIPT_DIR/core/tools/precommit_living_truth.py"
    HOOK_DIR="$PROJECT_ROOT/.git/hooks"
    HOOK_DEST="$HOOK_DIR/pre-commit"
    if [ ! -f "$HOOK_SRC" ]; then
        warn "PRISM pre-commit hook source not found; skipped hook install"
        return
    fi
    mkdir -p "$HOOK_DIR"
    if [ -f "$HOOK_DEST" ]; then
        if grep -q "precommit_living_truth.py" "$HOOK_DEST" 2>/dev/null || grep -q "PRISM pre-commit hook" "$HOOK_DEST" 2>/dev/null; then
            ok "PRISM Living Truth pre-commit hook already installed"
        else
            warn "Existing git pre-commit hook found; PRISM Living Truth hook not installed automatically"
            warn "To enable it, chain $HOOK_SRC from $HOOK_DEST"
        fi
        return
    fi
    cp "$HOOK_SRC" "$HOOK_DEST"
    chmod +x "$HOOK_DEST"
    ok "Installed PRISM Living Truth pre-commit hook"
}

PRISM_VERSION="$(read_framework_version)"

if [ -z "$PRISM_VERSION" ]; then
    printf 'Could not resolve PRISM framework version from %s\n' "$VERSION_FILE" >&2
    exit 1
fi

# --- Parse Arguments ---
while [ $# -gt 0 ]; do
    case "$1" in
        --upgrade)
            ACTION="upgrade"
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --platform)
            PLATFORM="$2"
            shift 2
            ;;
        --mode)
            MODE="$2"
            MODE_EXPLICIT=true
            shift 2
            ;;
        --style)
            MODE="$2"
            MODE_EXPLICIT=true
            shift 2
            ;;
        --project-root)
            PROJECT_ROOT="$2"
            shift 2
            ;;
        --help|-h)
            echo "PRISM Setup v${PRISM_VERSION}"
            echo ""
            echo "Usage:"
            echo "  From the project root after unzipping a release:"
            echo "    ./.prism/setup.sh [OPTIONS]"
            echo "  From inside the PRISM directory:"
            echo "    ./setup.sh [OPTIONS]"
            echo ""
            echo "Actions:"
            echo "  (default)               Fresh install — set up PRISM for a new or existing project"
            echo "  --upgrade               Upgrade PRISM to v${PRISM_VERSION} (preserves docs and config values)"
            echo "  --force                 With --upgrade: re-apply even when installed version equals target"
            echo ""
            echo "Options:"
            echo "  --style <name>          guided | freedom (default: guided; install only, not upgrade)"
            echo "  --platform <name|core|all>  $(echo "$ALL_PLATFORM_KEYS" | sed 's/ *$//' | tr ' ' '|')|core|all (default: core = claude/copilot/codex/cursor)"
            echo "  --project-root <path>   Target project root (defaults to parent of PRISM directory)"
            echo "  -h, --help              Show this help"
            echo ""
            echo "Platforms supported:"
            # Use printf '%s\n' to ensure trailing newline so `while read` includes the last row.
            # Read all 7 TSV columns explicitly so size_warning_chars doesn't leak into the legacy slot.
            # AWK avoids the POSIX `read` empty-field-collapsing trap when IFS=\t.
            # Convert the "-" sentinel back to empty for human-friendly output.
            printf '%s\n' "$PLATFORM_DATA" | awk -F'\t' '
                {
                    k = $1; label = $2; dest = $3
                    legacy = ($6 == "-" ? "" : $6)
                    size_warn = ($7 == "-" ? "" : $7)
                    ann = ""
                    if (legacy != "") ann = "legacy: " legacy
                    if (size_warn != "") {
                        if (ann != "") ann = ann "; max: " size_warn " chars"
                        else ann = "max: " size_warn " chars"
                    }
                    if (ann != "") printf "  %-12s %-20s → %s  (%s)\n", k, label, dest, ann
                    else printf "  %-12s %-20s → %s\n", k, label, dest
                }'
            echo ""
            echo "Note: codex / opencode / kiro / antigravity all write to AGENTS.md."
            echo "      When --platform all is used, AGENTS.md is written once (dedupe by destination)."
            echo ""
            echo "Styles:"
            echo "  guided     Full framework with explicit commands (start product, approve, etc.)"
            echo "  freedom    No gates, no approval, no immutable versioning. Edit in-place. PERMANENT choice."
            echo ""
            echo "Examples:"
            echo "  ./.prism/setup.sh"
            echo "  ./.prism/setup.sh --style freedom"
            echo "  ./.prism/setup.sh --upgrade"
            echo "  ./.prism/setup.sh --upgrade --force"
            echo "  ./.prism/setup.sh --platform gemini --style guided"
            exit 0
            ;;
        *)
            warn "Unknown option: $1"
            shift
            ;;
    esac
done

REQUESTED_MODE="$MODE"
if ! MODE=$(normalize_mode "$MODE"); then
    warn "Invalid style: $REQUESTED_MODE"
    warn "Supported styles: guided, freedom"
    exit 1
fi

if [ "$MODE_EXPLICIT" = true ]; then
    if [ "$REQUESTED_MODE" = "freestyle" ]; then
        warn "freestyle has been removed. Using guided instead."
    fi
fi

# Validate --platform value
if [ "$PLATFORM" != "all" ] && [ "$PLATFORM" != "core" ] && ! is_known_platform "$PLATFORM"; then
    fail "Unknown platform: $PLATFORM"
    warn "Supported: $(echo "$ALL_PLATFORM_KEYS" | sed 's/  *$//') core all"
    exit 1
fi

# --- Determine Project Root ---
if [ -z "$PROJECT_ROOT" ]; then
    PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
fi

require_adapter_src() {
    local src="$1"

    if [ -f "$src" ]; then
        return 0
    fi

    fail "Source adapter not found: $src"
    cat >&2 <<EOF

This PRISM directory does not contain generated adapter outputs.
That usually means you are running setup.sh from a source checkout instead of a release package.

Use one of these paths:
  1. Recommended: build a release package, then run setup from the unzipped .prism directory:
       cd "$SCRIPT_DIR"
       ./scripts/release.sh
       unzip dist/prism-v${PRISM_VERSION}.zip -d /path/to/target-project
       cd /path/to/target-project
       ./.prism/setup.sh --style <guided|freedom>

  2. Local testing only: generate active adapters into this checkout, run setup, then remove generated adapter outputs before source validation or committing:
       cd "$SCRIPT_DIR"
       python3 scripts/generate_adapters.py --output-root .
       ./setup.sh --project-root /path/to/target-project --style <guided|freedom>

Source validation intentionally fails when generated active adapter outputs are left in the source tree.
EOF
    exit 1
}

# Resolve the list of platforms to install based on --platform value.
resolve_platforms() {
    if [ "$PLATFORM" = "all" ]; then
        echo "$ALL_PLATFORM_KEYS"
    elif [ "$PLATFORM" = "core" ]; then
        echo "$CORE_PLATFORM_KEYS"
    else
        echo "$PLATFORM"
    fi
}

# ===========================================================================
# ACTION: UPGRADE
# ===========================================================================
if [ "$ACTION" = "upgrade" ]; then
    header "PRISM Upgrade to v${PRISM_VERSION}"
    info "PRISM directory: $SCRIPT_DIR"
    info "Project root:    $PROJECT_ROOT"

    CONFIG_TEMPLATE="$SCRIPT_DIR/prism-config.md"
    CONFIG="$PROJECT_ROOT/prism-config.md"
    BACKUP_DIR="$PROJECT_ROOT/.prism-backups/pre-upgrade-$(date +%Y-%m-%d-%H%M%S)"

    # --- Step 1: Pre-flight check ---
    header "Step 1: Pre-flight Check"

    INSTALLED_VERSION=""
    if [ -f "$CONFIG" ]; then
        INSTALLED_VERSION=$(grep 'version:' "$CONFIG" | head -1 | sed 's/.*"\(.*\)".*/\1/' 2>/dev/null || echo "")
    fi

    if [ -z "$INSTALLED_VERSION" ]; then
        warn "Could not detect installed PRISM version from prism-config.md"
        warn "Treating as upgrade from unknown version"
        INSTALLED_VERSION="unknown"
    fi

    if [ "$INSTALLED_VERSION" = "$PRISM_VERSION" ] && [ "$FORCE" != true ]; then
        ok "Already at v${PRISM_VERSION}. Use --force to re-apply."
        exit 0
    fi

    if [ "$INSTALLED_VERSION" = "$PRISM_VERSION" ]; then
        info "Re-applying v${PRISM_VERSION} (--force)"
    else
        info "Installed: v${INSTALLED_VERSION} → Upgrading to: v${PRISM_VERSION}"
    fi

    # Read current mode from config (upgrade preserves mode, never changes it)
    CURRENT_MODE="guided"
    if [ -f "$CONFIG" ]; then
        CURRENT_MODE=$(grep 'mode:' "$CONFIG" | head -1 | sed 's/.*"\(.*\)".*/\1/' 2>/dev/null || echo "guided")
    fi

    CONFIG_MODE="$CURRENT_MODE"
    if ! CURRENT_MODE=$(normalize_mode "$CURRENT_MODE"); then
        warn "Unknown installed mode '$CONFIG_MODE'. Defaulting to guided for upgrade."
        CURRENT_MODE="guided"
    elif [ "$CONFIG_MODE" = "freestyle" ]; then
        warn "Legacy freestyle install detected. Upgrade will migrate it to guided."
    fi

    if [ "$CONFIG_MODE" = "freestyle" ]; then
        info "Mode: $CURRENT_MODE (legacy freestyle normalized)"
    else
        info "Mode: $CURRENT_MODE (preserved)"
    fi

    if [ "$MODE_EXPLICIT" = true ]; then
        warn "--style/--mode is ignored during upgrade. Style is preserved from existing config."
        warn "To change style after upgrade, reinstall with --style guided or --style freedom."
    fi

    # Scan docs for current state
    DOCS_DIR="$PROJECT_ROOT/docs"
    DRAFT_COUNT=0
    if [ -d "$DOCS_DIR" ]; then
        DRAFT_COUNT=$(grep -rl 'status: DRAFT' "$DOCS_DIR" 2>/dev/null | wc -l | tr -d ' ')
    fi

    # --- Step 2: Create backup ---
    header "Step 2: Backup"
    migrate_legacy_prism_backups
    BACKUP_ROOT="$PROJECT_ROOT/.prism-backups"
    mkdir -p "$BACKUP_ROOT"
    if [ ! -f "$BACKUP_ROOT/.gitignore" ]; then
        printf '*\n!.gitignore\n' > "$BACKUP_ROOT/.gitignore"
    fi
    mkdir -p "$BACKUP_DIR"

    for platform in $ALL_PLATFORM_KEYS; do
        dest=$(adapter_dest "$platform")
        if [ -f "$dest" ]; then
            # Multiple platforms may share a dest (e.g. AGENTS.md). Backing up
            # by basename is safe: subsequent iterations overwrite the same
            # file with identical content.
            cp "$dest" "$BACKUP_DIR/$(basename "$dest")"
            ok "Backed up: $(basename "$dest")"
        fi
        # Also back up any legacy paths (e.g. .cursorrules) before we delete them
        _legacy=$(adapter_legacy_dests "$platform")
        if [ -n "$_legacy" ]; then
            OLD_IFS="$IFS"
            IFS=','
            for legacy_rel in $_legacy; do
                IFS="$OLD_IFS"
                _legacy_abs="$PROJECT_ROOT/$legacy_rel"
                if [ -f "$_legacy_abs" ]; then
                    cp "$_legacy_abs" "$BACKUP_DIR/$(basename "$_legacy_abs").legacy"
                    ok "Backed up legacy: $legacy_rel"
                fi
                IFS=','
            done
            IFS="$OLD_IFS"
        fi
    done

    if [ -f "$CONFIG" ]; then
        cp "$CONFIG" "$BACKUP_DIR/prism-config.md"
        ok "Backed up: prism-config.md"
    fi

    ok "Backup saved to: $BACKUP_DIR"

    # --- Step 3: Remove stale managed package files ---
    header "Step 3: Package Cleanup"
    prune_stale_package_files

    # --- Step 4: Detect platforms from existing adapters ---
    if [ "$PLATFORM" = "all" ]; then
        # Auto-detect installed adapters by checking both current and legacy dests
        PLATFORMS=""
        for platform in $ALL_PLATFORM_KEYS; do
            dest=$(adapter_dest "$platform")
            found=false
            if [ -f "$dest" ]; then
                found=true
            else
                _legacy=$(adapter_legacy_dests "$platform")
                if [ -n "$_legacy" ]; then
                    OLD_IFS="$IFS"
                    IFS=','
                    for legacy_rel in $_legacy; do
                        IFS="$OLD_IFS"
                        if [ -f "$PROJECT_ROOT/$legacy_rel" ]; then
                            found=true
                            break
                        fi
                        IFS=','
                    done
                    IFS="$OLD_IFS"
                fi
            fi
            if [ "$found" = true ]; then
                PLATFORMS="${PLATFORMS} $platform"
            fi
        done
        if [ -z "$PLATFORMS" ]; then
            info "No existing adapters found; installing all platforms"
            PLATFORMS="$ALL_PLATFORM_KEYS"
        fi
    else
        PLATFORMS=" $PLATFORM"
    fi
    info "Platforms:$PLATFORMS"

    # --- Step 5: Update adapters (dedupe by dest path) ---
    header "Step 5: Adapter Update"

    INSTALLED_DESTS=""
    for platform in $PLATFORMS; do
        src=$(adapter_src "$platform" "$CURRENT_MODE")
        dest=$(adapter_dest "$platform")
        adapter_name=$(basename "$dest")

        require_adapter_src "$src"

        # Migrate any legacy paths for this platform (e.g. cursor .cursorrules → .cursor/rules/prism.mdc)
        migrate_legacy_adapter_paths "$platform" "$BACKUP_DIR"

        # Dedupe: skip if this dest has already been written by another platform (e.g. AGENTS.md)
        case " $INSTALLED_DESTS " in
            *" $dest "*)
                info "$platform: skipped — $adapter_name already written by another platform"
                continue
                ;;
        esac

        if [ ! -f "$dest" ]; then
            mkdir -p "$(dirname "$dest")"
            cp "$src" "$dest"
            ok "$adapter_name: fresh install ($platform)"
            warn_if_oversize "$platform" "$dest"
            INSTALLED_DESTS="$INSTALLED_DESTS $dest"
            continue
        fi

        # Check if user customized the adapter (matches any known canonical source)
        FOUND_MATCH=false
        for check_mode in guided freedom; do
            for check_platform in $ALL_PLATFORM_KEYS; do
                check_src=$(adapter_src "$check_platform" "$check_mode")
                if [ -f "$check_src" ] && diff -q "$dest" "$check_src" >/dev/null 2>&1; then
                    FOUND_MATCH=true
                    break 2
                fi
            done
        done

        mkdir -p "$(dirname "$dest")"
        if [ "$FOUND_MATCH" = true ]; then
            cp "$src" "$dest"
            ok "$adapter_name: updated (no customizations detected) — $platform"
        else
            cp "$src" "$dest"
            warn "$adapter_name: updated — your previous version is in $BACKUP_DIR"
            warn "  Review the backup and re-add any custom rules if needed"
        fi
        warn_if_oversize "$platform" "$dest"
        INSTALLED_DESTS="$INSTALLED_DESTS $dest"
    done

    # --- Step 6: Update config version and normalized mode ---
    header "Step 6: Config Version"

    if [ ! -f "$CONFIG" ] && [ -f "$CONFIG_TEMPLATE" ]; then
        cp "$CONFIG_TEMPLATE" "$CONFIG"
        ok "Created missing project config at $CONFIG"
    fi

    if [ -f "$CONFIG" ]; then
        if grep -q 'version:' "$CONFIG"; then
            sed -i.bak "s/version: \".*\"/version: \"$PRISM_VERSION\"/" "$CONFIG" 2>/dev/null || true
            rm -f "${CONFIG}.bak"
            ok "Updated prism.version to $PRISM_VERSION"
        else
            sed -i.bak "/^prism:/a\\
  version: \"$PRISM_VERSION\"             # installed PRISM version" "$CONFIG" 2>/dev/null || true
            rm -f "${CONFIG}.bak"
            ok "Added prism.version field ($PRISM_VERSION)"
        fi

        if grep -q 'mode:' "$CONFIG"; then
            sed -i.bak "s/mode: \".*\"/mode: \"$CURRENT_MODE\"/" "$CONFIG" 2>/dev/null || true
            rm -f "${CONFIG}.bak"
            if [ "$CONFIG_MODE" = "freestyle" ]; then
                ok "Migrated prism.mode from freestyle to $CURRENT_MODE"
            else
                ok "Preserved prism.mode as $CURRENT_MODE"
            fi
        else
            sed -i.bak "/^prism:/a\\
  mode: \"$CURRENT_MODE\"                  # guided | freedom" "$CONFIG" 2>/dev/null || true
            rm -f "${CONFIG}.bak"
            ok "Added prism.mode field ($CURRENT_MODE)"
        fi
    fi

    # --- Step 7: Ensure active workflow directories exist ---
    SPRINT_SUPPORT_COUNT=0
    if [ -d "$DOCS_DIR" ]; then
        # Phase 9: ensure nested phase folders exist for upgrades from pre-Phase-9 layouts.
        mkdir -p "$DOCS_DIR/product/epics"
        mkdir -p "$DOCS_DIR/design"
        mkdir -p "$DOCS_DIR/architecture"
        mkdir -p "$DOCS_DIR/testing"
        for sprint_dir in "$DOCS_DIR"/sprint-v*; do
            if [ -d "$sprint_dir" ]; then
                mkdir -p "$sprint_dir/product/proposals/epics"
                mkdir -p "$sprint_dir/design/proposals"
                mkdir -p "$sprint_dir/architecture/proposals"
                mkdir -p "$sprint_dir/testing/proposals"
                touch "$sprint_dir/product/proposals/epics/.gitkeep"
                mkdir -p "$sprint_dir/tempo/in-progress"
                mkdir -p "$sprint_dir/tempo/completed"
                mkdir -p "$sprint_dir/changes"
                SPRINT_SUPPORT_COUNT=$((SPRINT_SUPPORT_COUNT + 1))
            fi
        done
    fi

    if [ "$SPRINT_SUPPORT_COUNT" -gt 0 ]; then
        ok "Ensured tempo/ and changes/ directories for $SPRINT_SUPPORT_COUNT sprint(s)"
    fi

    install_guided_precommit_hook "$CURRENT_MODE"

    # --- Step 8: Report ---
    header "Upgrade Complete: v${INSTALLED_VERSION} → v${PRISM_VERSION}"
    echo ""
    ok "Core:     Updated (phase engines, orchestrator, templates)"
    info "Adapter:  See results above"
    ok "Config:   Project-root prism-config.md updated, project values preserved"
    if [ "$DRAFT_COUNT" -gt 0 ]; then
        warn "Docs:     $DRAFT_COUNT in-progress doc(s) — will be checked on next resume"
    else
        ok "Docs:     No in-progress documents"
    fi
    ok "Backup:   $BACKUP_DIR"
    echo ""
    info "Your existing sprints and approved documents are untouched."
    info "Next: open your AI tool and continue where you left off."
    info "To rollback: restore files from $BACKUP_DIR"
    echo ""
    exit 0
fi

# ===========================================================================
# ACTION: INSTALL
# ===========================================================================

header "PRISM Setup v${PRISM_VERSION}"
info "PRISM directory: $SCRIPT_DIR"
info "Project root:    $PROJECT_ROOT"
info "Style:           $MODE"

PLATFORMS=$(resolve_platforms)
info "Adapters:        $PLATFORMS"

# Hint about extended platforms when running default core install (only on TTY install, not during upgrade)
if [ "$PLATFORM" = "core" ] && [ "$ACTION" = "install" ] && [ -t 1 ]; then
    EXTENDED_KEYS=""
    for k in $ALL_PLATFORM_KEYS; do
        case " $CORE_PLATFORM_KEYS " in
            *" $k "*) ;;
            *) EXTENDED_KEYS="$EXTENDED_KEYS $k" ;;
        esac
    done
    EXTENDED_KEYS=$(echo "$EXTENDED_KEYS" | sed 's/^ *//')
    if [ -n "$EXTENDED_KEYS" ]; then
        info "(extended platforms not installed: $EXTENDED_KEYS — re-run \`./setup.sh --platform <name>\` or \`--platform all\` to add)"
    fi
fi

# --- Install Adapters (dedupe by dest path) ---
header "Installing Adapters"

INSTALLED_DESTS=""
for platform in $PLATFORMS; do
    src=$(adapter_src "$platform" "$MODE")
    dest=$(adapter_dest "$platform")

    require_adapter_src "$src"

    # Dedupe: skip if this dest has already been written (e.g. multiple platforms → AGENTS.md)
    case " $INSTALLED_DESTS " in
        *" $dest "*)
            info "Skipping $platform — $(basename "$dest") already installed by another platform"
            continue
            ;;
    esac

    if [ -f "$dest" ]; then
        warn "$(basename "$dest") already exists at $dest"
        printf "  Overwrite? [y/N] "
        read -r answer
        case "$answer" in
            [yY]*) ;;
            *) info "Skipping $(basename "$dest")"; continue ;;
        esac
    fi

    mkdir -p "$(dirname "$dest")"
    cp "$src" "$dest"
    ok "Installed $(basename "$dest") ($MODE) → $dest  [$platform]"
    warn_if_oversize "$platform" "$dest"
    INSTALLED_DESTS="$INSTALLED_DESTS $dest"
done

# --- Create Docs Directory ---
header "Setting Up Documents Directory"

DOCS_DIR="$PROJECT_ROOT/docs"
mkdir -p "$DOCS_DIR"
ok "Docs directory ready: $DOCS_DIR"

# --- Create Inbox Directory ---
INBOX_DIR="$DOCS_DIR/inbox"
mkdir -p "$INBOX_DIR/processed"
touch "$INBOX_DIR/.gitkeep"
touch "$INBOX_DIR/processed/.gitkeep"
ok "docs/inbox/ staging directory ready"

# --- Create Living Truth phase directories (Phase 9: nested per-phase layout) ---
# Each phase has its own folder under /docs/. The actual Living Truth files
# (prd.md, design-system.md, architecture.md, nfr.md, etc.) and epic files
# (product/epics/EP-NNN-{slug}.md) are scaffolded on first sprint seal by
# seal_sprint.py (bootstrap_all_living_v1 + on-demand epic creation).
mkdir -p "$DOCS_DIR/product/epics"
mkdir -p "$DOCS_DIR/design"
mkdir -p "$DOCS_DIR/architecture"
mkdir -p "$DOCS_DIR/testing"
touch "$DOCS_DIR/product/epics/.gitkeep"
ok "Living Truth phase folders ready (product/, design/, architecture/, testing/)"

# --- Create Initial Sprint Structure (Phase 9: aligned with nested LT) ---
SPRINT_DIR="$DOCS_DIR/sprint-v1"
mkdir -p "$SPRINT_DIR/product"
mkdir -p "$SPRINT_DIR/product/proposals/epics"
mkdir -p "$SPRINT_DIR/design"
mkdir -p "$SPRINT_DIR/design/proposals"
mkdir -p "$SPRINT_DIR/architecture"
mkdir -p "$SPRINT_DIR/architecture/proposals"
mkdir -p "$SPRINT_DIR/planning"
mkdir -p "$SPRINT_DIR/testing"
mkdir -p "$SPRINT_DIR/testing/proposals"
mkdir -p "$SPRINT_DIR/tempo/in-progress"
mkdir -p "$SPRINT_DIR/tempo/completed"
mkdir -p "$SPRINT_DIR/changes"
touch "$SPRINT_DIR/product/proposals/epics/.gitkeep"
ok "sprint-v1 directory structure ready"

# --- Create / update project config ---
CONFIG_TEMPLATE="$SCRIPT_DIR/prism-config.md"
CONFIG="$PROJECT_ROOT/prism-config.md"

if [ ! -f "$CONFIG" ] && [ -f "$CONFIG_TEMPLATE" ]; then
    cp "$CONFIG_TEMPLATE" "$CONFIG"
    ok "Created project config: $CONFIG"
fi

if [ -f "$CONFIG" ]; then
    if command -v sed >/dev/null 2>&1; then
        PROJECT_NAME_ESCAPED=$(escape_sed_replacement "$(basename "$PROJECT_ROOT")")
        sed -i.bak "s/mode: \"guided\"/mode: \"$MODE\"/" "$CONFIG" 2>/dev/null || true
        sed -i.bak "s/mode: \"freestyle\"/mode: \"$MODE\"/" "$CONFIG" 2>/dev/null || true
        sed -i.bak "s/mode: \"freedom\"/mode: \"$MODE\"/" "$CONFIG" 2>/dev/null || true
        sed -i.bak "s/__PRISM_VERSION__/$PRISM_VERSION/" "$CONFIG" 2>/dev/null || true
        sed -i.bak "s/version: \".*\"/version: \"$PRISM_VERSION\"/" "$CONFIG" 2>/dev/null || true
        sed -i.bak "s/{{PROJECT_NAME}}/$PROJECT_NAME_ESCAPED/" "$CONFIG" 2>/dev/null || true
        rm -f "${CONFIG}.bak"
    fi
fi

# --- Configuration Reminder ---
header "Configuration"

if [ -f "$CONFIG" ]; then
    if grep -q '{{PROJECT_NAME}}' "$CONFIG"; then
        warn "Could not auto-fill the project name. Please edit $CONFIG manually."
        echo ""
        echo "  Edit: $CONFIG"
    else
        ok "Project config ready: $CONFIG"
        info "Project name defaulted to: $(basename "$PROJECT_ROOT")"
    fi
    info "Optional: add a one-line project summary in $CONFIG"
fi

install_guided_precommit_hook "$MODE"

# --- Show Installed Layout ---
header "Installed Layout"
echo "  PRISM home:   $SCRIPT_DIR"
echo "  Framework v:  $PRISM_VERSION"
echo "  Project docs: $DOCS_DIR"
echo "  Project cfg:  $CONFIG"
SHOWN_DESTS=""
for platform in $PLATFORMS; do
    dest=$(adapter_dest "$platform")
    case " $SHOWN_DESTS " in
        *" $dest "*) continue ;;
    esac
    if [ -f "$dest" ]; then
        echo "  Adapter:      $dest"
        SHOWN_DESTS="$SHOWN_DESTS $dest"
    fi
done

# --- Done ---
header "Setup Complete!"
echo ""
info "Next steps:"
echo "  1. Review $CONFIG (project name has been prefilled when possible)"
echo "  2. Install Python dependencies (required by PRISM tools):"
echo "       pip install -r $SCRIPT_DIR/requirements.txt"
echo "     (Skip if pyyaml is already available in your Python environment.)"
echo "  3. Open your AI tool (Claude Code, Copilot, etc.)"
if [ "$MODE" = "freedom" ]; then
    echo "  4. Just start talking — work on any phase in any order"
    echo "     No commands needed. No gates. No approval."
    echo "     AI detects intent and uses the right template."
    echo "     NOTE: Freedom mode is permanent."
else
    echo "  4. Type: start product"
    echo "     OR: drop existing docs into $PROJECT_ROOT/docs/inbox/ and run: import [phase]"
fi
echo ""
info "Mode: $MODE — See $SCRIPT_DIR/README.md for mode details and role-specific instructions."
info "PRISM framework files stay in $SCRIPT_DIR; project artifacts live in $PROJECT_ROOT/docs and $CONFIG."
info "To import existing documents: cp your-doc.md $PROJECT_ROOT/docs/inbox/product.md → import product"
echo ""
