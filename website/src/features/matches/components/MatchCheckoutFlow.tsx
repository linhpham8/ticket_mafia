"use client";

import { MatchCheckoutFlowView } from "./MatchCheckoutFlowView";
import { FlowState, useMatchCheckoutFlow } from "./useMatchCheckoutFlow";

export type { FlowState };

type MatchCheckoutFlowProps = {
  tokenProvider?: () => string | null;
};

// Sprint: v1 | Feature: FR-002,FR-003,FR-004,FR-005 | US: US-002..US-005 | Task Group: TG 1.3 User Browse, Seat Selection, Checkout Hold, and Payment Completion
// Contract: design-system-v1.md SCREEN-002..SCREEN-005; api-specs-v1.md API-003..API-006 through typed service
export function MatchCheckoutFlow({ tokenProvider }: MatchCheckoutFlowProps) {
  const model = useMatchCheckoutFlow({ tokenProvider });

  return <MatchCheckoutFlowView model={model} />;
}
