# Đặc tả Yêu cầu Hệ thống (SRS) - Hệ thống Quản lý Siêu thị

## 1. Giới thiệu
Tài liệu này mô tả các chức năng của phần mềm **Quản lý Siêu thị** - ứng dụng giúp nhân viên thu ngân và quản lý cửa hàng thao tác bán hàng, kiểm soát kho và xem thống kê doanh thu.

## 2. Mô tả Tổng quan
* **Người dùng**: Nhân viên thu ngân (thao tác bán hàng) và Quản lý (xem thống kê, nhập xuất kho).
* **Môi trường**: Ứng dụng Desktop chạy offline trên Windows (không cần mạng Internet).

## 3. Yêu cầu Chức năng (Functional Requirements)

### FR1: Bán hàng (POS)
* Quản lý nhiều hóa đơn cùng lúc (tối đa 10 tab).
* Tìm kiếm sản phẩm theo mã vạch hoặc tên.
* Tự động tính tổng tiền, cho phép nhập chiết khấu, tính tiền khách đưa và tiền thối lại.
* In hoặc lưu hóa đơn khi hoàn tất thanh toán.

### FR2: Quản lý Kho hàng
* Hiển thị danh sách sản phẩm theo dạng bảng.
* Lọc sản phẩm theo danh mục hoặc trạng thái tồn kho (ví dụ: sắp hết hàng).
* Tính năng "Ghim (★)" để đánh dấu các sản phẩm quan trọng/bán chạy lên đầu.

### FR3: Import / Export Dữ liệu
* **Nhập file CSV**: Thêm hàng loạt sản phẩm vào kho từ file Excel (CSV).
* **Xuất file CSV**: Xuất dữ liệu kho hiện tại ra file CSV để báo cáo.

### FR4: Thống kê (Dashboard)
* Xem tổng số đơn hàng, doanh thu và giá vốn theo thời gian thực (Hôm nay, 7 ngày qua, Tháng này).
* Vẽ biểu đồ tròn (Pie chart) tỷ trọng doanh thu theo từng ngành hàng.
* Hiển thị chi tiết từng hóa đơn đã bán.

## 4. Yêu cầu Phi chức năng (NFR)
* **Kiến trúc**: Sử dụng chuẩn **MVC** (Model - View - Controller).
* **Giao diện**: Dùng thư viện `CustomTkinter` để tạo giao diện hiện đại, trực quan, các thành phần tự động co giãn (auto-resize).
* **Kiểm tra dữ liệu (Validation)**: Cảnh báo bằng Messagebox khi người dùng mở quá 10 tab hóa đơn, hoặc nhập sai số tiền, tìm kiếm sản phẩm không tồn tại.