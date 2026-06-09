import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { MatchCheckoutFlow } from "./MatchCheckoutFlow";
import { matchesApi } from "../services/matches.api";

vi.mock("../services/matches.api", () => ({
  matchesApi: {
    listMatches: vi.fn(),
    getSeatMap: vi.fn(),
    checkout: vi.fn(),
    paymentCompleted: vi.fn()
  }
}));

const api = vi.mocked(matchesApi);

describe("MatchCheckoutFlow", () => {
  beforeEach(() => {
    api.listMatches.mockReset();
    api.getSeatMap.mockReset();
    api.checkout.mockReset();
    api.paymentCompleted.mockReset();
  });

  afterEach(() => {
    cleanup();
  });

  it("loads matches and blocks selecting a sixth seat", async () => {
    api.listMatches.mockResolvedValueOnce([{ id: "match-1", name: "Hanoi vs Saigon", startsAt: null, status: "OPEN_FOR_SALE" }]);
    api.getSeatMap.mockResolvedValueOnce({
      data: {
        match: { id: "match-1", status: "OPEN_FOR_SALE" },
        seats: Array.from({ length: 6 }, (_, index) => ({
          id: `seat-${index + 1}`,
          seatCode: `A-T1-00${index + 1}`,
          sectionCode: "A",
          floorNo: 1,
          isVip: false,
          status: "AVAILABLE",
          priceVnd: 120000
        }))
      }
    });

    render(<MatchCheckoutFlow tokenProvider={() => "token"} />);
    fireEvent.click(await screen.findByRole("button", { name: "Chọn ghế" }));
    await screen.findByTestId("seat-map-grid");
    for (let index = 1; index <= 5; index += 1) {
      fireEvent.click(screen.getByTestId(`seat-A-T1-00${index}`));
    }
    fireEvent.click(screen.getByTestId("seat-A-T1-006"));

    expect(screen.getByRole("alert")).toHaveTextContent("Bạn chỉ có thể chọn tối đa 5 ghế cho mỗi lần mua.");
    expect(screen.getByText("5/5 ghế đã chọn")).toBeInTheDocument();
  });

  it("creates checkout and moves to pending confirmation", async () => {
    api.listMatches.mockResolvedValueOnce([{ id: "match-1", name: "Hanoi vs Saigon", startsAt: null, status: "OPEN_FOR_SALE" }]);
    api.getSeatMap.mockResolvedValueOnce({
      data: {
        match: { id: "match-1", status: "OPEN_FOR_SALE" },
        seats: [{
          id: "seat-1",
          seatCode: "A-T1-001",
          sectionCode: "A",
          floorNo: 1,
          isVip: false,
          status: "AVAILABLE",
          priceVnd: 120000
        }]
      }
    });
    api.checkout.mockResolvedValueOnce({
      data: {
        orderId: "order-1",
        status: "HELD",
        holdExpiresAt: "2026-07-01T12:10:00Z",
        totalAmountVnd: 120000,
        items: [{ seatId: "seat-1", seatCode: "A-T1-001", priceSnapshotVnd: 120000 }],
        paymentQr: { assetRef: "asset://payment/default" }
      }
    });
    api.paymentCompleted.mockResolvedValueOnce({
      data: {
        orderId: "order-1",
        status: "PENDING_ADMIN_CONFIRM",
        adminConfirmExpiresAt: "2026-07-01T12:20:00Z"
      }
    });

    render(<MatchCheckoutFlow tokenProvider={() => "token"} />);
    fireEvent.click(await screen.findByRole("button", { name: "Chọn ghế" }));
    fireEvent.click(await screen.findByTestId("seat-A-T1-001"));
    fireEvent.click(screen.getByRole("button", { name: "Thanh toán" }));

    expect(await screen.findByTestId("checkout-qr")).toBeInTheDocument();
    expect(screen.getByText("asset://payment/default")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Tôi đã chuyển khoản" }));

    await waitFor(() => expect(screen.getByTestId("pending-confirmation")).toBeInTheDocument());
    expect(api.checkout).toHaveBeenCalledWith("token", "match-1", ["seat-1"]);
    expect(api.paymentCompleted).toHaveBeenCalledWith("token", "order-1");
  });
});
