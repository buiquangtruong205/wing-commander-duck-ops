# Phân Tích Phương Pháp và Thuật Toán Xử Lý Ảnh - Wing Commander: Duck Ops

Tài liệu này phân tích chi tiết các kỹ thuật xử lý ảnh và thuật toán được sử dụng trong dự án để điều khiển game bằng cử chỉ tay và quản lý tài nguyên đồ họa.

## 1. Xử Lý Ảnh Từ Camera (Real-time Computer Vision)

Dự án sử dụng Camera làm thiết bị đầu vào chính, thay thế cho chuột và bàn phím truyền thống. Quy trình xử lý bao gồm các bước sau:

### 1.1. Thư viện sử dụng
- **OpenCV (cv2):** Sử dụng để thu thập luồng dữ liệu từ webcam, lật ảnh (mirroring), thay đổi kích thước (resizing) và chuyển đổi không gian màu.
- **MediaPipe:** Giải pháp của Google được sử dụng để phát hiện và theo dõi các điểm mốc (landmarks) trên bàn tay.

### 1.2. Thuật toán Hand Tracking
Dự án sử dụng module **MediaPipe Hands**, dựa trên một pipeline học máy (Machine Learning) phức tạp:
- **BlazePalm Detector:** Một mô hình phát hiện lòng bàn tay hoạt động trên toàn bộ khung hình để xác định vị trí sơ bộ của bàn tay.
- **Hand Landmark Model:** Sau khi phát hiện lòng bàn tay, mô hình này sẽ xác định **21 điểm mốc 3D** (landmarks) trên bàn tay.

### 1.3. Quy trình xử lý khung hình (Frame Processing Pipeline)
1. **Capture:** Đọc khung hình từ `cv2.VideoCapture`.
2. **Mirroring:** Sử dụng `cv2.flip(frame, 1)` để người chơi cảm thấy tự nhiên (di chuyển tay phải thì tâm ngắm sang phải).
3. **Color Conversion:** Chuyển đổi từ BGR (OpenCV default) sang RGB (MediaPipe requirement).
4. **Inference:** Đưa ảnh vào mô hình MediaPipe để lấy tọa độ các điểm mốc.
5. **Coordinate Mapping:** Ánh xạ tọa độ chuẩn hóa (0.0 - 1.0) của điểm mốc số 8 (đầu ngón trỏ) sang tọa độ pixel của màn hình game (1280x720).

### 1.4. Thuật toán nhận diện cử chỉ (Gesture Logic)
Dự án không sử dụng các mô hình phân loại cử chỉ phức tạp mà sử dụng **logic hình học** dựa trên vị trí tương đối của các điểm mốc:
- **Bắn (Shoot):** So sánh tọa độ Y của đầu ngón trỏ (Landmark 8) và khớp ngón trỏ (Landmark 6). Nếu `Y_tip > Y_pip`, nghĩa là ngón tay đang gập lại, hệ thống ghi nhận lệnh bắn.
- **Phóng tên lửa (Rocket):** Kiểm tra tư thế chữ "V" (Ngón trỏ và ngón giữa hướng lên, các ngón khác gập lại).
- **Di chuyển:** Tọa độ của đầu ngón trỏ được sử dụng trực tiếp để cập nhật vị trí của tâm ngắm (Crosshair).

---

## 2. Xử Lý Hình Ảnh Tài Nguyên (Static Image Processing)

Ngoài việc xử lý camera, dự án còn áp dụng các kỹ thuật xử lý ảnh để tối ưu hóa đồ họa game:

### 2.1. Xử lý Sprite Sheet
Các tệp ảnh như `duck_spritesheet.png` chứa nhiều khung hình hoạt họa.
- **Phân tách khung hình:** Sử dụng thuật toán cắt ảnh theo lưới để trích xuất từng frame (ví dụ: 4 frames cho hành động đập cánh).
- **Xử lý nền (Background Removal):** Sử dụng OpenCV để lọc bỏ màu nền (thường là màu xanh lá hoặc màu đồng nhất) thông qua kỹ thuật **Color Thresholding** hoặc sử dụng kênh Alpha để tạo độ trong suốt.

### 2.2. Hiệu ứng hạt (Particle System)
Khi vịt bị bắn trúng, hệ thống tạo ra các hạt (Particles). Đây là sự kết hợp giữa xử lý ảnh và toán học:
- Mỗi hạt là một Surface nhỏ của Pygame.
- Thuật toán di chuyển ngẫu nhiên và giảm độ sáng (fading) theo thời gian để tạo hiệu ứng nổ.

### 2.3. Tối ưu hóa hiển thị
- **Scaling:** Sử dụng thuật toán nội suy của Pygame/OpenCV để thay đổi kích thước ảnh mà không làm mất quá nhiều chi tiết.
- **Double Buffering:** Kỹ thuật vẽ lên một buffer trung gian trước khi hiển thị lên màn hình để tránh hiện tượng nháy ảnh (flickering).

## 3. Tổng kết thuật toán chính

| Tính năng | Thuật toán / Phương pháp | Thư viện |
| :--- | :--- | :--- |
| Phát hiện bàn tay | BlazePalm + Landmark Model | MediaPipe |
| Theo dõi vị trí | Linear Coordinate Mapping | NumPy / Python |
| Nhận diện bắn | Geometric Heuristics (Y-coord comparison) | Python |
| Hoạt họa vịt | Sprite Sheet Slicing | Pygame |
| Hiệu ứng nổ | Particle Physics Simulation | Pygame |
| Tiền xử lý camera | Affine Transform (Flip/Resize) | OpenCV |
