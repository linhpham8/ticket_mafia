export type PendingConfirmation = {
  orderId: string;
  type: "PURCHASE" | "EXCHANGE";
  userIdentifier: string;
  totalAmountVnd: number;
  seatCount: number;
  adminConfirmExpiresAt: string;
  status: "PENDING_ADMIN_CONFIRM";
};

// Sprint: v1 | Feature: FR-008 | US: US-008 | Task Group: TG 1.4 Admin Payment Confirmation and Audit
// Contract: design-system-v1.md SCREEN-008/DS-COMP-004/DS-COMP-005; project-reference-v1.md PR-004 typed admin feature service
export async function listPendingConfirmations(): Promise<PendingConfirmation[]> {
  return [
    {
      orderId: "demo-order-1",
      type: "PURCHASE",
      userIdentifier: "fan1@example.test",
      totalAmountVnd: 240000,
      seatCount: 2,
      adminConfirmExpiresAt: "2026-07-01T12:10:00Z",
      status: "PENDING_ADMIN_CONFIRM",
    },
    {
      orderId: "demo-exchange-1",
      type: "EXCHANGE",
      userIdentifier: "fan2@example.test",
      totalAmountVnd: 50000,
      seatCount: 1,
      adminConfirmExpiresAt: "2026-07-01T12:06:00Z",
      status: "PENDING_ADMIN_CONFIRM",
    },
  ];
}
