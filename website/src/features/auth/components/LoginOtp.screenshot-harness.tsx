import React from "react";
import { createRoot } from "react-dom/client";
import { LoginOtp } from "./LoginOtp";

createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <LoginOtp />
  </React.StrictMode>
);
