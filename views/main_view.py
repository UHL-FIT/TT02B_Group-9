import customtkinter as ctk

class MainView:
    def __init__(self, root):
        self.root = root

        # --- 1. THANH TOPBAR (Màu xanh biển đậm) ---
        self.topbar = ctk.CTkFrame(self.root, height=60, corner_radius=0, fg_color="#003366")
        self.topbar.pack(side="top", fill="x")

        # Nút 3 gạch ngang
        self.btn_menu = ctk.CTkButton(self.topbar, text="☰", width=40, font=("Arial", 24), 
                                       fg_color="transparent", hover_color="#00509e")
        self.btn_menu.pack(side="right", padx=10, pady=5)

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
        """Hiển thị menu dạng thả xuống"""
        if self.menu_visible:
            self.dropdown_menu.place_forget()
            self.menu_visible = False
        else:
            # Đặt menu ngay dưới thanh topbar (y=60)
            self.dropdown_menu.place(relx=1.0, x=-10, y=60, anchor="ne")
            self.dropdown_menu.lift() # Đưa lên lớp trên cùng
            self.menu_visible = True