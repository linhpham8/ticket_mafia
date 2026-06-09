let accessToken: string | null = null;

// Sprint: v1 | Feature: FR-001,NFR-003 | US: US-001 | Task Group: TG 1.1 Foundation and Auth
// Contract: api-specs-v1.md API-002; project-reference-v1.md PR-004 frontend typed service boundary
export const authSession = {
  setAccessToken(token: string) {
    accessToken = token;
  },
  getAccessToken() {
    return accessToken;
  },
  clear() {
    accessToken = null;
  }
};
