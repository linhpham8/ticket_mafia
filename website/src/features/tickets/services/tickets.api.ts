export type TicketSummary = {
  ticketId: string;
  status: string;
  seatCode: string;
};

export type OrderHistoryRow = {
  orderId: string;
  status: string;
  matchName: string;
  totalAmountVnd: number;
  createdAt: string;
  tickets: TicketSummary[];
};

export type TicketDetail = {
  ticketId: string;
  match: { id: string; name: string };
  seatCode: string;
  status: string;
  qrToken: string | null;
  issuedAt: string;
  scannedAt: string | null;
};

async function requestJson<TResponse>(url: string, token: string): Promise<TResponse> {
  const response = await fetch(url, {
    headers: { "Authorization": `Bearer ${token}` }
  });
  if (!response.ok) {
    throw new Error("TICKET_REQUEST_FAILED");
  }
  return response.json() as Promise<TResponse>;
}

// Sprint: v1 | Feature: FR-009,NFR-003 | US: US-009,US-010 | Task Group: TG 1.5 Purchase History, Ticket Detail, and One-Time Scan
// Contract: api-specs-v1.md API-008/API-009; project-reference-v1.md PR-004 typed service boundary
export const ticketsApi = {
  listOrders: (token: string) => requestJson<{ data: OrderHistoryRow[]; meta: { nextCursor: string | null } }>("/api/v1/orders", token),
  getTicket: (token: string, ticketId: string) => requestJson<{ data: TicketDetail }>(`/api/v1/tickets/${ticketId}`, token)
};
