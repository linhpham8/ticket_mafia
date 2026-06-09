"use client";

import { useEffect, useState } from "react";
import { authSession } from "../../auth";
import { OrderHistoryRow, TicketDetail, ticketsApi } from "../services/tickets.api";

type TicketHistoryProps = {
  tokenProvider?: () => string | null;
};

// Sprint: v1 | Feature: FR-009,FR-010,NFR-003 | US: US-009,US-010,US-011 | Task Group: TG 1.5 Purchase History, Ticket Detail, and One-Time Scan
// Contract: design-system-v1.md SCREEN-009/SCREEN-010/SCREEN-011; api-specs-v1.md API-008/API-009 through typed service
export function TicketHistory({ tokenProvider = authSession.getAccessToken }: TicketHistoryProps) {
  const [state, setState] = useState<"loading" | "empty" | "list" | "detail" | "error">("loading");
  const [orders, setOrders] = useState<OrderHistoryRow[]>([]);
  const [detail, setDetail] = useState<TicketDetail | null>(null);

  useEffect(() => {
    const token = tokenProvider();
    if (!token) {
      setState("error");
      return;
    }
    ticketsApi.listOrders(token)
      .then((body) => {
        setOrders(body.data);
        setState(body.data.length === 0 ? "empty" : "list");
      })
      .catch(() => setState("error"));
  }, [tokenProvider]);

  async function openTicket(ticketId: string) {
    const token = tokenProvider();
    if (!token) {
      setState("error");
      return;
    }
    try {
      const body = await ticketsApi.getTicket(token, ticketId);
      setDetail(body.data);
      setState("detail");
    } catch {
      setState("error");
    }
  }

  if (state === "loading") {
    return <main data-testid="ticket-history-loading">Đang tải lịch sử mua vé...</main>;
  }
  if (state === "empty") {
    return <main data-testid="ticket-history-empty">Bạn chưa có đơn mua vé nào.</main>;
  }
  if (state === "error") {
    return <main role="alert">Không thể tải thông tin vé.</main>;
  }
  if (state === "detail" && detail) {
    const entryValid = detail.status === "ISSUED" && detail.qrToken;
    return (
      <main data-testid="ticket-detail" style={pageShell}>
        <section style={ticketHero}>
          <button style={ghostButton} onClick={() => setState("list")}>Lịch sử mua vé</button>
          <div>
            <span style={eyebrow}>E-ticket</span>
            <h1 style={heroTitle}>{detail.match.name}</h1>
            <p style={heroCopy}>Ghế {detail.seatCode} · Trạng thái <span data-testid="ticket-status">{detail.status}</span></p>
          </div>
        </section>

        <section style={detailGrid}>
          <div style={ticketCard}>
            <div style={ticketStub}>
              <span>Ticket Mafia</span>
              <strong>{detail.seatCode}</strong>
            </div>
            <div style={{ padding: 24, display: "grid", gap: 18 }}>
              <div>
                <span style={muted}>Trận đấu</span>
                <h2 style={{ margin: "6px 0 0", fontSize: 24 }}>{detail.match.name}</h2>
              </div>
              <div style={infoGrid}>
                <Info label="Ghế" value={detail.seatCode} />
                <Info label="Trạng thái" value={detail.status} />
              </div>
              {entryValid ? (
                <section data-testid="ticket-qr-card" aria-label="QR vé vào sân" style={qrPanel}>
                  <span style={muted}>QR vé vào sân</span>
                  <strong style={{ overflowWrap: "anywhere" }}>{detail.qrToken}</strong>
                </section>
              ) : (
                <p role="alert" style={alertBox}>Vé này không còn hợp lệ để vào sân.</p>
              )}
            </div>
          </div>

          <aside style={sideCard}>
            <h2 style={{ margin: 0, fontSize: 20 }}>Hướng dẫn vào sân</h2>
            <p style={muted}>Mở QR tại cổng, chỉ quét một lần. Nếu đổi ghế thành công, dùng vé mới nhất trong lịch sử.</p>
            <div style={divider} />
            <span style={pill}>{entryValid ? "Sẵn sàng vào sân" : "Không hợp lệ"}</span>
          </aside>
        </section>
      </main>
    );
  }
  return (
    <main data-testid="ticket-history-list" style={pageShell}>
      <section style={listHeader}>
        <div>
          <span style={eyebrow}>My tickets</span>
          <h1 style={{ margin: "8px 0", fontSize: "clamp(32px, 5vw, 54px)", letterSpacing: 0 }}>Lịch sử mua vé</h1>
          <p style={muted}>Quản lý đơn đã mua, mở QR/e-ticket và kiểm tra trạng thái ghế.</p>
        </div>
      </section>
      <section style={{ maxWidth: 1080, margin: "0 auto", display: "grid", gap: 14 }}>
        {orders.map((order) => (
          <article key={order.orderId} style={orderCard}>
            <div style={orderPoster} aria-hidden="true" />
            <div>
              <strong style={{ display: "block", fontSize: 20 }}>{order.matchName}</strong>
              <p style={muted}>{order.status} · {Number(order.totalAmountVnd).toLocaleString("vi-VN")} VND</p>
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                {order.tickets.map((ticket) => (
                  <button key={ticket.ticketId} style={ticketButton} onClick={() => openTicket(ticket.ticketId)}>
                    {ticket.seatCode} · {ticket.status}
                  </button>
                ))}
              </div>
            </div>
          </article>
        ))}
      </section>
    </main>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div style={infoBox}>
      <span style={muted}>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

const pageShell = {
  minHeight: "100vh",
  padding: "24px clamp(16px, 3vw, 36px) 48px",
  background: "#f6f7fb",
  color: "#0f172a",
  fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
};

const listHeader = {
  maxWidth: 1080,
  minHeight: 240,
  margin: "0 auto 24px",
  display: "flex",
  alignItems: "end",
  padding: 28,
  borderRadius: 8,
  color: "#fff",
  backgroundImage: "linear-gradient(90deg, rgba(15,23,42,.9), rgba(15,23,42,.4)), url('https://images.unsplash.com/photo-1510051640316-cee39563ddab?auto=format&fit=crop&w=1400&q=80')",
  backgroundSize: "cover",
  backgroundPosition: "center",
};

const ticketHero = {
  maxWidth: 1080,
  minHeight: 260,
  margin: "0 auto 22px",
  padding: 28,
  borderRadius: 8,
  display: "grid",
  alignContent: "space-between",
  color: "#fff",
  backgroundImage: "linear-gradient(90deg, rgba(2,6,23,.9), rgba(2,6,23,.35)), url('https://images.unsplash.com/photo-1526232761682-d26e03ac148e?auto=format&fit=crop&w=1400&q=80')",
  backgroundSize: "cover",
  backgroundPosition: "center",
};

const detailGrid = { maxWidth: 1080, margin: "0 auto", display: "grid", gridTemplateColumns: "minmax(0, 1fr) 300px", gap: 18, alignItems: "start" };
const ticketCard = { display: "grid", gridTemplateColumns: "130px minmax(0, 1fr)", overflow: "hidden", border: "1px solid #e2e8f0", borderRadius: 8, background: "#fff", boxShadow: "0 14px 34px rgba(15,23,42,.07)" };
const ticketStub = { display: "grid", alignContent: "space-between", padding: 18, background: "#0f172a", color: "#fff", textTransform: "uppercase" as const, fontWeight: 800 };
const infoGrid = { display: "grid", gridTemplateColumns: "repeat(2, minmax(0, 1fr))", gap: 12 };
const infoBox = { display: "grid", gap: 4, padding: 14, border: "1px solid #e2e8f0", borderRadius: 8, background: "#f8fafc" };
const qrPanel = { display: "grid", gap: 12, placeItems: "center", minHeight: 220, padding: 20, border: "1px dashed #94a3b8", borderRadius: 8, background: "#f8fafc" };
const sideCard = { position: "sticky" as const, top: 16, display: "grid", gap: 14, padding: 20, border: "1px solid #e2e8f0", borderRadius: 8, background: "#fff" };
const orderCard = { display: "grid", gridTemplateColumns: "120px minmax(0, 1fr)", gap: 16, alignItems: "center", padding: 14, border: "1px solid #e2e8f0", borderRadius: 8, background: "#fff", boxShadow: "0 14px 34px rgba(15,23,42,.07)" };
const orderPoster = { height: 92, borderRadius: 8, backgroundImage: "linear-gradient(135deg, rgba(5,150,105,.9), rgba(14,165,233,.68)), url('https://images.unsplash.com/photo-1577223625816-7546f13df25d?auto=format&fit=crop&w=500&q=80')", backgroundSize: "cover", backgroundPosition: "center" };
const ticketButton = { minHeight: 38, border: "1px solid #cbd5e1", borderRadius: 999, padding: "0 13px", background: "#fff", color: "#0f172a", fontWeight: 700, cursor: "pointer" };
const ghostButton = { width: "fit-content", minHeight: 38, border: "1px solid rgba(255,255,255,.48)", borderRadius: 6, padding: "0 14px", background: "rgba(255,255,255,.12)", color: "#fff", fontWeight: 800, cursor: "pointer" };
const eyebrow = { textTransform: "uppercase" as const, fontSize: 12, fontWeight: 900, letterSpacing: 0, color: "#bae6fd" };
const heroTitle = { margin: "8px 0", fontSize: "clamp(32px, 5vw, 54px)", lineHeight: 1, letterSpacing: 0 };
const heroCopy = { margin: 0, color: "rgba(255,255,255,.84)" };
const muted = { color: "#64748b", fontSize: 14 };
const divider = { height: 1, background: "#e2e8f0" };
const pill = { display: "inline-flex", width: "fit-content", borderRadius: 999, padding: "6px 10px", background: "#ecfdf5", color: "#047857", fontSize: 12, fontWeight: 800 };
const alertBox = { padding: 14, borderRadius: 8, border: "1px solid #f59e0b", background: "#fffbeb", color: "#92400e" };
