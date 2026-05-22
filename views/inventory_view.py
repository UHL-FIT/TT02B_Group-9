from customtkinter import windows
import customtkinter as ctk
from tkinter import ttk, filedialog
import os
from PIL import Image, ImageTk

class InventoryView(ctk.CTkFrame):
    def __init__(self, master, controller):
        # Đổi nền frame chính thành màu tối
        super().__init__(master, fg_color="#1a1a1a")
        self.controller = controller
        self.all_checked = False
        self.image_refs = []
        self.setup_ui()

    def setup_ui(self):
        # --- BỘ LỌC & TÌM KIẾM ---
        search_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#2b2b2b")
        search_frame.pack(fill="x", padx=20, pady=(0, 15), ipady=5)

        # GOM TẤT CẢ VỀ BÊN TRÁI THEO ĐÚNG THỨ TỰ YÊU CẦU:
        
        # 1. Thanh tìm kiếm (Có gợi ý mờ)
        self.entry_search = ctk.CTkEntry(search_frame, placeholder_text="🔍 Nhập mã hoặc tên hàng (F3)...", 
                                         font=("Arial", 14), width=280, corner_radius=8, 
                                         border_width=1, fg_color="#333333", text_color="white", border_color="#555555")
        self.entry_search.pack(side="left", padx=(15, 5), pady=10)
        
        # Đăng ký phím tắt F3 toàn màn hình để focus vào ô tìm kiếm
        self.winfo_toplevel().bind("<F3>", lambda event: self.entry_search.focus())

        # 2. Nút Tìm kiếm
        btn_search = ctk.CTkButton(search_frame, text="🔍 Tìm kiếm", font=("Arial", 13, "bold"), 
                                   width=100, corner_radius=8, fg_color="#1d4ed8", hover_color="#1e3a8a",
                                   command=self.controller.search_data)
        btn_search.pack(side="left", padx=5, pady=10)

        # 3. Nút Làm mới
        btn_refresh = ctk.CTkButton(search_frame, text="🔄 Làm mới", font=("Arial", 13, "bold"), 
                                    width=100, fg_color="#d97706", hover_color="#b45309", corner_radius=8, 
                                    command=self.controller.load_data)
        btn_refresh.pack(side="left", padx=5, pady=10)

        # 4. Bộ lọc danh mục
        self.cb_category = ctk.CTkComboBox(search_frame, values=["Tất cả danh mục"], font=("Segoe UI", 13), 
                                           width=160, command=self.controller.apply_filters)
        self.cb_category.set("Tất cả danh mục")
        self.cb_category.pack(side="left", padx=5, pady=10)

        # 5. Bộ lọc trạng thái
        self.cb_stock = ctk.CTkComboBox(search_frame, values=["Tất cả trạng thái", "Còn hàng", "Sắp hết (<=10)"], 
                                        font=("Segoe UI", 13), width=160, command=self.controller.apply_filters)
        self.cb_stock.set("Tất cả trạng thái")
        self.cb_stock.pack(side="left", padx=(5, 15), pady=10)
        
        # --- NÚT CHỨC NĂNG (Dưới cùng) ---
        action_frame = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=10)
        action_frame.pack(side="bottom", fill="x", padx=20, pady=(0, 20), ipady=5)

        btn_font = ("Arial", 13, "bold")
        
        ctk.CTkButton(action_frame, text="➕ Thêm Mới", font=btn_font, fg_color="#16a34a", hover_color="#15803d", 
                      command=self.controller.handle_add).pack(side="left", padx=(10, 5), pady=10, expand=True, fill="x")
        ctk.CTkButton(action_frame, text="✏️ Sửa", font=btn_font, fg_color="#2563eb", hover_color="#1d4ed8", 
                      command=self.controller.handle_edit).pack(side="left", padx=5, pady=10, expand=True, fill="x")
        ctk.CTkButton(action_frame, text="🗑️ Xóa", font=btn_font, fg_color="#dc2626", hover_color="#b91c1c", 
                      command=self.controller.handle_delete).pack(side="left", padx=5, pady=10, expand=True, fill="x")
        
        ctk.CTkButton(action_frame, text="📤 Xuất CSV", font=btn_font, fg_color="#0d9488", hover_color="#0f766e", 
                      command=self.controller.handle_export).pack(side="right", padx=(5, 10), pady=10, expand=True, fill="x")
        ctk.CTkButton(action_frame, text="📥 Nhập CSV", font=btn_font, fg_color="#7c3aed", hover_color="#6d28d9", 
                      command=self.controller.handle_import).pack(side="right", padx=5, pady=10, expand=True, fill="x")

        # --- BẢNG DỮ LIỆU ---
        table_container = ctk.CTkFrame(self, corner_radius=15, fg_color="#2b2b2b")
        table_container.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # Tinh chỉnh Style Treeview cho Dark Mode
        style = ttk.Style() 
        style.theme_use("clam") 
        style.configure("Treeview.Heading", font=("Arial", 13, "bold"), 
                        background="#3b3b3b", foreground="white", borderwidth=0, padding=(5,10))
        style.configure("Treeview", font=("Arial", 13), rowheight=100, 
                        background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", borderwidth=0)
        style.map('Treeview', background=[('selected', '#1d4ed8')], foreground=[('selected', 'white')])

        # THÊM CỘT PRICE_IN VÀO GIỮA CATEGORY VÀ PRICE_OUT
        columns = ("check", "pin", "barcode", "name", "category", "price_in", "price_out", "stock", "unit")
        self.tree = ttk.Treeview(table_container, columns=columns, show="tree headings", style="Treeview")
        
        scrollbar = ctk.CTkScrollbar(table_container, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y", padx=(0, 5), pady=5)
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        self.tree.heading("#0", text="Ảnh")
        self.tree.column("#0", width=120, anchor="center", stretch=False)

        self.tree.heading("check", text="☐", command=self.toggle_all_check)
        self.tree.heading("pin", text="☆")  
        self.tree.heading("barcode", text="Mã hàng") 
        self.tree.heading("name", text="Tên hàng hóa", anchor="w") 
        self.tree.heading("category", text="Nhóm hàng") 
        self.tree.heading("price_in", text="Giá nhập")
        self.tree.heading("price_out", text="Giá bán") 
        self.tree.heading("stock", text="Tồn kho") 
        self.tree.heading("unit", text="Đơn vị")
            
        self.tree.column("check", width=45, anchor="center", stretch=False)
        self.tree.column("pin", width=45, anchor="center", stretch=False)
        self.tree.column("barcode", width=120, anchor="center")
        self.tree.column("name", width=240, anchor="w")
        self.tree.column("category", width=130, anchor="center")
        self.tree.column("price_in", width=110, anchor="center") 
        self.tree.column("price_out", width=110, anchor="center")
        self.tree.column("stock", width=90, anchor="center")
        self.tree.column("unit", width=80, anchor="center")

        # Cấu hình màu sắc dòng xen kẽ tối
        self.tree.tag_configure('low_stock', foreground='#f87171', font=("Arial", 13, "bold"))
        self.tree.tag_configure('even_row', background='#2b2b2b')
        self.tree.tag_configure('odd_row', background='#333333')

        self.tree.bind('<ButtonRelease-1>', self.handle_tree_click)
        self.bind("<Map>", lambda event: self.after(50, lambda: self.winfo_toplevel().focus_set()))

    def toggle_all_check(self):
        self.all_checked = not self.all_checked
        new_icon = "☑" if self.all_checked else "☐"   
        self.tree.heading("check", text=new_icon)
        for item in self.tree.get_children():
            values = list(self.tree.item(item, "values"))
            values[0] = new_icon
            self.tree.item(item, values=values)

    def update_table(self, data_list):
        self.all_checked = False
        self.tree.heading("check", text="☐")
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        self.image_refs.clear()

        def get_stock(p):
            try:
                return int(p[5]) if p[5] is not None else 0
            except (ValueError, TypeError):
                return 0

        sorted_data = sorted(data_list, key=lambda p: get_stock(p) > 10)
            
        for i, p in enumerate(sorted_data):
            try:
                barcode = str(p[0]) if p[0] is not None else ""
                name = str(p[1]) if p[1] is not None else ""
                category = str(p[2]) if p[2] is not None else ""
                price_in = float(p[3]) if p[3] is not None else 0.0 
                price_out = float(p[4]) if p[4] is not None else 0.0
                stock = int(p[5]) if p[5] is not None else 0
                unit = str(p[7]) if p[7] is not None else ""
                image_path = str(p[8]) if p[8] else ""
                is_pinned = int(p[9]) if p[9] is not None else 0

                row_data = ("☐", "★" if is_pinned == 1 else "☆", barcode, name, category, f"{price_in:,.0f} đ", f"{price_out:,.0f} đ", stock, unit)
                tags = ('even_row',) if i % 2 == 0 else ('odd_row',)
                if stock <= 10:
                    tags = tags + ('low_stock',)

                img_tk = ""
                final_img_path = os.path.join("assets", "img", "default_product.png")
                if image_path and os.path.exists(image_path):
                    final_img_path = image_path

                if os.path.exists(final_img_path):
                    try:
                        img = Image.open(final_img_path)
                        img = img.resize((90, 90), Image.Resampling.LANCZOS)
                        img_tk = ImageTk.PhotoImage(img)
                        self.image_refs.append(img_tk)
                    except Exception as e:
                        print(f"Lỗi tải ảnh cho {barcode}: {e}")

                if img_tk:
                    self.tree.insert("", "end", image=img_tk, values=row_data, tags=tags)
                else:
                    self.tree.insert("", "end", values=row_data, tags=tags)

            except Exception as e:
                print(f"Lỗi hiển thị dòng: {e}")
                continue

    def handle_tree_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell": return
        column = self.tree.identify_column(event.x)
        item_id = self.tree.identify_row(event.y)
        if not item_id: return
        item_values = list(self.tree.item(item_id, "values"))
        
        if column == '#1': 
            item_values[0] = "☑" if item_values[0] == "☐" else "☐"
            self.tree.item(item_id, values=item_values)
        elif column == '#2': 
            barcode = item_values[2] 
            current_pin = item_values[1]
            self.controller.toggle_pin(barcode, current_pin)

    def get_checked_barcodes(self):
        checked = []
        for item in self.tree.get_children():
            if self.tree.item(item, "values")[0] == "☑":
                checked.append(self.tree.item(item, "values")[2])
        return checked

# =====================================================================
# PRODUCT FORM (CHUYỂN SANG DARK MODE)
# =====================================================================
class ProductForm(ctk.CTkToplevel):
    def __init__(self, master, title, on_save_callback, product_data=None):
        super().__init__(master)
        self.title(title)
        self.geometry("480x700")
        self.grab_set() 
        self.configure(fg_color="#1a1a1a")
        
        self.on_save_callback = on_save_callback
        self.selected_image_path = "" 
        
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="#2b2b2b", corner_radius=15)
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

        lbl_header = ctk.CTkLabel(self.scroll_frame, text="THÔNG TIN SẢN PHẨM", font=("Arial", 18, "bold"), text_color="white")
        lbl_header.pack(pady=(10, 15))

        self.entries = {}
        fields = [
            ("barcode", "Mã hàng (Barcode):"),
            ("name", "Tên sản phẩm:"),
            ("category", "Nhóm hàng:"),
            ("price_in", "Giá nhập (VND):"),
            ("price_out", "Giá bán (VND) - BẮT BUỘC SỐ:"),
            ("stock", "Số lượng tồn kho - BẮT BUỘC SỐ:"),
            ("unit", "Đơn vị tính (Cái, Hộp, Kg...):")
        ]
        
        for key, label_text in fields:
            ctk.CTkLabel(self.scroll_frame, text=label_text, font=("Arial", 12, "bold"), text_color="#9ca3af").pack(pady=(5, 0), padx=20, anchor="w")
            
            entry = ctk.CTkEntry(self.scroll_frame, font=("Arial", 14), height=35, border_width=1, corner_radius=6,
                                 fg_color="#333333", text_color="white", border_color="#555555")
            entry.pack(pady=(2, 10), padx=20, fill="x") 
            self.entries[key] = entry

        self.lbl_img = ctk.CTkLabel(self.scroll_frame, text="Hình ảnh: (Mặc định)", font=("Arial", 12, "bold"), text_color="#9ca3af")
        self.lbl_img.pack(pady=(10, 0), padx=20, anchor="w")
        
        btn_img = ctk.CTkButton(self.scroll_frame, text="📂 Chọn ảnh từ máy tính...", 
                                font=("Arial", 13), fg_color="#4b5563", hover_color="#374151", height=35,
                                command=self.choose_image)
        btn_img.pack(pady=(5, 20), padx=20, fill="x")
            
        if product_data:
            self.entries["barcode"].insert(0, product_data[2])
            self.entries["barcode"].configure(state="disabled", fg_color="#1f2937") 
            self.entries["name"].insert(0, product_data[3])
            self.entries["category"].insert(0, product_data[4])
            price_in_str = str(product_data[5]).replace(" đ", "").replace(",", "")
            self.entries["price_in"].insert(0, price_in_str)
            price_out_str = str(product_data[6]).replace(" đ", "").replace(",", "")
            self.entries["price_out"].insert(0, price_out_str)
            self.entries["stock"].insert(0, product_data[7])
            self.entries["unit"].insert(0, product_data[8])

        btn_save = ctk.CTkButton(self, text="💾 Lưu Thông Tin", font=("Arial", 15, "bold"), height=45,
                                 fg_color="#16a34a", hover_color="#15803d", corner_radius=10, command=self.save_data)
        btn_save.pack(pady=(0, 20), padx=20, fill="x")

    def choose_image(self):
        file_path = filedialog.askopenfilename(title="Chọn ảnh sản phẩm", 
                                               filetypes=[("Image files", "*.jpg *.png *.jpeg")])
        if file_path:
            self.selected_image_path = file_path
            self.lbl_img.configure(text=f"Đã chọn: {os.path.basename(file_path)}", text_color="#10b981")

    def save_data(self):
        data = {
            "barcode": self.entries["barcode"].get(),
            "name": self.entries["name"].get(),
            "category": self.entries["category"].get(),
            "price_in": self.entries["price_in"].get(),
            "price_out": self.entries["price_out"].get(),
            "stock": self.entries["stock"].get(),
            "unit": self.entries["unit"].get(),
            "image_path": self.selected_image_path 
        }
        self.on_save_callback(data, self)