"use client";

import { FlowState, MatchCheckoutModel } from "./useMatchCheckoutFlow";

type MatchCheckoutFlowViewProps = {
  model: MatchCheckoutModel;
  visibleState?: FlowState;
};

export function MatchCheckoutFlowView({ model, visibleState = model.state }: MatchCheckoutFlowViewProps) {
  return (
    <main data-testid={visibleState} style={pageShell}>
      <header style={topBar}>
        <div style={brandLockup}>
          <span style={brandMark}>TM</span>
          <div>
            <strong style={{ display: "block", fontSize: 15 }}>Ticket Mafia</strong>
            <span style={{ color: "#64748b", fontSize: 13 }}>Football tickets</span>
          </div>
        </div>
        {model.selectedMatch ? <button style={ghostButton} onClick={model.showMatchList}>Danh sách trận</button> : null}
      </header>
      <MatchListPanel model={model} visibleState={visibleState} />
      <SeatMapPanel model={model} visibleState={visibleState} />
      <CheckoutPanel model={model} visibleState={visibleState} />
      <PendingPanel model={model} visibleState={visibleState} />
    </main>
  );
}

function MatchListPanel({ model, visibleState }: MatchCheckoutFlowViewProps) {
  if (visibleState === "matches-loading") {
    return <StateCard>Đang tải danh sách trận đấu...</StateCard>;
  }
  if (visibleState === "matches-empty") {
    return <StateCard>Chưa có trận đấu đang bán vé.</StateCard>;
  }
  if (visibleState === "matches-error") {
    return <StateCard role="alert">Không thể tải danh sách trận đấu. Vui lòng thử lại.</StateCard>;
  }
  if (visibleState !== "matches-list") {
    return null;
  }
  const matchesByDate = model.matches.reduce<Record<string, typeof model.matches>>((acc, match) => {
    const key = match.startsAt
      ? new Intl.DateTimeFormat("vi-VN", { weekday: "long", day: "2-digit", month: "2-digit", year: "numeric" }).format(new Date(match.startsAt))
      : "Chưa có lịch thi đấu";
    acc[key] = [...(acc[key] ?? []), match];
    return acc;
  }, {});
  return (
    <section aria-label="Danh sách trận đấu" style={{ display: "grid", gap: 24 }}>
      <div style={hero}>
        <div style={heroOverlay}>
          <div style={breadcrumb}>Trang chủ / Vé thể thao / Vé bóng đá</div>
          <h1 style={heroTitle}>Vé bóng đá đang mở bán</h1>
          <p style={heroCopy}>Chọn trận, khu ngồi và hoàn tất giữ vé trong vài phút. Ghế thật, giá rõ ràng, trạng thái cập nhật theo từng đơn.</p>
          <div style={searchPanel}>
            <label style={searchField}>
              <span>Tìm trận đấu</span>
              <input aria-label="Tìm trận đấu" placeholder="Nhập đội bóng, sân, giải đấu" style={searchInput} />
            </label>
            <label style={searchField}>
              <span>Thời gian</span>
              <select aria-label="Thời gian" style={searchInput} defaultValue="all">
                <option value="all">Tất cả ngày</option>
                <option value="weekend">Cuối tuần</option>
                <option value="month">Tháng này</option>
              </select>
            </label>
            <button style={primaryButton}>Tìm vé</button>
          </div>
        </div>
      </div>

      <div style={contentGrid}>
        <aside style={filterPanel} aria-label="Bộ lọc vé">
          <strong style={{ fontSize: 16 }}>Bộ lọc</strong>
          <FilterCheck label="Đang bán" checked />
          <FilterCheck label="Khu VIP" />
          <FilterCheck label="Giá tốt nhất" />
          <div style={divider} />
          <span style={muted}>Sắp xếp</span>
          <select aria-label="Sắp xếp" style={select}>
            <option>Ngày gần nhất</option>
            <option>Giá thấp nhất</option>
          </select>
        </aside>

        <div style={{ display: "grid", gap: 20 }}>
          {Object.entries(matchesByDate).map(([date, matches]) => (
            <section key={date} style={{ display: "grid", gap: 12 }}>
              <div style={dateHeader}>
                <h2 style={{ margin: 0, fontSize: 18 }}>{date}</h2>
                <span style={pill}>{matches.length} trận</span>
              </div>
              {matches.map((match) => (
                <article key={match.id} style={matchCard}>
                  <div style={matchPoster} aria-hidden="true">
                    <span style={posterLeague}>Football</span>
                  </div>
                  <div style={{ minWidth: 0 }}>
                    <strong style={matchName}>{match.name}</strong>
                    <p style={matchMeta}>{match.startsAt ? new Date(match.startsAt).toLocaleString("vi-VN") : "Chưa có lịch thi đấu"}</p>
                    <div style={tagRow}>
                      <span style={softTag}>E-ticket</span>
                      <span style={softTag}>Chọn ghế</span>
                      <span style={softTag}>QR chuyển khoản</span>
                    </div>
                  </div>
                  <div style={priceBlock}>
                    <span style={muted}>Từ</span>
                    <strong style={{ fontSize: 20 }}>120.000 VND</strong>
                    <button style={primaryButton} onClick={() => model.openSeats(match)}>Chọn ghế</button>
                  </div>
                </article>
              ))}
            </section>
          ))}
        </div>
      </div>
    </section>
  );
}

