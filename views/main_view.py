import customtkinter as ctk

class MainView:
    def __init__(self, root):
        self.root = root

        # --- 1. THANH TOPBAR (Màu xanh biển đậm) ---
        self.topbar = ctk.CTkFrame(self.root, height=60, corner_radius=0, fg_color="#003366")
        self.topbar.pack(side="top", fill="x")

        # Nút 3 gạch ngang (Bên phải ngoài cùng) - Đã thêm kích hoạt toggle_menu
        self.btn_menu = ctk.CTkButton(self.topbar, text="☰", width=40, font=("Arial", 24), 
                                       fg_color="transparent", hover_color="#00509e",
                                       command=self.toggle_menu)
        self.btn_menu.pack(side="right", padx=10, pady=5)

        # NÚT GIỚI THIỆU (Nằm cạnh nút 3 gạch ngang)
        self.btn_about = ctk.CTkButton(self.topbar, text="✦  Giới thiệu", font=("Arial", 14, "bold"), 
                                       fg_color="transparent", hover_color="#00509e", 
                                       command=self.show_about_dialog)
        self.btn_about.pack(side="right", padx=5, pady=5)

        # Tiêu đề hệ thống bên trái
        ctk.CTkLabel(self.topbar, text="HỆ THỐNG SIÊU THỊ", font=("Arial", 18, "bold"), text_color="white").pack(side="left", padx=10)

        # --- 2. KHU VỰC BODY ---
        self.body_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.body_frame.pack(side="top", fill="both", expand=True)

        self.content_area = ctk.CTkFrame(self.body_frame, fg_color="transparent")
        self.content_area.pack(fill="both", expand=True, padx=10, pady=10)

        # --- 3. DROPDOWN MENU (Chỉ sổ xuống khi bấm) ---
        self.dropdown_menu = ctk.CTkFrame(self.root, width=200, corner_radius=5, 
                                          fg_color="#1a2b3c", border_width=1, border_color="gray")
        
        self.btn_sales = ctk.CTkButton(self.dropdown_menu, text="🛒 Bán Hàng", fg_color="transparent", anchor="w", font=("Arial", 13))
        self.btn_sales.pack(fill="x", pady=5, padx=10)
        self.btn_inventory = ctk.CTkButton(self.dropdown_menu, text="📦 Kho Hàng", fg_color="transparent", anchor="w", font=("Arial", 13))
        self.btn_inventory.pack(fill="x", pady=5, padx=10)
        self.btn_stats = ctk.CTkButton(self.dropdown_menu, text="📊 Thống Kê", fg_color="transparent", anchor="w", font=("Arial", 13))
        self.btn_stats.pack(fill="x", pady=5, padx=10)

        self.menu_visible = False

    def toggle_menu(self):
        """Hiển thị hoặc ẩn Dropdown Menu bằng tọa độ tương đối an toàn"""
        if self.menu_visible:
            self.dropdown_menu.place_forget()
            self.menu_visible = False
        else:
            # Neo menu vào góc trên bên phải (anchor="ne"), cách lề phải 10px, dưới topbar (y=60)
            self.dropdown_menu.place(relx=1.0, x=-10, y=60, anchor="ne")
            self.dropdown_menu.lift()  # Đưa lên lớp trên cùng để không bị che khuất
            self.menu_visible = True

    # =======================================================
    # POPUP GIỚI THIỆU PHẦN MỀM
    # =======================================================
    def show_about_dialog(self):
        about_window = ctk.CTkToplevel(self.root)
        about_window.title("Giới thiệu Phần mềm")
        about_window.geometry("420x400")
        
        # Khóa tương tác với cửa sổ chính cho đến khi tắt popup
        about_window.grab_set() 
        about_window.resizable(False, False)
        # Ép cửa sổ nổi lên trên cùng
        about_window.attributes("-topmost", True) 

        # 1. Tiêu đề
        lbl_title = ctk.CTkLabel(about_window, text="THÔNG TIN PHẦN MỀM", font=("Arial", 20, "bold"), text_color="#1abc9c")
        lbl_title.pack(pady=(25, 20))

        # 2. Khung chứa chi tiết
        info_frame = ctk.CTkFrame(about_window, fg_color="transparent")
        info_frame.pack(fill="x", padx=40)

        details = [
            ("Phần mềm:", "Hệ thống quản lí siêu thị"),
            ("Phiên bản:", "1.0.0"),
            ("Tác giả:", "Nhóm 9"),
            ("Đơn vị:", "Trường Đại học Hạ Long (UHL)"),
            ("Ngày phát hành:", "06/05/2026")
        ]

        for label, value in details:
            row = ctk.CTkFrame(info_frame, fg_color="transparent")
            row.pack(fill="x", pady=6)
            # Cột Label
            ctk.CTkLabel(row, text=label, font=("Arial", 14, "bold"), width=130, anchor="w").pack(side="left")
            # Cột Giá trị
            ctk.CTkLabel(row, text=value, font=("Arial", 14), anchor="w").pack(side="left")

        # 3. Dòng kẻ ngang phân cách
        divider = ctk.CTkFrame(about_window, height=2, fg_color="#555555")
        divider.pack(fill="x", padx=40, pady=(20, 15))

        # 4. Mô tả ngắn gọn
        desc_text = "Phần mềm hỗ trợ quản lý bán hàng, theo dõi kho và thống kê doanh thu toàn diện. Giúp tự động hóa quy trình nghiệp vụ và tiết kiệm tối đa thời gian vận hành cửa hàng."
        lbl_desc = ctk.CTkLabel(about_window, text=desc_text, font=("Arial", 13, "italic"),
                                wraplength=340, justify="center", text_color="#aaaaaa")
        lbl_desc.pack(pady=(0, 20))
