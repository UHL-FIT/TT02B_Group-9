# SuperMarket POS - Hệ Thống Quản Lý Siêu Thị

SuperMarket POS là một ứng dụng Python chuyên dụng giúp quản lý quy trình bán hàng, kiểm soát kho vật tư và thống kê doanh thu siêu thị một cách trực quan, hiện đại. Phần mềm được xây dựng theo chuẩn kiến trúc MVC (Model-View-Controller) kết hợp giao diện CustomTkinter hiện đại.

**Lưu ý:** Đây là dự án Bài tập lớn môn Lập trình Python do **Nhóm 9** phát triển. Mọi tính năng nghiệp vụ cơ bản của một hệ thống POS (Point of Sale) đều được triển khai đầy đủ.

## 🌟 Tính năng nổi bật

* **Giao diện Hiện đại (GUI):** Thiết kế Dark/Light mode tối ưu trải nghiệm người dùng bằng CustomTkinter.
* **Bán hàng & Thanh toán (POS):** * Quản lý nhiều giỏ hàng (Tabs) cùng lúc (Hỗ trợ treo tối đa 10 hóa đơn).
  * Tìm kiếm sản phẩm thông minh, tính toán tiền thối, chiết khấu.
* **Quản lý Kho hàng:** * Hiển thị danh sách sản phẩm, lọc theo danh mục, trạng thái tồn kho.
  * Import/Export hàng loạt dữ liệu thông qua file `.csv`.
  * Tính năng "Ghim (★)" các sản phẩm quan trọng lên đầu danh sách.
* **Thống kê & Báo cáo:** * Biểu đồ trực quan (Pie chart) phân tích tỷ trọng ngành hàng.
  * Lọc doanh thu theo thời gian (Hôm nay, 7 ngày qua, Tháng này).
  * Xem chi tiết từng đơn hàng đã giao dịch.

## 📂 Cấu trúc Dự án

\`\`\`text
SuperMarket_Project/
├── controllers/             # Chứa logic điều khiển (main_controller, sale_controller,...)
├── data/                    # Nơi lưu trữ database (supermarket.db)
├── models/                  # Chứa logic tương tác cơ sở dữ liệu (database.py)
├── utils/                   # Các tiện ích hệ thống (logger.py)
├── views/                   # Giao diện người dùng (main_view, sale_view, inventory_view)
├── main.py                  # File khởi chạy ứng dụng chính
├── data_preset.csv          # Dữ liệu mẫu ban đầu để Import vào kho
├── requirements.txt         # Khai báo các thư viện Python phụ thuộc cần cài đặt
├── README.md                # Tài liệu hướng dẫn chính, tổng quan về dự án
└── .gitignore               # Cấu hình bỏ qua các file rác khi đẩy lên Git
\`\`\`

## 🚀 Hướng dẫn cài đặt và sử dụng

### 1. Khởi tạo môi trường ảo

Mở Terminal/Git Bash tại thư mục dự án và chạy các lệnh sau để tạo và kích hoạt môi trường ảo:

**Trên Windows:**
\`\`\`bash
python -m venv .venv
.venv\\Scripts\\activate
\`\`\`
**Trên macOS/Linux:**
\`\`\`bash
python3 -m venv .venv
source .venv/bin/activate
\`\`\`

### 2. Cài đặt thư viện (Dependencies)

Sau khi môi trường ảo đã được kích hoạt (có chữ `(.venv)` ở đầu dòng lệnh), tiến hành cài đặt các thư viện cần thiết:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 3. Chạy ứng dụng

Khởi động hệ thống quản lý bằng lệnh:
\`\`\`bash
python main.py
\`\`\`

---
*Phát triển bởi Nhóm 9 - Trường Đại học Hạ Long (UHL).*