function SeatMapPanel({ model, visibleState }: MatchCheckoutFlowViewProps) {
  if (visibleState === "seat-map-loading") {
    return <StateCard>Đang tải sơ đồ ghế...</StateCard>;
  }
  if (visibleState === "seat-map-empty") {
    return <StateCard>Khu này chưa có ghế khả dụng.</StateCard>;
  }
  if (visibleState === "seat-map-error") {
    return <StateCard role="alert">Không thể tải sơ đồ ghế. Vui lòng thử lại.</StateCard>;
  }
  if (visibleState !== "seat-map-grid") {
    return null;
  }
  const minPrice = Math.min(...model.seats.map((seat) => Number(seat.priceVnd)));
  return (
    <section aria-label="Sơ đồ ghế" style={{ display: "grid", gap: 22 }}>
      <div style={detailHero}>
        <div>
          <div style={breadcrumb}>Vé bóng đá / Chi tiết trận</div>
          <h1 style={detailTitle}>{model.selectedMatch?.name}</h1>
          <p style={heroCopy}>
            {model.selectedMatch?.startsAt ? new Date(model.selectedMatch.startsAt).toLocaleString("vi-VN") : "Chưa có lịch thi đấu"}
          </p>
        </div>
        <div style={eventStatCard}>
          <span style={muted}>Giá từ</span>
          <strong style={{ fontSize: 24 }}>{Number(minPrice).toLocaleString("vi-VN")} VND</strong>
          <span style={softTag}>{model.seats.filter((seat) => seat.status === "AVAILABLE").length} ghế khả dụng</span>
        </div>
      </div>

      <div style={ticketLayout}>
        <div style={{ display: "grid", gap: 16 }}>
          <section style={mapCard}>
            <div style={sectionHeader}>
              <div>
                <h2 style={{ margin: 0, fontSize: 20 }}>Chọn khu vực và ghế</h2>
                <p style={{ ...muted, margin: "6px 0 0" }}>Tối đa 5 ghế cho mỗi lần mua. Ghế đã giữ sẽ không thể chọn.</p>
              </div>
              <div style={legend}>
                <span><i style={{ ...legendDot, background: "#0f766e" }} /> Đã chọn</span>
                <span><i style={{ ...legendDot, background: "#fff", border: "1px solid #94a3b8" }} /> Trống</span>
                <span><i style={{ ...legendDot, background: "#f59e0b" }} /> Đã giữ</span>
              </div>
            </div>
            <div style={seatGrid}>
              {model.seats.map((seat) => {
                const selected = model.selectedSeatIds.includes(seat.id);
                return (
                  <button
                    key={seat.id}
                    data-testid={`seat-${seat.seatCode}`}
                    onClick={() => model.toggleSeat(seat)}
                    style={{
                      ...seatButton,
                      borderColor: selected ? "#0f766e" : "#cbd5e1",
                      background: selected ? "#0f766e" : seat.status === "AVAILABLE" ? "#ffffff" : "#f59e0b",
                      color: selected ? "#ffffff" : "#0f172a",
                      opacity: seat.status === "AVAILABLE" ? 1 : 0.82
                    }}
                  >
                    <strong>{seat.seatCode}</strong>
                    <span>{seat.sectionCode}{seat.isVip ? " VIP" : ""} · T{seat.floorNo}</span>
                    <span>{Number(seat.priceVnd).toLocaleString("vi-VN")} VND</span>
                  </button>
                );
              })}
            </div>
          </section>
          {model.message ? <p role="alert" style={alertBox}>{model.message}</p> : null}
        </div>

        <aside style={summaryCard} aria-label="Tóm tắt đơn vé">
          <h2 style={{ margin: 0, fontSize: 20 }}>Tóm tắt vé</h2>
          <p style={muted}>{model.selectedSeatIds.length}/5 ghế đã chọn</p>
          <div style={divider} />
          {model.selectedSeats.length === 0 ? (
            <p style={muted}>Chọn ghế trên sơ đồ để xem tổng tiền.</p>
          ) : (
            <div style={{ display: "grid", gap: 10 }}>
              {model.selectedSeats.map((seat) => (
                <div key={seat.id} style={summaryRow}>
                  <span>{seat.seatCode}</span>
                  <strong>{Number(seat.priceVnd).toLocaleString("vi-VN")} VND</strong>
                </div>
              ))}
            </div>
          )}
          <div style={divider} />
          <div style={summaryRow}>
            <span>Tổng tạm tính</span>
            <strong>{model.selectedSeats.reduce((sum, seat) => sum + Number(seat.priceVnd), 0).toLocaleString("vi-VN")} VND</strong>
          </div>
          <button style={{ ...primaryButton, width: "100%", opacity: model.selectedSeatIds.length === 0 ? 0.55 : 1 }} disabled={model.selectedSeatIds.length === 0} onClick={model.startCheckout}>Thanh toán</button>
        </aside>
      </div>
    </section>
  );
}

