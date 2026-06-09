"use client";

import { useEffect, useMemo, useState } from "react";
import { authSession } from "../../auth";
import { MatchRow, SeatRow, matchesApi } from "../services/matches.api";

export type FlowState = "matches-loading" | "matches-empty" | "matches-list" | "matches-error" |
  "seat-map-loading" | "seat-map-empty" | "seat-map-grid" | "seat-map-error" |
  "checkout-empty" | "checkout-loading" | "checkout-qr" | "checkout-expired-error" |
  "pending-empty" | "pending-loading" | "pending-confirmation" | "pending-expired-error";

export type CheckoutSummary = {
  orderId: string;
  holdExpiresAt: string;
  totalAmountVnd: number;
  qr: string;
};

export type PendingSummary = {
  orderId: string;
  adminConfirmExpiresAt: string;
};

export type MatchCheckoutModel = {
  state: FlowState;
  matches: MatchRow[];
  selectedMatch: MatchRow | null;
  seats: SeatRow[];
  selectedSeatIds: string[];
  selectedSeats: SeatRow[];
  message: string;
  checkout: CheckoutSummary | null;
  pending: PendingSummary | null;
  showMatchList: () => void;
  openSeats: (match: MatchRow) => Promise<void>;
  toggleSeat: (seat: SeatRow) => void;
  startCheckout: () => Promise<void>;
  markPaymentCompleted: () => Promise<void>;
};

type UseMatchCheckoutFlowOptions = {
  tokenProvider?: () => string | null;
};

// Sprint: v1 | Feature: FR-002,FR-003,FR-004,FR-005 | US: US-002..US-005 | Task Group: TG 1.3 User Browse, Seat Selection, Checkout Hold, and Payment Completion
// Contract: design-system-v1.md SCREEN-002..SCREEN-005; api-specs-v1.md API-003..API-006 through typed service
export function useMatchCheckoutFlow({
  tokenProvider = authSession.getAccessToken
}: UseMatchCheckoutFlowOptions = {}): MatchCheckoutModel {
  const [state, setState] = useState<FlowState>("matches-loading");
  const [matches, setMatches] = useState<MatchRow[]>([]);
  const [selectedMatch, setSelectedMatch] = useState<MatchRow | null>(null);
  const [seats, setSeats] = useState<SeatRow[]>([]);
  const [selectedSeatIds, setSelectedSeatIds] = useState<string[]>([]);
  const [message, setMessage] = useState("");
  const [checkout, setCheckout] = useState<CheckoutSummary | null>(null);
  const [pending, setPending] = useState<PendingSummary | null>(null);

  useEffect(() => {
    matchesApi.listMatches()
      .then((rows) => {
        setMatches(rows);
        setState(rows.length === 0 ? "matches-empty" : "matches-list");
      })
      .catch(() => setState("matches-error"));
  }, []);

  const selectedSeats = useMemo(
    () => seats.filter((seat) => selectedSeatIds.includes(seat.id)),
    [seats, selectedSeatIds]
  );

  async function openSeats(match: MatchRow) {
    setSelectedMatch(match);
    setState("seat-map-loading");
    setMessage("");
    try {
      const body = await matchesApi.getSeatMap(match.id);
      setSeats(body.data.seats);
      setSelectedSeatIds([]);
      setState(body.data.seats.length === 0 ? "seat-map-empty" : "seat-map-grid");
    } catch {
      setState("seat-map-error");
    }
  }

  function toggleSeat(seat: SeatRow) {
    if (seat.status !== "AVAILABLE") {
      setMessage("Ghế này vừa được người khác giữ. Vui lòng chọn ghế khác.");
      return;
    }
    if (selectedSeatIds.includes(seat.id)) {
      setSelectedSeatIds(selectedSeatIds.filter((id) => id !== seat.id));
      return;
    }
    if (selectedSeatIds.length >= 5) {
      setMessage("Bạn chỉ có thể chọn tối đa 5 ghế cho mỗi lần mua.");
      return;
    }
    setSelectedSeatIds([...selectedSeatIds, seat.id]);
  }

  async function startCheckout() {
    const token = tokenProvider();
    if (!token) {
      setMessage("Vui lòng đăng nhập để tiếp tục mua vé.");
      return;
    }
    if (!selectedMatch || selectedSeatIds.length === 0) {
      return;
    }
    setState("checkout-loading");
    try {
      const body = await matchesApi.checkout(token, selectedMatch.id, selectedSeatIds);
      setCheckout({
        orderId: body.data.orderId,
        holdExpiresAt: body.data.holdExpiresAt,
        totalAmountVnd: body.data.totalAmountVnd,
        qr: body.data.paymentQr.assetRef
      });
      setState("checkout-qr");
    } catch {
      setState("checkout-expired-error");
    }
  }

  async function markPaymentCompleted() {
    const token = tokenProvider();
    if (!token || !checkout) {
      return;
    }
    try {
      const body = await matchesApi.paymentCompleted(token, checkout.orderId);
      setPending({ orderId: body.data.orderId, adminConfirmExpiresAt: body.data.adminConfirmExpiresAt });
      setState("pending-confirmation");
    } catch {
      setState("pending-expired-error");
    }
  }

  return {
    state,
    matches,
    selectedMatch,
    seats,
    selectedSeatIds,
    selectedSeats,
    message,
    checkout,
    pending,
    showMatchList: () => setState("matches-list"),
    openSeats,
    toggleSeat,
    startCheckout,
    markPaymentCompleted
  };
}
