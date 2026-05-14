# Tổng quan project Wing Commander: Duck Ops

## 1. Mục tiêu project

**Wing Commander: Duck Ops** là game bắn vịt chạy bằng Python/Pygame, kết hợp điều khiển truyền thống bằng chuột và điều khiển bằng cử chỉ tay qua webcam. Người chơi dùng đầu ngón trỏ để di chuyển tâm ngắm, gập ngón trỏ để bắn, và dùng dấu hiệu chữ V để phóng tên lửa.

Project hiện tại tập trung vào bản desktop:

- `main.py`: entrypoint mỏng, chỉ dùng để khởi chạy game.
- `game_controller.py`: controller chính, chứa class `DuckOpsGame`, cấu trúc state và logic điều khiển.
- `backend/`: xử lý database, game object, hand tracking.
- `frontend/`: quản lý asset và vẽ UI bằng Pygame.
- `frontend/images/`, `frontend/sounds/`: tài nguyên hình ảnh và âm thanh.
- `scratch/`: script thử nghiệm/xử lý ảnh, kiểm tra sprite và database.
- `duck_ops.db`: SQLite database lưu người chơi, cài đặt và điểm cao.

## 2. Công nghệ sử dụng

- **Python**: ngôn ngữ chính.
- **Pygame**: vòng lặp game, sprite, UI, âm thanh, render màn hình.
- **OpenCV (`cv2`)**: đọc webcam, lật ảnh, resize preview camera, chuyển đổi màu.
- **MediaPipe Hands**: nhận diện bàn tay và 21 landmark.
- **SQLite**: lưu profile người chơi, cài đặt và bảng điểm.
- **NumPy**: chuyển frame camera thành surface Pygame.

Các package cần có khi chạy game:

```bash
pip install pygame opencv-python mediapipe numpy
```

## 3. Cách chạy

Từ thư mục gốc project:

```bash
python main.py
```

Yêu cầu:

- Máy có webcam nếu muốn dùng điều khiển bằng tay.
- Python đã cài các thư viện ở trên.
- Chạy ở môi trường có thể mở cửa sổ Pygame.

## 4. Luồng hoạt động chính

File `main.py` chỉ gọi `DuckOpsGame` từ `game_controller.py`. File `game_controller.py` tạo class `DuckOpsGame`, khởi tạo toàn bộ hệ thống:

1. Khởi tạo Pygame, mixer âm thanh, màn hình 1280x720.
2. Khởi tạo `DatabaseManager` để đọc/tạo database.
3. Load ảnh, âm thanh và font qua `AssetsManager`.
4. Tạo UI button/input/slider/toggle.
5. Mở webcam bằng `cv2.VideoCapture(0)`.
6. Khởi tạo `HandTracker`.
7. Chạy vòng lặp chính `run()`.

Trong mỗi frame:

1. Đọc frame từ webcam.
2. Lật camera nếu bật `flip_camera`.
3. Đưa frame vào MediaPipe để lấy vị trí tay.
4. Chuyển landmark đầu ngón trỏ thành tọa độ màn hình.
5. Nhận diện gesture bắn/tên lửa.
6. Xử lý input Pygame từ chuột/bàn phím.
7. Nếu đang chơi, cập nhật logic vịt, boss, feather, particle, điểm số.
8. Vẽ màn hình tương ứng với state hiện tại.
9. Hiển thị preview camera nhỏ ở góc màn hình.

## 5. Các state màn hình

Game dùng biến `self.state` trong `game_controller.py` để điều hướng:

| State | Vai trò |
|---|---|
| `LOGIN` | Nhập tên người chơi |
| `HOME` | Menu chính |
| `PLAY_SELECT` | Chọn chế độ chơi |
| `STORY` | Màn hình briefing/cốt truyện |
| `PLAYING` | Gameplay chính |
| `SETTINGS` | Cài đặt âm lượng, camera, fullscreen, độ nhạy |
| `LEADERBOARD` | Bảng điểm |
| `TUTORIAL` | Hướng dẫn chơi |
| `ABOUT` | Thông tin project |
| `GAMEOVER` | Kết thúc game |

## 6. Chế độ chơi

### QUICK

- Thời lượng 60 giây.
- Người chơi bắn càng nhiều vịt càng tốt.
- Hết giờ thì kết thúc và lưu điểm.

### CHALLENGE

- Mỗi level có 30 giây.
- Người chơi cần đạt `target_score`.
- Sau mỗi level có boss.
- Khi boss chết, người chơi được cộng điểm lớn và lên level.
- Độ khó tăng theo level: nhiều vịt hơn, tốc độ cao hơn, target score tăng.

### ENDLESS

- Không giới hạn thời gian.
- Người chơi có 3 mạng.
- Vịt thoát khỏi màn hình sẽ trừ mạng.
- Hết mạng thì game over.

## 7. Điều khiển bằng tay

Module `backend/hand_tracker.py` dùng MediaPipe Hands:

- Landmark 8: đầu ngón trỏ, dùng làm vị trí tâm ngắm.
- Bắn: nếu đầu ngón trỏ thấp hơn khớp DIP/PIP, coi như ngón tay đang gập.
- Tên lửa: ngón trỏ và ngón giữa duỗi lên, ngón áp út và út gập xuống, khoảng cách giữa hai đầu ngón đủ rộng.

Trong `game_controller.py`, tọa độ tay được làm mượt bằng lerp:

```python
self.hand_x += (hand_pos[0] - self.hand_x) * actual_lerp
self.hand_y += (hand_pos[1] - self.hand_y) * actual_lerp
```

`tracking_sensitivity` trong settings ảnh hưởng tới tốc độ bám của tâm ngắm.

## 8. Gameplay object

