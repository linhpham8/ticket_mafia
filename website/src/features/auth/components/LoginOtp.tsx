"use client";

import { FormEvent, useState } from "react";
import { requestOtp, verifyOtp } from "../services/auth.api";
import { authSession } from "../services/authSession";

type LoginState = "empty" | "form" | "loading" | "error" | "success";

// Sprint: v1 | Feature: FR-001,NFR-003 | US: US-001 | Task Group: TG 1.1 Foundation and Auth
// Contract: design-system-v1.md SCREEN-001; api-specs-v1.md API-001/API-002 through auth API service
export function LoginOtp() {
  const [identifier, setIdentifier] = useState("");
  const [otp, setOtp] = useState("");
  const [challengeId, setChallengeId] = useState<string | null>(null);
  const [state, setState] = useState<LoginState>("empty");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!identifier.trim()) {
      return;
    }
    setState("loading");
    try {
      if (!challengeId) {
        const body = await requestOtp(identifier);
        setChallengeId(body.data.challengeId);
        setState("form");
        return;
      }
      const body = await verifyOtp(challengeId, otp);
      authSession.setAccessToken(body.data.accessToken);
      setState("success");
    } catch {
        setState("error");
    }
  }

  const stateId = state === "empty" ? "login-empty" : state === "loading" ? "login-loading" :
    state === "error" ? "login-error" : "login-form";

  return (
    <main className="auth-shell" data-testid={stateId}>
      <form aria-label="Đăng nhập OTP" onSubmit={submit}>
        <h1>Đăng nhập để mua vé</h1>
        <label htmlFor="identifier">Email hoặc số điện thoại</label>
        <input
          id="identifier"
          value={identifier}
          onChange={(event) => {
            setIdentifier(event.target.value);
            if (state === "empty" && event.target.value.trim()) {
              setState("form");
            }
          }}
        />
        {challengeId ? (
          <>
            <label htmlFor="otp">Mã OTP</label>
            <input id="otp" value={otp} onChange={(event) => setOtp(event.target.value)} />
            <p>Demo OTP: 000000</p>
          </>
        ) : null}
        {state === "error" ? <p role="alert">Mã OTP không đúng. Vui lòng kiểm tra và thử lại.</p> : null}
        {state === "success" ? <p role="status">Đăng nhập thành công.</p> : null}
        <button disabled={!identifier.trim() || state === "loading"}>
          {state === "loading" ? (challengeId ? "Đang xác thực..." : "Đang gửi...") : "Tiếp tục"}
        </button>
      </form>
    </main>
  );
}
