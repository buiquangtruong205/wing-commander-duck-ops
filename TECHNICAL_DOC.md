# TECHNICAL DOCUMENTATION: DUCK OPS AI ARCHITECTURE

Tài liệu này giải thích chi tiết về cách thức hoạt động của hệ thống AI và sự tương tác giữa Backend - Frontend trong Wing Commander: Duck Ops.

---

## 🧠 1. Hệ thống AI Tracking (Mediapipe)

Dự án sử dụng **MediaPipe Hands** để nhận diện 21 điểm mốc (landmarks) trên bàn tay.

### Các Logic chính:
1.  **Tọa độ Tâm ngắm (Crosshair)**:
    - Được lấy từ tọa độ của **Landmark 8** (Index Finger Tip).
    - Tọa độ này được chuẩn hóa (0.0 đến 1.0) và gửi qua WebSocket.
2.  **Phát hiện Bắn (Shoot Detection)**:
    - So sánh tọa độ Y của **Landmark 8** (Index Tip) và **Landmark 6** (Index PIP).
    - Nếu `Tip.y > PIP.y` (Ngón trỏ gập xuống), hệ thống ghi nhận một sự kiện `trigger`.
3.  **Phát hiện Tên lửa (Rocket Detection)**:
    - Kiểm tra nếu Ngón trỏ và Ngón giữa (Landmark 8 & 12) duỗi thẳng, trong khi các ngón khác gập lại (V-Sign).
    - Yêu cầu khoảng thời gian hồi chiêu (cooldown) là 1.5 giây.

---

## 📡 2. Giao tiếp WebSocket

Luồng dữ liệu giữa Frontend và Backend diễn ra theo chu kỳ:
1.  **Frontend**: Capture frame từ Webcam -> Convert sang Base64/JPEG -> Gửi qua WebSocket `/ws/tracking`.
2.  **Backend**: Nhận ảnh -> Xử lý qua MediaPipe -> Trả về JSON chứa tọa độ và trạng thái trigger.
3.  **JSON Response Format**:
    ```json
    {
      "detected": true,
      "x": 0.52,
      "y": 0.48,
      "trigger": false,
      "rocket": false
    }
    ```

---

## 🗄️ 3. Cơ sở dữ liệu (Database Schema)

Sử dụng SQLite với 2 bảng chính:

### Bảng `players`
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Primary Key |
| `username` | TEXT | Tên định danh (Unique) |
| `created_at` | DATETIME | Ngày tham gia |

### Bảng `scores`
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Primary Key |
| `player_id` | INTEGER | Liên kết tới bảng players |
| `score` | INTEGER | Điểm số đạt được |
| `difficulty` | TEXT | Độ khó (easy, medium, hard) |
| `recorded_at` | DATETIME | Thời điểm ghi nhận |

---

## 🎮 4. Game Engine (Canvas 2D)

- Game chạy trên vòng lặp `requestAnimationFrame`.
- Sử dụng **Lottie-web** để render các animation của vịt, giúp giảm tải cho CPU so với việc sử dụng quá nhiều Spritesheets.
- Hệ thống hạt (Particle System) được viết tùy chỉnh để xử lý hiệu ứng cháy nổ và điểm số bay lên.

---

## 🛠️ 5. Performance Optimization

- **Downscaling**: Ảnh gửi lên Server được giảm độ phân giải xuống 320x240 để giảm độ trễ (latency).
- **Smoothing (Lerp)**: Sử dụng Linear Interpolation trên Frontend để làm mượt chuyển động của tâm ngắm, tránh tình trạng bị giật (jitter) do nhiễu từ camera.
- **Async Processing**: Backend xử lý ảnh trong các hàm `async` để không chặn (block) các kết nối khác.

---
*Tài liệu kỹ thuật phiên bản 1.2 - 2026*
