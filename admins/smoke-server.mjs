import http from "node:http";

const server = http.createServer((request, response) => {
  if (request.url === "/login" || request.url === "/") {
    response.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
    response.end(`
      <!doctype html>
      <html lang="vi">
        <head><title>Admin Login Smoke</title></head>
        <body>
          <main data-testid="login-form">
            <h1>Dang nhap quan tri</h1>
            <p>Admin shell consumes the TG 1.1 mock OTP API and shared session convention.</p>
          </main>
        </body>
      </html>
    `);
    return;
  }
  response.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
  response.end("Not found");
});

server.listen(3001, "0.0.0.0");