function CheckoutPanel({ model, visibleState }: MatchCheckoutFlowViewProps) {
  if (visibleState === "checkout-empty") {
    return <StateCard>Không có ghế trong đơn thanh toán.</StateCard>;
  }
  if (visibleState === "checkout-loading") {
    return <StateCard>Đang tạo đơn thanh toán...</StateCard>;
  }
  if (visibleState === "checkout-expired-error") {
    return (
      <section role="alert" style={mapCard}>
        <p>Đã hết thời gian giữ ghế. Vui lòng tạo đơn mới.</p>
        <button style={primaryButton} onClick={() => model.selectedMatch && model.openSeats(model.selectedMatch)}>Chọn lại ghế</button>
      </section>
    );
  }
  if (visibleState !== "checkout-qr" || !model.checkout) {
    return null;
  }
  return (
    <section aria-label="Thanh toán QR" style={ticketLayout}>
      <div style={mapCard}>
        <div style={sectionHeader}>
          <div>
            <h1 style={{ margin: 0, fontSize: 28 }}>Thanh toán chuyển khoản</h1>
            <p style={{ ...muted, margin: "8px 0 0" }}>Ghế được giữ đến {new Date(model.checkout.holdExpiresAt).toLocaleTimeString("vi-VN")}</p>
          </div>
          <span style={pill}>Đang giữ ghế</span>
        </div>
        <div style={qrCard}>{model.checkout.qr}</div>
        <p style={muted}>Sau khi chuyển khoản, bấm xác nhận để admin kiểm tra và phát hành vé.</p>
      </div>
      <aside style={summaryCard}>
        <h2 style={{ margin: 0, fontSize: 20 }}>Đơn hàng</h2>
        <p>Mã ghế: {model.selectedSeats.map((seat) => seat.seatCode).join(", ")}</p>
        <div style={summaryRow}>
          <span>Tổng tiền</span>
          <strong>{Number(model.checkout.totalAmountVnd).toLocaleString("vi-VN")} VND</strong>
        </div>
        <button style={{ ...primaryButton, width: "100%" }} onClick={model.markPaymentCompleted}>Tôi đã chuyển khoản</button>
      </aside>
    </section>
  );
}

