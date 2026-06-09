export type MatchRow = {
  id: string;
  name: string;
  startsAt: string | null;
  status: string;
};

export type SeatRow = {
  id: string;
  seatCode: string;
  sectionCode: string;
  floorNo: number;
  isVip: boolean;
  status: string;
  priceVnd: number;
};

export type SeatMapResponse = {
  data: {
    match: { id: string; status: string };
    seats: SeatRow[];
  };
};

export type CheckoutResponse = {
  data: {
    orderId: string;
    status: "HELD";
    holdExpiresAt: string;
    totalAmountVnd: number;
    items: { seatId: string; seatCode: string; priceSnapshotVnd: number }[];
    paymentQr: { assetRef: string };
  };
};

export type PaymentCompletedResponse = {
  data: {
    orderId: string;
    status: "PENDING_ADMIN_CONFIRM";
    adminConfirmExpiresAt: string;
  };
};

const demoMatches: MatchRow[] = [
  {
    id: "demo-match-1",
    name: "Hanoi FC vs Saigon FC",
    startsAt: "2026-07-01T19:00:00+07:00",
    status: "OPEN_FOR_SALE",
  },
  {
    id: "demo-match-2",
    name: "Da Nang FC vs Hue FC",
    startsAt: "2026-07-05T18:30:00+07:00",
    status: "OPEN_FOR_SALE",
  },
  {
    id: "demo-match-3",
    name: "Viettel FC vs Thanh Hoa FC",
    startsAt: "2026-07-12T20:00:00+07:00",
    status: "OPEN_FOR_SALE",
  },
];

const demoSeats: SeatRow[] = [
  { id: "demo-seat-1", seatCode: "A-VIP-001", sectionCode: "A", floorNo: 1, isVip: true, status: "AVAILABLE", priceVnd: 250000 },
  { id: "demo-seat-2", seatCode: "A-VIP-002", sectionCode: "A", floorNo: 1, isVip: true, status: "AVAILABLE", priceVnd: 250000 },
  { id: "demo-seat-3", seatCode: "A-T1-011", sectionCode: "A", floorNo: 1, isVip: false, status: "AVAILABLE", priceVnd: 180000 },
  { id: "demo-seat-4", seatCode: "A-T1-012", sectionCode: "A", floorNo: 1, isVip: false, status: "HELD", priceVnd: 180000 },
  { id: "demo-seat-5", seatCode: "B-T1-021", sectionCode: "B", floorNo: 1, isVip: false, status: "AVAILABLE", priceVnd: 140000 },
  { id: "demo-seat-6", seatCode: "B-T2-041", sectionCode: "B", floorNo: 2, isVip: false, status: "AVAILABLE", priceVnd: 120000 },
  { id: "demo-seat-7", seatCode: "C-T1-031", sectionCode: "C", floorNo: 1, isVip: false, status: "AVAILABLE", priceVnd: 100000 },
  { id: "demo-seat-8", seatCode: "D-T2-061", sectionCode: "D", floorNo: 2, isVip: false, status: "AVAILABLE", priceVnd: 90000 },
];

async function requestJson<TResponse>(url: string, init?: RequestInit): Promise<TResponse> {
  const response = await fetch(url, init);
  if (!response.ok) {
    throw new Error("MATCH_CHECKOUT_REQUEST_FAILED");
  }
  return response.json() as Promise<TResponse>;
}

async function requestJsonWithFallback<TResponse>(url: string, fallback: TResponse): Promise<TResponse> {
  const controller = new AbortController();
  let timeoutId: ReturnType<typeof setTimeout> | undefined;
  const fallbackAfterTimeout = new Promise<TResponse>((resolve) => {
    timeoutId = setTimeout(() => {
      controller.abort();
      resolve(fallback);
    }, 1200);
  });
  try {
    return await Promise.race([
      requestJson<TResponse>(url, { signal: controller.signal }),
      fallbackAfterTimeout,
    ]);
  } catch {
    return fallback;
  } finally {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
  }
}

// Sprint: v1 | Feature: FR-002,FR-003,FR-004,FR-005 | US: US-002..US-005 | Task Group: TG 1.3 User Browse, Seat Selection, Checkout Hold, and Payment Completion
// Contract: api-specs-v1.md API-003..API-006; project-reference-v1.md PR-004 typed service boundary
export const matchesApi = {
  listMatches: () =>
    requestJsonWithFallback<{ data: MatchRow[] }>("/api/v1/matches", { data: demoMatches }).then((body) => body.data),
  getSeatMap: (matchId: string) =>
    requestJsonWithFallback<SeatMapResponse>(`/api/v1/matches/${matchId}/seats`, {
      data: {
        match: { id: matchId, status: "OPEN_FOR_SALE" },
        seats: demoSeats,
      },
    }),
  checkout: (token: string, matchId: string, seatIds: string[]) =>
    requestJson<CheckoutResponse>("/api/v1/orders/checkout", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
        "Idempotency-Key": crypto.randomUUID()
      },
      body: JSON.stringify({ matchId, seatIds })
    }),
  paymentCompleted: (token: string, orderId: string) =>
    requestJson<PaymentCompletedResponse>(`/api/v1/orders/${orderId}/payment-completed`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
        "Idempotency-Key": crypto.randomUUID()
      }
    })
};