Các object chính nằm trong `backend/game_logic.py`:

- `Duck`: vịt thường, vịt nhanh, vịt zigzag, vịt elite.
- `Boss`: kế thừa `Duck`, máu lớn hơn, di chuyển ở phía trên màn hình, bắn feather.
- `Feather`: vật thể boss thả xuống, chạm đáy sẽ tạo nhiễu camera.
- `Crosshair`: tâm ngắm.
- `Particle`: hiệu ứng nổ khi bắn trúng.

Điểm theo loại vịt trong `game_controller.py`:

| Loại vịt | Điểm |
|---|---:|
| `normal` | 10 |
| `fast` | 25 |
| `zigzag` | 50 |
| `elite` | 100 |

Tên lửa gây sát thương diện rộng nhưng điểm mỗi vịt thấp hơn bắn thường.

## 9. Database

Module `backend/database.py` quản lý SQLite database `duck_ops.db`.

Các bảng chính:

### `PlayerProfile`

| Cột | Ý nghĩa |
|---|---|
| `username` | Khóa chính, tên người chơi |
| `create_at` | Thời điểm tạo profile |

### `HighScores`

| Cột | Ý nghĩa |
|---|---|
| `id` | Khóa tự tăng |
| `username` | Người chơi |
| `difficulty` | Chế độ chơi |
| `highest_score` | Điểm cao nhất |
| `achieved_date` | Thời điểm đạt điểm |

### `PlayerSetting`

| Cột | Ý nghĩa |
|---|---|
| `music_volume` | Âm lượng ambient/flying |
| `sfx_volume` | Âm lượng hiệu ứng |
| `is_fullscreen` | Bật/tắt fullscreen |
| `camera_index` | Index camera, hiện chưa được dùng đầy đủ trong `game_controller.py` |
| `flip_camera` | Lật camera kiểu gương |
| `tracking_sensitivity` | Độ nhạy bám tay |

### `Meta`

Lưu dữ liệu nhỏ dạng key/value, hiện dùng để nhớ `last_user`.

## 10. UI và asset

### `frontend/assets_manager.py`

Chịu trách nhiệm:

- Load background menu và background theo level.
- Load sprite vịt thường và vịt vàng/elite.
- Load sound: bắn, trúng vịt, nổ, flying ambient.
- Chọn font hệ thống.
- Áp dụng âm lượng cho từng nhóm âm thanh.

### `frontend/ui_system.py`

Chứa:

- `UIButton`
- `UIInputField`
- `UISlider`
- `UIToggle`
- `UISystem`

`UISystem` vẽ các màn hình:

- Login
- Home
- Chọn mode
- Story
- Settings
- Leaderboard
- Tutorial
- About
- Hiệu ứng camera noise

## 11. Tài nguyên hình ảnh và âm thanh

Hình ảnh chính:

- `frontend/images/backgroudHome.png`: background menu.
- `frontend/images/anh1.png`, `anh2.png`, `anh3.png`: background level.
- `frontend/images/duck_sprite.png`: sprite vịt thường.
- `frontend/images/yellow_duck_spritesheet.png`: sprite vịt elite/boss.
- Các file duck khác là asset bổ sung/backup/thử nghiệm.

Âm thanh:

- `gunshot.wav`: tiếng bắn.
- `duck_hit.wav`: trúng vịt.
- `explosion.wav`: nổ/game over.
- `flying.wav`: âm thanh nền khi gameplay.

## 12. Thư mục scratch

`scratch/` chứa các script phụ, không phải luồng runtime chính:

- Kiểm tra kích thước, transparency, frame của sprite.
- Xử lý/cắt nền ảnh vịt vàng.
- Xóa viền và kiểm tra frame loading.
- Một số script kiểm tra database hoặc logic vịt.

Các file tiêu biểu:

- `clean_duck.py`: xóa nền trắng và crop sprite vịt vàng.
- `remove_borders.py`: xóa viền trong từng frame sprite.
- `test_duck_logic.py`: kiểm tra class `Duck`.
- `verify_fix.py`: kiểm tra sprite vịt vàng load đúng 4 frame.

## 13. Điểm cần lưu ý

1. Một số tài liệu và chuỗi hiển thị tiếng Việt trong code đang bị lỗi encoding/mojibake, ví dụ `ChÆ¡i`, `CÃ i Ä‘áº·t`. Nên chuyển các file sang UTF-8 đúng để UI hiển thị đẹp.
2. `README.md`, `TECHNICAL_DOC.md`, `API_REFERENCE.md` còn mô tả kiến trúc web/FastAPI/WebSocket, nhưng trong cây code hiện tại không thấy app FastAPI đầy đủ. Tài liệu này phản ánh code thực tế đang có trong repo.
3. `camera_index` có trong database settings nhưng `game_controller.py` đang hard-code `cv2.VideoCapture(0)`.
4. Asset manager đang load `frontend/images/nature_bg.png`, nhưng file này không xuất hiện trong danh sách file hiện tại. Code có fallback surface nên game không crash, nhưng nên kiểm tra lại asset thiếu.
5. `git status` bị chặn bởi Git safe directory vì khác owner trong sandbox. Đây không phải lỗi code game.

## 14. Gợi ý cải thiện tiếp theo

- Sửa encoding toàn bộ file `.py` và `.md` sang UTF-8.
- Đồng bộ lại README với kiến trúc desktop hiện tại.
- Cho phép chọn camera bằng `camera_index` trong settings.
- Thêm `requirements.txt`.
- Tách nhỏ thêm state machine/menu input trong `game_controller.py` thành các module riêng để dễ bảo trì.
- Thêm test nhẹ cho database và gesture logic.
- Bổ sung xử lý khi webcam không mở được.
