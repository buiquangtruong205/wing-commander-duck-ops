# 🦆 WING COMMANDER: DUCK OPS 🦆

**Wing Commander: Duck Ops** là một dự án game bắn vịt hiện đại, kết hợp giữa lối chơi cổ điển và công nghệ thị giác máy tính (Computer Vision) tiên tiến. Người chơi có thể điều khiển trò chơi bằng chuột truyền thống hoặc sử dụng cử chỉ tay (Hand Gestures) thông qua Camera.

---

## 🚀 Tính năng nổi bật

- 🎮 **Lối chơi Arcade kinh điển**: Bắn vịt, ghi điểm, combo và sử dụng tên lửa.
- 🤖 **Điều khiển bằng AI (Hand Tracking)**: Sử dụng MediaPipe và YOLO để nhận diện cử chỉ tay trong thời gian thực.
- ⚡ **Giao diện Cyberpunk**: Đồ họa Neon, hiệu ứng Lottie mượt mà và HUD phong cách kính mờ (Glassmorphism).
- 🏆 **Hệ thống bảng xếp hạng**: Lưu trữ điểm số và lịch sử chiến đấu qua Backend FastAPI.
- 🛠️ **Đa nền tảng**: Hỗ trợ phiên bản Web (Browser) và phiên bản Desktop (Pygame).

---

## 🛠️ Công nghệ sử dụng

### Backend (Python/FastAPI)
- **FastAPI**: Xử lý API và WebSocket truyền dữ liệu tracking.
- **MediaPipe/OpenCV**: Nhận diện bàn tay và xử lý hình ảnh từ Camera.
- **SQLite**: Lưu trữ thông tin người chơi và điểm số.

### Frontend (HTML/JS/CSS)
- **Vanilla JavaScript**: Logic game trên Canvas.
- **Lottie Files**: Hiệu ứng hoạt hình cho vịt và UI.
- **CSS3**: Thiết kế giao diện hiện đại với Animation và Glassmorphism.

### Standalone Version (Pygame)
- **Pygame**: Engine cho phiên bản Desktop với hiệu suất cao hơn.

---

## 📥 Cài đặt và Khởi chạy

### 1. Yêu cầu hệ thống
- Python 3.8 trở lên.
- Camera/Webcam (để sử dụng tính năng AI).

### 2. Cài đặt thư viện
```bash
pip install -r backend/requirements.txt
# Hoặc cài đặt thủ công:
pip install fastapi uvicorn opencv-python mediapipe numpy
```

### 3. Khởi chạy dự án
Bạn có thể chạy file script tự động:
- Chạy file `run_all.bat` trên Windows.

Hoặc chạy thủ công 2 phần:
- **Backend**: `cd backend && python -m uvicorn app.main:app --reload`
- **Frontend**: `cd frontend && python -m http.server 8080`

Sau đó truy cập: `http://localhost:8080/interface/index.html`

---

## 🎮 Hướng dẫn điều khiển

### 🖱️ Chế độ Chuột (Mặc định)
- **Di chuyển**: Di chuyển chuột để điều khiển tâm ngắm.
- **Bắn**: Nhấn chuột trái.
- **Tên lửa**: Nhấn phím `Space`.

### 🖐️ Chế độ AI (Hand Tracking)
*Bật tính năng này trong phần "Cài đặt" của game.*
- **Di chuyển**: Sử dụng **Ngón trỏ** (Index Finger) hướng vào camera để di chuyển tâm ngắm.
- **Bắn**: **Gập ngón trỏ** (Finger Curl) để khai hỏa.
- **Tên lửa**: Sử dụng **Dấu hiệu chữ V** (Index & Middle fingers extended) để phóng tên lửa.

---

## 📁 Cấu trúc thư mục

```text
wing-commander-duck-ops/
├── backend/                # Server FastAPI & Xử lý AI
│   ├── app/                # Logic ứng dụng (API, Services, Models)
│   └── game_data.db        # Cơ sở dữ liệu SQLite
├── frontend/               # Giao diện Web
│   ├── assets/             # Hình ảnh, âm thanh, animations
│   ├── duck/               # Logic game (game.js)
│   └── interface/          # Giao diện Menu & CSS
├── game_pygame.py          # Phiên bản game bằng Pygame
├── ai_controller.py        # Script điều khiển AI độc lập
├── run_all.bat             # File chạy nhanh dự án
└── README.md               # Tài liệu hướng dẫn
```

---

## 📜 Giấy phép
Dự án được phát triển bởi **Duck Ops Team**. Vui lòng giữ nguồn khi sử dụng.

---
*Chúc bạn có những giờ phút săn vịt vui vẻ, Chỉ huy!* 👮🫡
