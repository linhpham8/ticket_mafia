import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { SeatExchange } from "./SeatExchange";
import { exchangeApi } from "../services/exchange.api";

vi.mock("../services/exchange.api", () => ({
  exchangeApi: {
    checkout: vi.fn()
  }
}));

const api = vi.mocked(exchangeApi);

describe("SeatExchange", () => {
  beforeEach(() => {
    api.checkout.mockReset();
  });

  afterEach(() => {
    cleanup();
  });

  it("allows only equal-or-higher available seats and submits exchange checkout", async () => {
    api.checkout.mockResolvedValueOnce({
      data: {
        orderId: "exchange-order-1",
        type: "EXCHANGE",
        priceDifferenceVnd: 50000,
        holdExpiresAt: "2026-07-01T12:10:00Z",
        paymentQr: { assetRef: "asset://payment/default" }
      }
    });

    render(<SeatExchange tokenProvider={() => "token"} idempotencyKeyFactory={() => "exchange-key-1"} />);

    expect(await screen.findByTestId("exchange-seat-grid")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "C-T1-001 · 80.000 VND" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "D-T1-001 · 160.000 VND" })).toBeDisabled();

    fireEvent.click(screen.getByRole("button", { name: "B-T1-001 · 150.000 VND" }));
    fireEvent.click(screen.getByRole("button", { name: "Tiếp tục đổi ghế" }));

    await waitFor(() => expect(screen.getByTestId("exchange-confirmed")).toHaveTextContent("exchange-order-1"));
    expect(api.checkout).toHaveBeenCalledWith("token", "ticket-demo", "seat-higher", "exchange-key-1");
  });

  it("renders empty and blocked states from SCREEN-012", async () => {
    const { unmount } = render(
      <SeatExchange seats={[{ seatId: "cheap", seatCode: "C-T1-001", priceVnd: 80000, status: "AVAILABLE" }]} />
    );
    expect(await screen.findByTestId("exchange-empty")).toHaveTextContent("Không có ghế phù hợp để đổi.");

    unmount();
    render(<SeatExchange tokenProvider={() => null} />);
    fireEvent.click(screen.getByRole("button", { name: "B-T1-001 · 150.000 VND" }));
    fireEvent.click(screen.getByRole("button", { name: "Tiếp tục đổi ghế" }));
    expect(await screen.findByTestId("exchange-error")).toHaveTextContent("Chỉ được đổi sang ghế có giá bằng hoặc cao hơn.");
  });
});
