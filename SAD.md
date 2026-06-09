# Tài liệu Kiến trúc Phần mềm (SAD) - Hệ thống Quản lý Siêu thị

## 1. Giới thiệu
Tài liệu này phác thảo mô hình tổ chức source code và luồng dữ liệu của phần mềm Quản lý Siêu thị.

## 2. Kiến trúc Tổng thể
Phần mềm áp dụng chặt chẽ mô hình **MVC**:
* **Model**: Quản lý dữ liệu bằng CSDL **SQLite3** (`supermarket.db`). Kết hợp thư viện **Pandas** để xử lý đọc/ghi file CSV khi xuất nhập kho nhanh chóng.
* **View**: Giao diện xây dựng hoàn toàn bằng **CustomTkinter** thay vì Tkinter cũ để mang lại trải nghiệm UI hiện đại. Sử dụng cấu trúc Frame lồng nhau để chuyển đổi giữa các màn hình (Bán hàng, Kho, Thống kê) mà không cần mở nhiều cửa sổ lộn xộn.
* **Controller**: Viết bằng Python, làm nhiệm vụ nhận tương tác từ View, gọi Model để truy vấn SQLite, và render kết quả lên lại View.

## 3. Cấu trúc Source Code
```text
Supermarket/
├── assets/
    ├── data_preset/data_preset.csv  # File mẫu để người dùng import vào kho.
    ├── img                  # Chứa hình ảnh của sản phẩm
├── data/                    # Nơi chứa file database SQLite (supermarket.db) và log.
├── models/
│   └── database.py          # Model: Chứa các lệnh SQL (CRUD), logic import/export CSV bằng Pandas.
├── views/
│   ├── main_view.py         # Giao diện khung chính (Thanh topbar, Menu thả xuống).
│   ├── sale_view.py         # Giao diện tab bán hàng.
│   ├── inventory_view.py    # Giao diện bảng kho hàng.
│   └── stats_view.py        # Giao diện bảng thống kê và biểu đồ Matplotlib.
├── controllers/
│   ├── main_controller.py   # Controller điều hướng các màn hình.
│   ├── sale_controller.py   # Controller xử lý tính tiền, giỏ hàng.
│   ├── inventory_controller.py # Controller quản lý lọc, tìm kiếm kho.
│   └── stats_controller.py  # Controller tính toán KPI, hiển thị biểu đồ.
├── utils/
│   └── logger.py            # Hỗ trợ ghi lại lịch sử lỗi hệ thống ra file log.
├── main.py                  # File khởi chạy duy nhất.
```

## 4. Công nghệ sử dụng
* **Ngôn ngữ**: Python 3.9+
* **Cơ sở dữ liệu**: `sqlite3` (nhẹ, tích hợp sẵn, phù hợp ứng dụng Desktop offline).
* **Giao diện**: `customtkinter`.
* **Phân tích & Biểu đồ**: `pandas` (xử lý dataframe từ CSV) và `matplotlib` (vẽ biểu đồ tròn doanh thu).

## 5. Luồng dữ liệu (Ví dụ: Thao tác Thanh toán)
1. **View (`sale_view.py`)**: Thu ngân ấn nút "Thanh toán". Dữ liệu (tổng tiền, tiền khách đưa, danh sách món hàng) được đẩy sang `sale_controller`.
2. **Controller (`sale_controller.py`)**: Kiểm tra (validate) xem tiền khách đưa có đủ không. Nếu đủ, gọi hàm `process_sale()` bên Database.
3. **Model (`database.py`)**: Mở transaction SQLite -> Trừ số lượng tồn kho trong bảng `Products` -> Lưu hóa đơn vào bảng `Sales` -> Lưu chi tiết món hàng vào `Sale_Details` -> Commit (Lưu lại).
4. **Model -> Controller**: Trả về kết quả Thành công.
5. **Controller -> View**: Hiển thị popup "Thanh toán thành công", reset tab hóa đơn về trống.