function PendingPanel({ model, visibleState }: MatchCheckoutFlowViewProps) {
  if (visibleState === "pending-empty") {
    return <StateCard>Không có giao dịch chờ xác nhận.</StateCard>;
  }
  if (visibleState === "pending-loading") {
    return <StateCard>Đang tải trạng thái xác nhận...</StateCard>;
  }
  if (visibleState === "pending-expired-error") {
    return <StateCard role="alert">Admin chưa xác nhận trong 10 phút. Đơn đã bị hủy và ghế đã được mở lại.</StateCard>;
  }
  if (visibleState !== "pending-confirmation" || !model.pending) {
    return null;
  }
  return (
    <section style={mapCard}>
      <span style={pill}>Đang chờ admin xác nhận</span>
      <h1 style={{ margin: "16px 0 8px", fontSize: 28 }}>Đơn vé đã gửi xác nhận</h1>
      <p>Admin sẽ kiểm tra trước {new Date(model.pending.adminConfirmExpiresAt).toLocaleTimeString("vi-VN")}</p>
      <button style={primaryButton}>Xem lịch sử mua vé</button>
    </section>
  );
}

function FilterCheck({ label, checked = false }: { label: string; checked?: boolean }) {
  return (
    <label style={{ display: "flex", gap: 10, alignItems: "center", fontSize: 14, color: "#334155" }}>
      <input type="checkbox" defaultChecked={checked} />
      {label}
    </label>
  );
}

function StateCard({ children, role }: { children: React.ReactNode; role?: string }) {
  return <section role={role} style={stateCard}>{children}</section>;
}

const pageShell = {
  minHeight: "100vh",
  background: "#f6f7fb",
  color: "#0f172a",
  fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
  padding: "18px clamp(16px, 3vw, 36px) 48px",
};

const topBar = {
  maxWidth: 1180,
  margin: "0 auto 18px",
  display: "flex",
  justifyContent: "space-between",
  gap: 16,
  alignItems: "center",
};

const brandLockup = { display: "flex", gap: 10, alignItems: "center" };
const brandMark = { display: "grid", placeItems: "center", width: 40, height: 40, borderRadius: 8, background: "#0f172a", color: "#fff", fontWeight: 800 };

const hero = {
  maxWidth: 1180,
  width: "100%",
  minHeight: 320,
  margin: "0 auto",
  borderRadius: 8,
  overflow: "hidden",
  backgroundImage: "linear-gradient(90deg, rgba(15,23,42,.88), rgba(15,23,42,.46)), url('https://images.unsplash.com/photo-1431324155629-1a6deb1dec8d?auto=format&fit=crop&w=1600&q=80')",
  backgroundSize: "cover",
  backgroundPosition: "center",
};

const heroOverlay = { padding: "48px clamp(20px, 5vw, 56px)", display: "grid", gap: 18, color: "#fff" };
const breadcrumb = { fontSize: 13, color: "rgba(255,255,255,.76)" };
const heroTitle = { margin: 0, maxWidth: 720, fontSize: "clamp(34px, 6vw, 64px)", lineHeight: .95, letterSpacing: 0 };
const heroCopy = { margin: 0, maxWidth: 640, color: "rgba(255,255,255,.86)", lineHeight: 1.55 };
const searchPanel = { display: "grid", gridTemplateColumns: "minmax(180px, 1.5fr) minmax(150px, .8fr) auto", gap: 10, maxWidth: 850, padding: 10, background: "rgba(255,255,255,.96)", borderRadius: 8 };
const searchField = { display: "grid", gap: 5, color: "#475569", fontSize: 12, fontWeight: 700 };
const searchInput = { minHeight: 42, border: "1px solid #e2e8f0", borderRadius: 6, padding: "0 12px", color: "#0f172a", background: "#fff" };

