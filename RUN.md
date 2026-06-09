1. Chạy nhanh bằng Docker Compose smoke runtime
   Cách này bật postgres + backend + website smoke + admin smoke.

export TICKETING_QR_SIGNING_SECRET=local-dev-secret-change-me
docker compose --profile local up --build

Mở:

- Backend health: http://localhost:8080/actuator/health
- Website smoke: http://localhost:3000/login
- Admin smoke: http://localhost:3001/login

Tắt:

docker compose --profile local down

2. Chạy UI Next dev thật để test giao diện
   Terminal 1: bật DB + backend.

export TICKETING_QR_SIGNING_SECRET=local-dev-secret-change-me
docker compose up postgres

Terminal 2:

cd backend
SPRING_PROFILES_ACTIVE=local \
 SPRING_DATASOURCE_URL=jdbc:postgresql://localhost:15432/ticket_mafia \
 SPRING_DATASOURCE_USERNAME=ticket_mafia \
 SPRING_DATASOURCE_PASSWORD=ticket_mafia \
 TICKETING_QR_SIGNING_SECRET=local-dev-secret-change-me \
 mvn spring-boot:run

Terminal 3: website.

cd website
npm install
npm run dev -- -p 3000

Mở:

- http://localhost:3000/login
- http://localhost:3000/matches
- http://localhost:3000/tickets
- http://localhost:3000/tickets/exchange

Terminal 4: admin.

cd admins
npm install
npm run dev -- -p 3001

Mở:

- http://localhost:3001/login
- http://localhost:3001/admin/matches
- http://localhost:3001/admin/confirmations

Lưu ý: website hiện gọi API bằng path tương đối /api/v1/... nhưng chưa thấy next.config rewrite sang backend 8080, nên chạy Next dev thật có
thể test UI, còn các flow gọi backend có khả năng lỗi API cho tới khi thêm proxy/rewrite. Admin hiện đang dùng mock service nội bộ nên test
màn hình admin được độc lập hơn.
