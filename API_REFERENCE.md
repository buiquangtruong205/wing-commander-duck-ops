# API REFERENCE: DUCK OPS BACKEND

Tài liệu này liệt kê các điểm cuối (endpoints) của API backend được sử dụng để quản lý thông tin người chơi, cấu hình và điểm số.

---

## 🏗️ Base URL
Mặc định: `http://localhost:8000/db`

---

## 👤 1. Quản lý Người chơi (Players)

### Đăng nhập hoặc Tạo mới
- **Endpoint**: `POST /players/`
- **Body**:
  ```json
  { "username": "TenNguoiChoi" }
  ```
- **Mô tả**: Trả về thông tin người chơi hiện có hoặc tạo mới nếu chưa tồn tại.

### Lấy thông tin người chơi
- **Endpoint**: `GET /players/{username}`
- **Mô tả**: Lấy thông tin chi tiết của một chỉ huy cụ thể.

---

## ⚙️ 2. Cấu hình (Settings)

### Lấy cấu hình
- **Endpoint**: `GET /players/{username}/settings`
- **Mô tả**: Lấy các cài đặt đã lưu (âm lượng, độ nhạy, chế độ AI, v.v.).

### Cập nhật cấu hình
- **Endpoint**: `PUT /players/{username}/settings`
- **Body**:
  ```json
  {
    "music_volume": 50,
    "sfx_volume": 80,
    "camera_index": 0,
    "flip_camera": true,
    "hand_mode": true
  }
  ```

---

## 🏆 3. Điểm số (Scores)

### Lấy danh sách điểm cao
- **Endpoint**: `GET /players/{username}/scores`
- **Mô tả**: Trả về danh sách các mức điểm cao nhất theo từng độ khó của người chơi.

### Cập nhật điểm số mới
- **Endpoint**: `POST /players/{username}/scores`
- **Body**:
  ```json
  {
    "difficulty": "hard",
    "highest_score": 1500
  }
  ```
- **Mô tả**: Hệ thống sẽ tự động so sánh và cập nhật nếu điểm mới cao hơn điểm cũ trong cơ sở dữ liệu.

---

## 📡 4. Real-time Tracking (WebSocket)

- **URL**: `ws://localhost:8000/ws/tracking`
- **Mô tả**: Nhận frame hình ảnh (Base64) và trả về dữ liệu tọa độ bàn tay trong thời gian thực.

---
*Tài liệu API phiên bản 1.0*
