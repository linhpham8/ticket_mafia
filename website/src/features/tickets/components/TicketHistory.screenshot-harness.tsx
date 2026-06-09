import React from "react";
import { createRoot } from "react-dom/client";
import { TicketHistory } from "./TicketHistory";

createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <TicketHistory tokenProvider={() => "demo-token"} />
  </React.StrictMode>
);
