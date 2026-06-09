import Link from "next/link";
import { getInventoryConfig } from "../../../../../matches/adminMatches.service";

export default async function AdminInventoryPage({
  params,
  searchParams,
}: {
  params: Promise<{ matchId: string }>;
  searchParams?: Promise<{ state?: string; tab?: string }>;
}) {
  const { matchId } = await params;
  const view = await searchParams;
  const state = view?.state;
  const tab = view?.tab ?? "seats";
  const config = await getInventoryConfig();
  if (state === "loading") {
    return (
      <main style={page}>
        <InventoryHeader matchId={matchId} />
        <section data-testid="admin-inventory-loading" style={{ marginTop: 32 }}>
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
        <InventoryHeader matchId={matchId} />
        <section data-testid="admin-inventory-error" style={emptyState}>
          Không thể tải cấu hình vé.
        </section>
      </main>
    );
  }
  if (state === "empty") {
    return (
      <main style={page}>
        <InventoryHeader matchId={matchId} />
        <section data-testid="admin-inventory-empty" style={emptyState}>
          Chưa cấu hình ghế cho trận này.
        </section>
      </main>
    );
  }

  return (
    <main style={page}>
      <InventoryHeader matchId={matchId} />
      <section style={metricGrid} aria-label="Tổng quan cấu hình vé">
        <Metric label="Khu đang có giá" value={String(config.prices.length)} />
        <Metric label="QR khả dụng" value={String(config.qrConfigs.length)} />
        <Metric label="Mặc định" value={config.qrConfigs.find((qr) => qr.isDefault)?.name ?? "-"} />
      </section>

      <nav aria-label="Inventory tabs" style={tabs}>
        <Link style={tabStyle(tab === "seats")} href={`/admin/matches/${matchId}/inventory?tab=seats`}>
          Ghế
        </Link>
        <Link style={tabStyle(tab === "prices")} href={`/admin/matches/${matchId}/inventory?tab=prices`}>
          Giá
        </Link>
        <Link style={tabStyle(tab === "qr")} href={`/admin/matches/${matchId}/inventory?tab=qr`}>
          QR thanh toán
        </Link>
      </nav>

      <section data-testid="admin-inventory-config" style={configCard}>
        <div hidden={tab !== "seats"} style={panelGrid}>
          <h2 style={sectionTitle}>Ghế</h2>
          <p style={muted}>{config.seatSummary}</p>
          <div style={fieldGrid}>
          <label style={field}>
            Khu
            <input name="sectionCode" defaultValue="A" style={input} />
          </label>
          <label style={field}>
            Tầng
            <input name="floorNo" defaultValue="1" style={input} />
          </label>
          <label style={field}>
            Số ghế
            <input name="seatCount" defaultValue="120" style={input} />
          </label>
          </div>
          <button style={button}>Tạo ghế</button>
        </div>

        <div hidden={tab !== "prices"} style={panelGrid}>
          <h2 style={sectionTitle}>Giá</h2>
          <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th style={cellHeader}>Khu</th>
                <th style={cellHeader}>Tầng</th>
                <th style={cellHeader}>VIP</th>
                <th style={cellHeader}>Giá</th>
              </tr>
            </thead>
            <tbody>
              {config.prices.map((price) => (
                <tr key={`${price.sectionCode}-${price.floorNo}-${price.isVip}`}>
                  <td style={cell}>{price.sectionCode}</td>
                  <td style={cell}>{price.floorNo}</td>
                  <td style={cell}>{price.isVip ? "Có" : "Không"}</td>
                  <td style={cell}>{price.priceVnd.toLocaleString("vi-VN")} VND</td>
                </tr>
              ))}
            </tbody>
          </table>
          </div>
          <label style={field}>
            Giá mới
            <input name="priceVnd" defaultValue="250000" style={input} />
          </label>
          <button style={button}>Cập nhật giá</button>
        </div>

        <div hidden={tab !== "qr"} style={panelGrid}>
          <h2 style={sectionTitle}>QR thanh toán</h2>
          <div style={qrGrid}>
            {config.qrConfigs.map((qr) => (
              <article key={qr.qrAssetRef} style={qrCard}>
                <strong>{qr.name}</strong>
                <span style={muted}>{qr.qrAssetRef}</span>
                <span style={qr.isDefault ? activePill : neutralPill}>{qr.isDefault ? "Mặc định" : "Dự phòng"}</span>
              </article>
            ))}
          </div>
          <label style={field}>
            Tên QR
            <input name="qrName" defaultValue="QR MB Bank" style={input} />
          </label>
          <label style={field}>
            Asset ref
            <input name="qrAssetRef" defaultValue="asset://payment/default-mb" style={input} />
          </label>
          <button style={button}>Chọn QR mặc định</button>
        </div>
      </section>
    </main>
  );
}

