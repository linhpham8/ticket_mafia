export type ExchangeCheckoutResponse = {
  orderId: string;
  type: "EXCHANGE";
  priceDifferenceVnd: number;
  holdExpiresAt: string;
  paymentQr: { assetRef: string | null };
};

async function postJson<TResponse>(url: string, token: string, idempotencyKey: string, body: unknown): Promise<TResponse> {
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Idempotency-Key": idempotencyKey,
      "Content-Type": "application/json"
    },
    body: JSON.stringify(body)
  });
  if (!response.ok) {
    throw new Error("EXCHANGE_REQUEST_FAILED");
  }
  return response.json() as Promise<TResponse>;
}

// Sprint: v1 | Feature: FR-011,FR-012,NFR-002 | US: US-012 | Task Group: TG 1.6 Seat Exchange and Local Demo Runtime
// Contract: api-specs-v1.md API-014; project-reference-v1.md PR-004 typed service boundary
export const exchangeApi = {
  checkout: (token: string, ticketId: string, newSeatId: string, idempotencyKey: string) =>
    postJson<{ data: ExchangeCheckoutResponse }>(
      `/api/v1/tickets/${ticketId}/exchange/checkout`,
      token,
      idempotencyKey,
      { newSeatId }
    )
};
