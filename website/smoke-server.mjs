import http from "node:http";

const pages = {
  "/login": "<main data-testid=\"login-form\"><h1>Đăng nhập OTP</h1></main>",
  "/tickets": "<main data-testid=\"ticket-history-list\"><h1>Lịch sử mua vé</h1></main>",
  "/tickets/exchange": "<main data-testid=\"exchange-seat-grid\"><h1>Đổi ghế</h1></main>",
};

// Sprint: v1 | Feature: FR-011,FR-012,NFR-005 | US: US-012 | Task Group: TG 1.6 Seat Exchange and Local Demo Runtime
// Contract: nfr-v1.md NFR-005 local Docker Compose self-test for website smoke routes.
const server = http.createServer((request, response) => {
  const body = pages[request.url ?? "/"] ?? pages["/login"];
  response.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
  response.end(`
    <!doctype html>
    <html lang="vi">
      <head><title>Ticket Mafia Website Smoke</title></head>
      <body>${body}</body>
    </html>
  `);
});

server.listen(3000, "0.0.0.0");