function InventoryHeader({ matchId }: { matchId: string }) {
  return (
    <header style={hero}>
      <Link style={backLink} href="/admin/matches">← Quản lý trận đấu</Link>
      <span style={eyebrow}>Inventory setup</span>
      <h1 style={{ margin: "8px 0", fontSize: 34, letterSpacing: 0 }}>Cấu hình ghế, giá và QR</h1>
      <p style={{ margin: 0, color: "#cbd5e1" }}>Match: {matchId}</p>
    </header>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <article style={metricCard}>
      <span style={muted}>{label}</span>
      <strong style={{ fontSize: 24 }}>{value}</strong>
    </article>
  );
}

const sectionTitle = {
  fontSize: 20,
  margin: 0,
};

const button = {
  marginTop: 12,
  minHeight: 40,
  padding: "0 14px",
  border: "1px solid #111827",
  borderRadius: 6,
  background: "#111827",
  color: "#fff",
  fontWeight: 800,
};

const cellHeader = {
  borderBottom: "1px solid #e2e8f0",
  color: "#64748b",
  fontSize: 13,
  padding: "12px 14px",
  textAlign: "left" as const,
};

const cell = {
  borderBottom: "1px solid #f1f5f9",
  padding: "14px",
};

const page = {
  minHeight: "100vh",
  fontFamily: "Inter, Arial, sans-serif",
  padding: 24,
  background: "#f6f7fb",
  color: "#0f172a",
};

const input = {
  display: "block",
  marginTop: 6,
  marginBottom: 12,
  padding: "9px 10px",
  border: "1px solid #cbd5e1",
  borderRadius: 6,
};

const skeleton = {
  height: 54,
  maxWidth: 1180,
  background: "#e2e8f0",
  marginBottom: 10,
  borderRadius: 8,
};

function tabStyle(active: boolean) {
  return {
    border: "1px solid #cbd5e1",
    borderRadius: 999,
    background: active ? "#111827" : "#fff",
    color: active ? "#fff" : "#111827",
    padding: "9px 14px",
    textDecoration: "none",
    fontWeight: 800,
  };
}

const hero = { maxWidth: 1180, margin: "0 auto", padding: 28, borderRadius: 8, background: "linear-gradient(135deg, #0f172a, #3b0764)", color: "#fff" };
const backLink = { display: "inline-flex", color: "#fff", textDecoration: "none", marginBottom: 18, fontWeight: 800 };
const eyebrow = { textTransform: "uppercase" as const, fontSize: 12, fontWeight: 900, color: "#d8b4fe" };
const metricGrid = { maxWidth: 1180, margin: "18px auto 0", display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: 12 };
const metricCard = { display: "grid", gap: 6, padding: 18, border: "1px solid #e2e8f0", borderRadius: 8, background: "#fff" };
const tabs = { maxWidth: 1180, margin: "18px auto 0", display: "flex", gap: 8, flexWrap: "wrap" as const };
const configCard = { maxWidth: 1180, margin: "18px auto 0", padding: 22, border: "1px solid #e2e8f0", borderRadius: 8, background: "#fff", boxShadow: "0 14px 34px rgba(15,23,42,.07)" };
const panelGrid = { display: "grid", gap: 14 };
const fieldGrid = { display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: 12 };
const field = { display: "grid", gap: 2, color: "#334155", fontSize: 13, fontWeight: 700 };
const qrGrid = { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 12 };
const qrCard = { display: "grid", gap: 8, padding: 16, border: "1px solid #e2e8f0", borderRadius: 8, background: "#f8fafc" };
const activePill = { display: "inline-flex", width: "fit-content", borderRadius: 999, padding: "5px 10px", background: "#ecfdf5", color: "#047857", fontSize: 12, fontWeight: 800 };
const neutralPill = { display: "inline-flex", width: "fit-content", borderRadius: 999, padding: "5px 10px", background: "#f1f5f9", color: "#475569", fontSize: 12, fontWeight: 800 };
const emptyState = { maxWidth: 1180, margin: "18px auto 0", padding: 24, border: "1px solid #e2e8f0", borderRadius: 8, background: "#fff" };
const muted = { margin: "4px 0 0", color: "#64748b", fontSize: 13 };
