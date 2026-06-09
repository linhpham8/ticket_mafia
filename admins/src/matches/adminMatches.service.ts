export type MatchStatus = "OPEN_FOR_SALE" | "SOLD_OUT" | "CANCELLED" | "CLOSED";

export type AdminMatch = {
  id: string;
  name: string;
  startsAt: string;
  status: MatchStatus;
};

export type InventoryPrice = {
  sectionCode: "A" | "B" | "C" | "D";
  floorNo: 1 | 2;
  isVip: boolean;
  priceVnd: number;
};

export type PaymentQrConfig = {
  name: string;
  qrAssetRef: string;
  isDefault: boolean;
};

// Sprint: v1 | Feature: FR-006,FR-007 | US: US-006,US-007 | Task Group: TG 1.2 Admin Match Inventory, Pricing, and QR
// Contract: design-system-v1.md SCREEN-006/SCREEN-007; project-reference-v1.md PR-002 typed admin feature service
export async function listAdminMatches(): Promise<AdminMatch[]> {
  return [
    {
      id: "demo-match-1",
      name: "Hanoi FC vs Saigon FC",
      startsAt: "2026-07-01T12:00:00Z",
      status: "OPEN_FOR_SALE",
    },
    {
      id: "demo-match-2",
      name: "Danang FC vs Hue FC",
      startsAt: "2026-07-05T12:00:00Z",
      status: "CLOSED",
    },
  ];
}

export async function getInventoryConfig(): Promise<{
  seatSummary: string;
  prices: InventoryPrice[];
  qrConfigs: PaymentQrConfig[];
}> {
  return {
    seatSummary: "A-VIP-001..A-VIP-120, B-T2-001..B-T2-120",
    prices: [
      { sectionCode: "A", floorNo: 1, isVip: true, priceVnd: 250000 },
      { sectionCode: "B", floorNo: 2, isVip: false, priceVnd: 120000 },
    ],
    qrConfigs: [{ name: "QR MB Bank", qrAssetRef: "asset://payment/default-mb", isDefault: true }],
  };
}