const contentGrid = { maxWidth: 1180, margin: "0 auto", display: "grid", gridTemplateColumns: "240px minmax(0, 1fr)", gap: 20, alignItems: "start" };
const filterPanel = { position: "sticky" as const, top: 16, display: "grid", gap: 14, padding: 18, border: "1px solid #e2e8f0", borderRadius: 8, background: "#fff" };
const dateHeader = { display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center" };
const matchCard = { display: "grid", gridTemplateColumns: "132px minmax(0, 1fr) auto", gap: 18, alignItems: "center", padding: 16, border: "1px solid #e2e8f0", borderRadius: 8, background: "#fff", boxShadow: "0 14px 34px rgba(15,23,42,.07)" };
const matchPoster = { height: 92, borderRadius: 8, backgroundImage: "linear-gradient(135deg, rgba(5,150,105,.9), rgba(14,165,233,.74)), url('https://images.unsplash.com/photo-1518091043644-c1d4457512c6?auto=format&fit=crop&w=500&q=80')", backgroundSize: "cover", backgroundPosition: "center", display: "flex", alignItems: "end", padding: 10, color: "#fff" };
const posterLeague = { fontSize: 12, fontWeight: 800, textTransform: "uppercase" as const };
const matchName = { display: "block", fontSize: 19, lineHeight: 1.25, overflowWrap: "anywhere" as const };
const matchMeta = { margin: "8px 0 0", color: "#475569" };
const tagRow = { display: "flex", gap: 8, flexWrap: "wrap" as const, marginTop: 12 };
const priceBlock = { display: "grid", justifyItems: "end", gap: 6, minWidth: 150 };

const detailHero = { maxWidth: 1180, margin: "0 auto", minHeight: 260, borderRadius: 8, padding: "34px clamp(20px, 4vw, 42px)", display: "flex", justifyContent: "space-between", gap: 18, alignItems: "end", color: "#fff", backgroundImage: "linear-gradient(90deg, rgba(2,6,23,.88), rgba(2,6,23,.35)), url('https://images.unsplash.com/photo-1522778119026-d647f0596c20?auto=format&fit=crop&w=1600&q=80')", backgroundSize: "cover", backgroundPosition: "center" };
const detailTitle = { margin: "8px 0", maxWidth: 760, fontSize: "clamp(32px, 5vw, 56px)", lineHeight: 1, letterSpacing: 0 };
const eventStatCard = { display: "grid", gap: 8, minWidth: 220, padding: 18, borderRadius: 8, background: "rgba(255,255,255,.94)", color: "#0f172a" };
const ticketLayout = { maxWidth: 1180, margin: "0 auto", display: "grid", gridTemplateColumns: "minmax(0, 1fr) 330px", gap: 20, alignItems: "start" };
const mapCard = { padding: 22, border: "1px solid #e2e8f0", borderRadius: 8, background: "#fff", boxShadow: "0 14px 34px rgba(15,23,42,.07)" };
const sectionHeader = { display: "flex", justifyContent: "space-between", gap: 18, alignItems: "start", marginBottom: 18 };
const legend = { display: "flex", gap: 12, flexWrap: "wrap" as const, color: "#475569", fontSize: 13 };
const legendDot = { display: "inline-block", width: 10, height: 10, borderRadius: 999, marginRight: 5 };
const seatGrid = { display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(116px, 1fr))", gap: 10 };
const seatButton = { minHeight: 78, borderRadius: 8, border: "1px solid #cbd5e1", display: "grid", gap: 3, padding: 10, textAlign: "left" as const, cursor: "pointer" };
const summaryCard = { position: "sticky" as const, top: 16, display: "grid", gap: 14, padding: 22, border: "1px solid #e2e8f0", borderRadius: 8, background: "#fff", boxShadow: "0 14px 34px rgba(15,23,42,.07)" };
const summaryRow = { display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center" };
const qrCard = { display: "grid", placeItems: "center", minHeight: 260, margin: "22px 0", border: "1px dashed #94a3b8", borderRadius: 8, background: "#f8fafc", color: "#0f172a", fontWeight: 700 };
const stateCard = { maxWidth: 1180, margin: "0 auto", padding: 24, border: "1px solid #e2e8f0", borderRadius: 8, background: "#fff" };
const alertBox = { maxWidth: 1180, margin: "0 auto", padding: 14, borderRadius: 8, border: "1px solid #f59e0b", background: "#fffbeb", color: "#92400e" };
const primaryButton = { minHeight: 42, border: "1px solid #0f172a", borderRadius: 6, padding: "0 16px", background: "#0f172a", color: "#fff", fontWeight: 800, cursor: "pointer" };
const ghostButton = { minHeight: 38, border: "1px solid #cbd5e1", borderRadius: 6, padding: "0 14px", background: "#fff", color: "#0f172a", fontWeight: 700, cursor: "pointer" };
const pill = { display: "inline-flex", alignItems: "center", width: "fit-content", borderRadius: 999, padding: "5px 10px", background: "#ecfdf5", color: "#047857", fontSize: 12, fontWeight: 800 };
const softTag = { display: "inline-flex", borderRadius: 999, padding: "5px 9px", background: "#eef2ff", color: "#3730a3", fontSize: 12, fontWeight: 700 };
const muted = { color: "#64748b", fontSize: 14 };
const divider = { height: 1, background: "#e2e8f0" };
const select = { minHeight: 38, border: "1px solid #cbd5e1", borderRadius: 6, padding: "0 10px", background: "#fff" };
