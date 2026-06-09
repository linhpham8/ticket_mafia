"use client";

import { useMemo, useState } from "react";
import { authSession } from "../../auth";
import { exchangeApi, ExchangeCheckoutResponse } from "../services/exchange.api";

type SeatOption = {
  seatId: string;
  seatCode: string;
  priceVnd: number;
  status: "AVAILABLE" | "HELD" | "ISSUED";
};

type SeatExchangeProps = {
  ticketId?: string;
  currentSeatCode?: string;
  currentPriceVnd?: number;
  seats?: SeatOption[];
  tokenProvider?: () => string | null;
  idempotencyKeyFactory?: () => string;
};

const defaultSeats: SeatOption[] = [
  { seatId: "seat-higher", seatCode: "B-T1-001", priceVnd: 150000, status: "AVAILABLE" },
  { seatId: "seat-equal", seatCode: "A-T1-002", priceVnd: 100000, status: "AVAILABLE" },
  { seatId: "seat-cheaper", seatCode: "C-T1-001", priceVnd: 80000, status: "AVAILABLE" },
  { seatId: "seat-held", seatCode: "D-T1-001", priceVnd: 160000, status: "HELD" }
];

// Sprint: v1 | Feature: FR-011,FR-012,BR-007 | US: US-012 | Task Group: TG 1.6 Seat Exchange and Local Demo Runtime
// Contract: design-system-v1.md SCREEN-012; api-specs-v1.md API-014 through typed exchange service
export function SeatExchange({
  ticketId = "ticket-demo",
  currentSeatCode = "A-T1-001",
  currentPriceVnd = 100000,
  seats = defaultSeats,
  tokenProvider = authSession.getAccessToken,
  idempotencyKeyFactory = () => `exchange-${Date.now()}`
}: SeatExchangeProps) {
  const [selectedSeatId, setSelectedSeatId] = useState<string | null>(null);
  const [state, setState] = useState<"empty" | "populated" | "error" | "confirmed">(
    seats.some((seat) => seat.status === "AVAILABLE" && seat.priceVnd >= currentPriceVnd) ? "populated" : "empty"
  );
  const [checkout, setCheckout] = useState<ExchangeCheckoutResponse | null>(null);
  const eligibleSeats = useMemo(
    () => seats.filter((seat) => seat.status === "AVAILABLE" && seat.priceVnd >= currentPriceVnd),
    [currentPriceVnd, seats]
  );
  const selectedSeat = seats.find((seat) => seat.seatId === selectedSeatId) ?? null;

  async function continueExchange() {
    if (!selectedSeat || selectedSeat.status !== "AVAILABLE" || selectedSeat.priceVnd < currentPriceVnd) {
      setState("error");
      return;
    }
    const token = tokenProvider();
    if (!token) {
      setState("error");
      return;
    }
    try {
      const response = await exchangeApi.checkout(token, ticketId, selectedSeat.seatId, idempotencyKeyFactory());
      setCheckout(response.data);
      setState("confirmed");
    } catch {
      setState("error");
    }
  }

  if (state === "empty") {
    return <main data-testid="exchange-empty">Không có ghế phù hợp để đổi.</main>;
  }
  if (state === "error") {
    return <main data-testid="exchange-error" role="alert">Chỉ được đổi sang ghế có giá bằng hoặc cao hơn.</main>;
  }
  if (state === "confirmed" && checkout) {
    return (
      <main data-testid="exchange-confirmed" style={{ maxWidth: 760, margin: "0 auto", padding: 24, fontFamily: "system-ui" }}>
        <h1>Đổi ghế</h1>
        <p>Đơn đổi ghế: {checkout.orderId}</p>
        <p>Chênh lệch: {Number(checkout.priceDifferenceVnd).toLocaleString("vi-VN")} VND</p>
        {checkout.paymentQr.assetRef ? <p>{checkout.paymentQr.assetRef}</p> : <p>Không cần thanh toán thêm.</p>}
      </main>
    );
  }

  return (
    <main data-testid="exchange-seat-grid" style={{ maxWidth: 760, margin: "0 auto", padding: 24, fontFamily: "system-ui" }}>
      <h1>Đổi ghế</h1>
      <p>Ghế hiện tại: {currentSeatCode}</p>
      <section aria-label="Danh sách ghế đổi">
        {seats.map((seat) => {
          const eligible = eligibleSeats.some((eligibleSeat) => eligibleSeat.seatId === seat.seatId);
          return (
            <button
              key={seat.seatId}
              type="button"
              disabled={!eligible}
              aria-pressed={selectedSeatId === seat.seatId}
              onClick={() => setSelectedSeatId(seat.seatId)}
              style={{ display: "block", marginBottom: 8, padding: 10 }}
            >
              {seat.seatCode} · {Number(seat.priceVnd).toLocaleString("vi-VN")} VND
            </button>
          );
        })}
      </section>
      <button type="button" onClick={continueExchange} disabled={!selectedSeatId}>
        Tiếp tục đổi ghế
      </button>
    </main>
  );
}
