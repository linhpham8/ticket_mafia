import Link from "next/link";
import { listAdminMatches, type MatchStatus } from "../../../matches/adminMatches.service";

const statusLabel: Record<MatchStatus, string> = {
  OPEN_FOR_SALE: "Đang bán",
  SOLD_OUT: "Hết vé",
  CANCELLED: "Đã hủy",
  CLOSED: "Đã đóng",
};

export default async function AdminMatchesPage({
  searchParams,
}: {
  searchParams?: Promise<{ state?: string }>;
}) {
  const state = (await searchParams)?.state;
  const matches = await listAdminMatches();
  if (state === "loading") {
    return (
      <main style={page}>
        <AdminHero title="Quản lý trận đấu" subtitle="Đang đồng bộ lịch bán vé và tồn kho ghế." />
        <section data-testid="admin-matches-loading" style={{ marginTop: 32 }}>
          <div style={skeleton} />
          <div style={skeleton} />
          <div style={skeleton} />
        </section>
      </main>
    );
  }
  if (state === "error") {
    return (
      <main style={page}>
        <AdminHero title="Quản lý trận đấu" subtitle="Không lấy được dữ liệu vận hành." />
        <section data-testid="admin-matches-error" style={emptyState}>
          Không thể tải danh sách trận đấu.
        </section>
      </main>
    );
  }
  const visibleMatches = state === "empty" ? [] : matches;

  return (
    <main style={page}>
      <AdminHero title="Quản lý trận đấu" subtitle="Tạo trận, kiểm soát trạng thái bán và vào cấu hình vé." action="Tạo trận đấu" />

      <section style={metricGrid} aria-label="Tổng quan trận đấu">
        <Metric label="Đang bán" value={String(visibleMatches.filter((match) => match.status === "OPEN_FOR_SALE").length)} />
        <Metric label="Tổng trận" value={String(visibleMatches.length)} />
        <Metric label="Cần cấu hình" value="2" />
      </section>

      {visibleMatches.length === 0 ? (
        <section data-testid="admin-matches-empty" style={emptyState}>
          Chưa có trận đấu nào.
        </section>
      ) : (
        <section data-testid="admin-matches-table" style={tableCard}>
          <div style={tableToolbar}>
            <strong>Lịch trận</strong>
            <label style={toolbarControl}>
              Trạng thái
              <select aria-label="Lọc trạng thái" style={control}>
                <option>Tất cả</option>
                <option>Đang bán</option>
                <option>Đã đóng</option>
              </select>
            </label>
          </div>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th style={cellHeader}>Trận đấu</th>
                <th style={cellHeader}>Thời gian</th>
                <th style={cellHeader}>Trạng thái</th>
                <th style={cellHeader}>Thao tác</th>
              </tr>
            </thead>
            <tbody>
              {visibleMatches.map((match) => (
                <tr key={match.id}>
                  <td style={cell}>
                    <strong>{match.name}</strong>
                    <p style={muted}>Match ID: {match.id}</p>
                  </td>
                  <td style={cell}>{new Intl.DateTimeFormat("vi-VN", { dateStyle: "medium", timeStyle: "short" }).format(new Date(match.startsAt))}</td>
                  <td style={cell}>
                    <span style={statusChip(match.status)}>
                      {statusLabel[match.status]}
                    </span>
                  </td>
                  <td style={cell}>
                    <Link style={rowAction} href={`/admin/matches/${match.id}/inventory`}>Cấu hình vé</Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}
    </main>
  );
}

function AdminHero({ title, subtitle, action }: { title: string; subtitle: string; action?: string }) {
  return (
    <header style={hero}>
      <div>
        <span style={eyebrow}>Admin console</span>
        <h1 style={{ margin: "8px 0", fontSize: 34, letterSpacing: 0 }}>{title}</h1>
        <p style={{ margin: 0, color: "#cbd5e1" }}>{subtitle}</p>
      </div>
      {action ? <button style={primaryAction}>{action}</button> : null}
    </header>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <article style={metricCard}>
      <span style={muted}>{label}</span>
      <strong style={{ fontSize: 28 }}>{value}</strong>
    </article>
  );
}

const cellHeader = {
  borderBottom: "1px solid #e2e8f0",
  color: "#64748b",
  fontSize: 13,
  padding: "14px 16px",
  textAlign: "left" as const,
};

const cell = {
  borderBottom: "1px solid #f1f5f9",
  padding: "16px",
  verticalAlign: "top" as const,
};

const page = {
  minHeight: "100vh",
  fontFamily: "Inter, Arial, sans-serif",
  padding: 24,
  background: "#f6f7fb",
  color: "#0f172a",
};

const hero = {
  display: "flex",
  justifyContent: "space-between",
  gap: 18,
  alignItems: "center",
  maxWidth: 1180,
  margin: "0 auto",
  padding: 28,
  borderRadius: 8,
  background: "linear-gradient(135deg, #0f172a, #14532d)",
  color: "#fff",
};

const skeleton = {
  height: 54,
  maxWidth: 1180,
  background: "#e2e8f0",
  marginBottom: 10,
  borderRadius: 8,
};

const metricGrid = { maxWidth: 1180, margin: "18px auto 0", display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: 12 };
const metricCard = { display: "grid", gap: 6, padding: 18, border: "1px solid #e2e8f0", borderRadius: 8, background: "#fff" };
const tableCard = { maxWidth: 1180, margin: "18px auto 0", overflowX: "auto" as const, border: "1px solid #e2e8f0", borderRadius: 8, background: "#fff", boxShadow: "0 14px 34px rgba(15,23,42,.07)" };
const tableToolbar = { display: "flex", justifyContent: "space-between", gap: 14, alignItems: "center", padding: 16, borderBottom: "1px solid #e2e8f0" };
const toolbarControl = { display: "flex", gap: 8, alignItems: "center", color: "#64748b", fontSize: 13 };
const control = { minHeight: 36, border: "1px solid #cbd5e1", borderRadius: 6, padding: "0 10px", background: "#fff" };
const emptyState = { maxWidth: 1180, margin: "18px auto 0", padding: 24, border: "1px solid #e2e8f0", borderRadius: 8, background: "#fff" };
const primaryAction = { minHeight: 42, border: "1px solid #fff", borderRadius: 6, padding: "0 16px", background: "#fff", color: "#0f172a", fontWeight: 800 };
const rowAction = { display: "inline-flex", minHeight: 34, alignItems: "center", borderRadius: 6, padding: "0 12px", background: "#0f172a", color: "#fff", textDecoration: "none", fontWeight: 700 };
const eyebrow = { textTransform: "uppercase" as const, fontSize: 12, fontWeight: 900, color: "#86efac" };
const muted = { margin: "4px 0 0", color: "#64748b", fontSize: 13 };

function statusChip(status: MatchStatus) {
  const palette = status === "OPEN_FOR_SALE"
    ? { border: "#bbf7d0", background: "#ecfdf5", color: "#047857" }
    : status === "CLOSED"
      ? { border: "#cbd5e1", background: "#f8fafc", color: "#475569" }
      : { border: "#fed7aa", background: "#fff7ed", color: "#c2410c" };
  return { border: `1px solid ${palette.border}`, background: palette.background, color: palette.color, borderRadius: 999, padding: "5px 10px", fontSize: 13, fontWeight: 800 };
}
