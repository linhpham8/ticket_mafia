import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { LoginOtp } from "./LoginOtp";
import { requestOtp, verifyOtp } from "../services/auth.api";
import { authSession } from "../services/authSession";

vi.mock("../services/auth.api", () => ({
  requestOtp: vi.fn(),
  verifyOtp: vi.fn()
}));

const requestOtpMock = vi.mocked(requestOtp);
const verifyOtpMock = vi.mocked(verifyOtp);

describe("LoginOtp", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    authSession.clear();
    requestOtpMock.mockReset();
    verifyOtpMock.mockReset();
  });

  afterEach(() => {
    cleanup();
  });

  it("keeps CTA disabled until identifier is present", () => {
    render(<LoginOtp />);
    expect(screen.getByTestId("login-empty")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Tiếp tục" })).toBeDisabled();
  });

  it("requests challenge then verifies demo OTP", async () => {
    requestOtpMock.mockResolvedValueOnce({ data: { challengeId: "challenge-1" } });
    verifyOtpMock.mockResolvedValueOnce({ data: { accessToken: "token" } });

    render(<LoginOtp />);
    fireEvent.change(screen.getByLabelText("Email hoặc số điện thoại"), { target: { value: "fan1@example.test" } });
    fireEvent.click(screen.getByRole("button", { name: "Tiếp tục" }));
    await screen.findByText("Demo OTP: 000000");
    fireEvent.change(screen.getByLabelText("Mã OTP"), { target: { value: "000000" } });
    fireEvent.click(screen.getByRole("button", { name: "Tiếp tục" }));

    await waitFor(() => expect(screen.getByRole("status")).toHaveTextContent("Đăng nhập thành công."));
    expect(requestOtpMock).toHaveBeenCalledWith("fan1@example.test");
    expect(verifyOtpMock).toHaveBeenCalledWith("challenge-1", "000000");
    expect(authSession.getAccessToken()).toBe("token");
  });

  it("shows loading while requesting a challenge", async () => {
    requestOtpMock.mockImplementation(() => new Promise(() => undefined));

    render(<LoginOtp />);
    fireEvent.change(screen.getByLabelText("Email hoặc số điện thoại"), { target: { value: "fan1@example.test" } });
    fireEvent.click(screen.getByRole("button", { name: "Tiếp tục" }));

    expect(await screen.findByTestId("login-loading")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Đang gửi..." })).toBeDisabled();
  });

  it("shows the contract error copy when OTP verification fails", async () => {
    requestOtpMock.mockResolvedValueOnce({ data: { challengeId: "challenge-1" } });
    verifyOtpMock.mockRejectedValueOnce(new Error("AUTH_OTP_INVALID"));

    render(<LoginOtp />);
    fireEvent.change(screen.getByLabelText("Email hoặc số điện thoại"), { target: { value: "fan1@example.test" } });
    fireEvent.click(screen.getByRole("button", { name: "Tiếp tục" }));
    await screen.findByText("Demo OTP: 000000");
    fireEvent.change(screen.getByLabelText("Mã OTP"), { target: { value: "111111" } });
    fireEvent.click(screen.getByRole("button", { name: "Tiếp tục" }));

    expect(await screen.findByTestId("login-error")).toBeInTheDocument();
    expect(screen.getByRole("alert")).toHaveTextContent("Mã OTP không đúng. Vui lòng kiểm tra và thử lại.");
  });
});
