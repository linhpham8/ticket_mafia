import { afterEach, describe, expect, it, vi } from "vitest";
import { matchesApi } from "./matches.api";

describe("matchesApi", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("falls back to demo matches when the backend match list is unavailable", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false }));

    const matches = await matchesApi.listMatches();

    expect(matches.length).toBeGreaterThan(0);
    expect(matches[0]).toMatchObject({
      id: "demo-match-1",
      status: "OPEN_FOR_SALE",
    });
  });

  it("falls back to demo seats when the backend seat map is unavailable", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("backend down")));

    const body = await matchesApi.getSeatMap("demo-match-1");

    expect(body.data.match).toEqual({ id: "demo-match-1", status: "OPEN_FOR_SALE" });
    expect(body.data.seats.some((seat) => seat.status === "AVAILABLE")).toBe(true);
  });
});
