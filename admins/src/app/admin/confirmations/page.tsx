import { listPendingConfirmations } from "./confirmations.service";

// Sprint: v1 | Feature: FR-008,FR-012 | US: US-008,US-012 | Task Group: TG 1.4 Admin Payment Confirmation and Audit; TG 1.6 Seat Exchange and Local Demo Runtime
// Contract: design-system-v1.md SCREEN-008 exchange confirm state; api-specs-v1.md API-007/API-015
export default async function AdminConfirmationsPage({
  searchParams,
}: {
  searchParams?: Promise<{ state?: string }>;
}) {
  const state = (await searchParams)?.state;
  const pending = await listPendingConfirmations();
  if (state === "loading") {
    return (
      <main style={page}>
        <AdminHero title="Xác nhận thanh toán" subtitle="Đang tải các giao dịch chờ admin duyệt." />
        <section data-testid="admin-confirm-loading" style={{ marginTop: 32 }}>
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
        <AdminHero title="Xác nhận thanh toán" subtitle="Không lấy được hàng chờ xác nhận." />
        <section data-testid="admin-confirm-error" style={emptyState}>
          Không thể tải giao dịch chờ xác nhận.
        </section>
      </main>
    );
  }

  const rows = state === "empty" ? [] : pending;

  return (
    <main style={page}>
      <AdminHero
        title="Xác nhận thanh toán"
        subtitle="Kiểm tra giao dịch đã chuyển khoản, xác nhận để phát hành vé hoặc từ chối để mở lại ghế."
      />

      <section style={metricGrid} aria-label="Tổng quan xác nhận">
        <Metric label="Đang chờ" value={String(rows.length)} />
        <Metric label="Đổi ghế" value={String(rows.filter((order) => order.type === "EXCHANGE").length)} />
        <Metric label="Tổng giá trị" value={formatCompactVnd(rows.reduce((sum, order) => sum + order.totalAmountVnd, 0))} />
      </section>

      <section style={tableCard}>
        <div style={tableToolbar}>
          <strong>Hàng chờ xác nhận</strong>
        <label style={{ display: "grid", gap: 6, color: "#374151", fontSize: 13 }}>
          Lọc trạng thái
          <select aria-label="Lọc trạng thái" style={control}>
            <option>Đang chờ</option>
            <option>Sắp hết hạn</option>
          </select>
        </label>
        </div>

      {rows.length === 0 ? (
        <section data-testid="admin-confirm-empty" style={emptyStateInner}>
          Không có giao dịch chờ xác nhận.
        </section>
      ) : (
        <div data-testid="admin-confirm-table" style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th style={cellHeader}>Mã đơn</th>
                <th style={cellHeader}>Khách hàng</th>
                <th style={cellHeader}>Loại</th>
                <th style={cellHeader}>Ghế</th>
                <th style={cellHeader}>Tổng tiền</th>
                <th style={cellHeader}>Trạng thái</th>
                <th style={cellHeader}>Thao tác</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((order) => (
                <tr key={order.orderId}>
                  <td style={cell}>
                    <strong>{order.orderId}</strong>
                    <p style={muted}>Hết hạn {new Intl.DateTimeFormat("vi-VN", { timeStyle: "short" }).format(new Date(order.adminConfirmExpiresAt))}</p>
                  </td>
                  <td style={cell}>{order.userIdentifier}</td>
                  <td style={cell}><span style={typeChip(order.type)}>{order.type === "EXCHANGE" ? "Đổi ghế" : "Mua vé"}</span></td>
                  <td style={cell}>{order.seatCount}</td>
                  <td style={cell}>{formatVnd(order.totalAmountVnd)}</td>
                  <td style={cell}>
                    <span style={chip}>Đang chờ</span>
                  </td>
                  <td style={{ ...cell, minWidth: 260 }}>
                    <button style={primaryAction}>
                      {order.type === "EXCHANGE" ? "Xác nhận đổi ghế" : "Xác nhận đã nhận tiền"}
                    </button>
                    <button style={secondaryAction}>Từ chối</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      </section>
    </main>
  );
}

function formatVnd(value: number) {
  return new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND" }).format(value);
}

function formatCompactVnd(value: number) {
  return new Intl.NumberFormat("vi-VN", { notation: "compact", maximumFractionDigits: 1 }).format(value) + " VND";
}

function AdminHero({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <header style={hero}>
      <div>
        <span style={eyebrow}>Admin console</span>
        <h1 style={{ margin: "8px 0", fontSize: 34, letterSpacing: 0 }}>{title}</h1>
        <p style={{ margin: 0, color: "#cbd5e1" }}>{subtitle}</p>
      </div>
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

const skeleton = {
  height: 54,
  maxWidth: 1180,
  background: "#e2e8f0",
  marginBottom: 10,
  borderRadius: 8,
};

const control = {
  minWidth: 160,
  padding: "9px 10px",
  border: "1px solid #cbd5e1",
  borderRadius: 6,
  background: "#fff",
};

const chip = {
  border: "1px solid #fed7aa",
  background: "#fff7ed",
  color: "#c2410c",
  borderRadius: 999,
  padding: "5px 10px",
  fontSize: 13,
  fontWeight: 800,
};

const primaryAction = {
  minHeight: 36,
  padding: "0 12px",
  border: "1px solid #0f766e",
  borderRadius: 6,
  background: "#0f766e",
  color: "#fff",
  marginRight: 8,
  fontWeight: 800,
};

const secondaryAction = {
  minHeight: 36,
  padding: "0 12px",
  border: "1px solid #dc2626",
  borderRadius: 6,
  background: "#fff",
  color: "#dc2626",
  fontWeight: 800,
};

const hero = { maxWidth: 1180, margin: "0 auto", padding: 28, borderRadius: 8, background: "linear-gradient(135deg, #0f172a, #164e63)", color: "#fff" };
const metricGrid = { maxWidth: 1180, margin: "18px auto 0", display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: 12 };
const metricCard = { display: "grid", gap: 6, padding: 18, border: "1px solid #e2e8f0", borderRadius: 8, background: "#fff" };
const tableCard = { maxWidth: 1180, margin: "18px auto 0", border: "1px solid #e2e8f0", borderRadius: 8, background: "#fff", boxShadow: "0 14px 34px rgba(15,23,42,.07)", overflow: "hidden" };
const tableToolbar = { display: "flex", justifyContent: "space-between", gap: 14, alignItems: "center", padding: 16, borderBottom: "1px solid #e2e8f0" };
const emptyState = { maxWidth: 1180, margin: "18px auto 0", padding: 24, border: "1px solid #e2e8f0", borderRadius: 8, background: "#fff" };
const emptyStateInner = { padding: 24 };
const eyebrow = { textTransform: "uppercase" as const, fontSize: 12, fontWeight: 900, color: "#67e8f9" };
const muted = { margin: "4px 0 0", color: "#64748b", fontSize: 13 };

function typeChip(type: "PURCHASE" | "EXCHANGE") {
  return {
    border: `1px solid ${type === "EXCHANGE" ? "#bfdbfe" : "#bbf7d0"}`,
    background: type === "EXCHANGE" ? "#eff6ff" : "#ecfdf5",
    color: type === "EXCHANGE" ? "#1d4ed8" : "#047857",
    borderRadius: 999,
    padding: "5px 10px",
    fontSize: 13,
    fontWeight: 800,
  };
}
