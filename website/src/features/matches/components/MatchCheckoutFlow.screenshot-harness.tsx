import React from "react";
import { createRoot } from "react-dom/client";
import { MatchCheckoutFlowView } from "./MatchCheckoutFlowView";
import { FlowState, useMatchCheckoutFlow } from "./useMatchCheckoutFlow";

const screenshotState = new URLSearchParams(window.location.search).get("state") as FlowState | null;

function MatchCheckoutScreenshotHarness() {
  const model = useMatchCheckoutFlow({ tokenProvider: () => "demo-token" });

  return <MatchCheckoutFlowView model={model} visibleState={screenshotState ?? undefined} />;
}

createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <MatchCheckoutScreenshotHarness />
  </React.StrictMode>
);
