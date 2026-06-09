import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { TicketHistory } from "./TicketHistory";
import { ticketsApi } from "../services/tickets.api";

vi.mock("../services/tickets.api", () => ({
  ticketsApi: {
    listOrders: vi.fn(),
    getTicket: vi.fn()
  }
}));

const api = vi.mocked(ticketsApi);

describe("TicketHistory", () => {
  beforeEach(() => {
    api.listOrders.mockReset();
    api.getTicket.mockReset();
  });

  afterEach(() => {
    cleanup();
  });

  it("renders only returned order history rows and opens an issued QR detail", async () => {
    api.listOrders.mockResolvedValueOnce({
      data: [{
        orderId: "order-1",
        status: "ISSUED",
        matchName: "Hanoi vs Saigon",
        totalAmountVnd: 120000,
        createdAt: "2026-07-01T12:00:00Z",
        tickets: [{ ticketId: "ticket-1", status: "ISSUED", seatCode: "A-T1-001" }]
      }],
      meta: { nextCursor: null }
    });
    api.getTicket.mockResolvedValueOnce({
      data: {
        ticketId: "ticket-1",
        match: { id: "match-1", name: "Hanoi vs Saigon" },
        seatCode: "A-T1-001",
        status: "ISSUED",
        qrToken: "tk_v1_signedopaque",
        issuedAt: "2026-07-01T12:00:00Z",
        scannedAt: null
      }
    });

    render(<TicketHistory tokenProvider={() => "token"} />);

    expect(await screen.findByTestId("ticket-history-list")).toBeInTheDocument();
    expect(screen.getByText("Hanoi vs Saigon")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "A-T1-001 · ISSUED" }));

    await waitFor(() => expect(screen.getByTestId("ticket-qr-card")).toHaveTextContent("tk_v1_signedopaque"));
    expect(api.listOrders).toHaveBeenCalledWith("token");
    expect(api.getTicket).toHaveBeenCalledWith("token", "ticket-1");
  });

  it("shows empty state and suppresses QR for invalid ticket status", async () => {
    api.listOrders.mockResolvedValueOnce({
      data: [{
        orderId: "order-2",
        status: "REJECTED",
        matchName: "Hanoi vs Hue",
        totalAmountVnd: 120000,
        createdAt: "2026-07-01T12:00:00Z",
        tickets: [{ ticketId: "ticket-2", status: "CANCELLED", seatCode: "B-T1-001" }]
      }],
      meta: { nextCursor: null }
    });
    api.getTicket.mockResolvedValueOnce({
      data: {
        ticketId: "ticket-2",
        match: { id: "match-2", name: "Hanoi vs Hue" },
        seatCode: "B-T1-001",
        status: "CANCELLED",
        qrToken: null,
        issuedAt: "2026-07-01T12:00:00Z",
        scannedAt: null
      }
    });

    render(<TicketHistory tokenProvider={() => "token"} />);
    fireEvent.click(await screen.findByRole("button", { name: "B-T1-001 · CANCELLED" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Vé này không còn hợp lệ để vào sân.");
    expect(screen.queryByTestId("ticket-qr-card")).not.toBeInTheDocument();
  });
});
