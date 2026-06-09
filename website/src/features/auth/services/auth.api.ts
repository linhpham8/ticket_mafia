// Sprint: v1 | Feature: FR-001,NFR-003 | US: US-001 | Task Group: TG 1.1 Foundation and Auth
// Contract: api-specs-v1.md API-001/API-002; project-reference-v1.md PR-004 typed API client boundary
export type OtpChallengeResponse = {
  data: {
    challengeId: string;
    expiresAt?: string;
  };
};

export type OtpVerifyResponse = {
  data: {
    accessToken: string;
    expiresAt?: string;
  };
};

async function postJson<TResponse>(url: string, body: unknown): Promise<TResponse> {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  if (!response.ok) {
    throw new Error("AUTH_REQUEST_FAILED");
  }
  return response.json() as Promise<TResponse>;
}

export function requestOtp(identifier: string) {
  return postJson<OtpChallengeResponse>("/api/v1/auth/otp/request", { identifier });
}

export function verifyOtp(challengeId: string, otp: string) {
  return postJson<OtpVerifyResponse>("/api/v1/auth/otp/verify", { challengeId, otp });
}
