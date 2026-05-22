import customtkinter as ctk
from tkinter import ttk
import os
from PIL import Image

# ================= TẠO BẢNG NHẬP LIỆU CUSTOM (TO & HIỆN ĐẠI HƠN) =================
class CustomInputDialog(ctk.CTkToplevel):
    def __init__(self, title, text, initial_value=""):
        super().__init__()
        self.title(title)
        self.geometry("400x220") # Kích thước to rõ ràng
        self.attributes("-topmost", True)
        self.grab_set() # Khóa cửa sổ nền
        
        self.value = None

        # Giao diện
        self.configure(fg_color="#2b2b2b")
        ctk.CTkLabel(self, text=text, font=("Arial", 18, "bold"), text_color="white").pack(pady=(25, 10))
        
        self.entry = ctk.CTkEntry(self, font=("Arial", 20), width=250, height=45, justify="center")
        self.entry.pack(pady=10)
        self.entry.insert(0, str(initial_value))
        self.entry.focus()
        self.entry.select_range(0, 'end') # Bôi đen sẵn để nhập đè luôn

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=(15, 10))

        ctk.CTkButton(btn_frame, text="XÁC NHẬN (Enter)", width=120, height=40, font=("Arial", 14, "bold"), 
                      fg_color="#2563eb", hover_color="#1d4ed8", command=self.on_ok).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="HỦY (Esc)", width=120, height=40, font=("Arial", 14, "bold"), 
                      fg_color="#4b5563", hover_color="#374151", command=self.on_cancel).pack(side="left", padx=10)

        # Phím tắt
        self.bind("<Return>", lambda e: self.on_ok())
        self.bind("<Escape>", lambda e: self.on_cancel())
        self.wait_window(self)

    def on_ok(self):
        self.value = self.entry.get()
        self.destroy()

    def on_cancel(self):
        self.destroy()

    def get_input(self):
        return self.value

# ================= MÀN HÌNH BÁN HÀNG CHÍNH =================
class SalesView(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color="#1a1a1a")
        self.controller = controller
        self.setup_ui()
        
    def setup_ui(self):
        top_frame = ctk.CTkFrame(self, height=55, fg_color="#2b2b2b", corner_radius=0)
        top_frame.pack(side="top", fill="x", pady=(0, 5))
        
        search_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        search_frame.pack(side="left", padx=(15, 5), pady=10, fill="y")
        
        self.entry_search = ctk.CTkEntry(search_frame, width=450, height=45, corner_radius=8,
                                         placeholder_text="🔍 Nhập mã hoặc tên hàng (F3)...", 
                                         font=("Arial", 14), fg_color="#333333", text_color="white", border_color="#555555")
        self.entry_search.pack(side="left", padx=5)
        
        self.dropdown_frame = ctk.CTkScrollableFrame(self, width=600, height=250, 
                                                     corner_radius=8, fg_color="#333333", 
                                                     border_width=1, border_color="#555555")
        
        btn_add_tab = ctk.CTkButton(top_frame, text="+", width=35, height=35, corner_radius=8,
                                    font=("Arial", 18, "bold"), fg_color="#1d4ed8", hover_color="#1e3a8a",
                                    command=self.controller.add_new_tab)
        btn_add_tab.pack(side="left", padx=(5, 15), pady=10)

        # 🆕 Đổi thành CTkScrollableFrame, thêm orientation="horizontal" và set height
        self.tabs_frame = ctk.CTkScrollableFrame(top_frame, orientation="horizontal", height=60, fg_color="transparent")
        self.tabs_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # 2. 🆕 THÊM DÒNG NÀY: Can thiệp và giảm độ dày của thanh cuộn ngang xuống 8px
        self.tabs_frame._scrollbar.configure(height=15)
        
        body_frame = ctk.CTkFrame(self, fg_color="transparent")
        body_frame.pack(side="top", fill="both", expand=True, padx=5, pady=5)
        
        left_frame = ctk.CTkFrame(body_frame, fg_color="#2b2b2b", corner_radius=10)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Cart.Treeview.Heading", font=("Arial", 12, "bold"), 
                        background="#3b3b3b", foreground="white", borderwidth=0, padding=5)
        style.configure("Cart.Treeview", font=("Arial", 13), rowheight=45, 
                        background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", borderwidth=0)
        style.map('Cart.Treeview', background=[('selected', '#1d4ed8')], foreground=[('selected', 'white')])
        
        cols = ("stt", "del", "barcode", "name", "unit", "qty", "price", "total", "add", "sub")
        self.tree = ttk.Treeview(left_frame, columns=cols, show="headings", style="Cart.Treeview")
        
        self.tree.heading("stt", text="STT")
        self.tree.heading("del", text="🗑️")
        self.tree.heading("barcode", text="Mã Hàng")
        self.tree.heading("name", text="Tên Hàng", anchor="w")
        self.tree.heading("unit", text="ĐVT")
        self.tree.heading("qty", text="SL")
        self.tree.heading("price", text="Đơn Giá")
        self.tree.heading("total", text="Thành Tiền")
        self.tree.heading("add", text="➕")
        self.tree.heading("sub", text="➖")
        
        self.tree.column("stt", width=50, anchor="center")
        self.tree.column("del", width=50, anchor="center")
        self.tree.column("barcode", width=120, anchor="center")
        self.tree.column("name", width=250, anchor="w")
        self.tree.column("unit", width=80, anchor="center")
        self.tree.column("qty", width=80, anchor="center")
        self.tree.column("price", width=120, anchor="e")
        self.tree.column("total", width=120, anchor="e")
        self.tree.column("add", width=50, anchor="center")
        self.tree.column("sub", width=50, anchor="center")
        
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind('<ButtonRelease-1>', self.handle_cart_click)

        right_frame = ctk.CTkFrame(body_frame, width=380, fg_color="#2b2b2b", corner_radius=10)
        right_frame.pack(side="right", fill="y")
        right_frame.pack_propagate(False) 
        
        # ========================================================
        # KHU VỰC 1: ĐÁY CỐ ĐỊNH (Gồm công tắc In và nút Thanh toán)
        # ========================================================
        bottom_panel = ctk.CTkFrame(right_frame, fg_color="transparent")
        bottom_panel.pack(side="bottom", fill="x", pady=20)

        # Công tắc in hóa đơn
        self.sw_print_invoice = ctk.CTkSwitch(bottom_panel, text="In hóa đơn khi thanh toán", 
                                              font=("Arial", 13), text_color="white")
        self.sw_print_invoice.pack(fill="x", padx=20, pady=(0, 15))
        self.sw_print_invoice.deselect()
        
        btn_checkout = ctk.CTkButton(bottom_panel, text="THANH TOÁN", font=("Arial", 20, "bold"), 
                                     height=60, fg_color="#2563eb", hover_color="#1d4ed8", corner_radius=10,
                                     command=self.controller.process_checkout)
        btn_checkout.pack(fill="x", padx=20)

        # ========================================================
        # KHU VỰC 2: PHẦN TRÊN CUỘN ĐƯỢC (Chứa toàn bộ thông tin)
        # ========================================================
        payment_scroll = ctk.CTkScrollableFrame(right_frame, fg_color="transparent")
        payment_scroll.pack(side="top", fill="both", expand=True)
        # Có thể làm mỏng thanh cuộn dọc (tùy chọn)
        payment_scroll._scrollbar.configure(width=8)

        # Đổi tham số parent của hàm summary_row sang payment_scroll
        self.create_summary_row(payment_scroll, "Tổng tiền hàng", "lbl_total_qty", "lbl_total_amt")
        
        row2 = ctk.CTkFrame(payment_scroll, fg_color="transparent")
        row2.pack(fill="x", padx=20, pady=8)
        ctk.CTkLabel(row2, text="Giảm giá (%) ✎", font=("Arial", 14), text_color="white").pack(side="left")
        self.btn_discount = ctk.CTkButton(row2, text="0%", width=70, height=28, fg_color="#374151", text_color="white", hover_color="#4b5563", command=self.ask_discount)
        self.btn_discount.pack(side="right")
        
        ctk.CTkFrame(payment_scroll, height=1, fg_color="#4b5563").pack(fill="x", padx=20, pady=15)
        
        row3 = ctk.CTkFrame(payment_scroll, fg_color="transparent")
        row3.pack(fill="x", padx=20, pady=8)
        ctk.CTkLabel(row3, text="Khách cần trả", font=("Arial", 16, "bold"), text_color="white").pack(side="left")
        self.lbl_final_amt = ctk.CTkLabel(row3, text="0", font=("Arial", 24, "bold"), text_color="#3b82f6")
        self.lbl_final_amt.pack(side="right")
        
        row4 = ctk.CTkFrame(payment_scroll, fg_color="transparent")
        row4.pack(fill="x", padx=20, pady=8)
        ctk.CTkLabel(row4, text="Khách thanh toán ✎", font=("Arial", 14), text_color="white").pack(side="left")
        self.btn_cust_pay = ctk.CTkButton(row4, text="0", width=120, height=35, font=("Arial", 14, "bold"), fg_color="#374151", text_color="white", hover_color="#4b5563", command=self.ask_cust_pay)
        self.btn_cust_pay.pack(side="right")
        
        self.row_change = ctk.CTkFrame(payment_scroll, fg_color="transparent")
        ctk.CTkLabel(self.row_change, text="Cần trả lại", font=("Arial", 14), text_color="#9ca3af").pack(side="left")
        self.lbl_change = ctk.CTkLabel(self.row_change, text="0", font=("Arial", 16, "bold"), text_color="#f87171")
        self.lbl_change.pack(side="right")
        
        pm_frame = ctk.CTkFrame(payment_scroll, fg_color="transparent")
        pm_frame.pack(fill="x", padx=20, pady=20)
        
        self.pay_var = ctk.StringVar(value="Chuyển khoản")
        r1 = ctk.CTkRadioButton(pm_frame, text="Tiền mặt", variable=self.pay_var, value="Tiền mặt", text_color="white", command=self.on_pay_method_change)
        r1.pack(side="left", padx=(0,15))
        r2 = ctk.CTkRadioButton(pm_frame, text="Chuyển khoản", variable=self.pay_var, value="Chuyển khoản", text_color="white", command=self.on_pay_method_change)
        r2.pack(side="left")
        
        self.quick_cash_frame = ctk.CTkFrame(payment_scroll, fg_color="transparent")
        cash_vals = [20000, 50000, 100000, 200000, 500000]
        for i, val in enumerate(cash_vals):
            btn = ctk.CTkButton(self.quick_cash_frame, text=f"{val:,.0f}", width=70, height=35, 
                                font=("Arial", 13), fg_color="#1f2937", text_color="#60a5fa", hover_color="#374151",
                                border_width=1, border_color="#374151",
                                command=lambda v=val: self.controller.update_customer_pay(v))
            btn.grid(row=i//3, column=i%3, padx=5, pady=5)
            
        self.qr_frame = ctk.CTkFrame(payment_scroll, fg_color="#374151", height=200, corner_radius=10)
        qr_image_path = os.path.join("assets", "img","qr", "qrcode.jpg") 
        try:
            qr_img_data = Image.open(qr_image_path)
            self.qr_image = ctk.CTkImage(light_image=qr_img_data, dark_image=qr_img_data, size=(150, 150))
            lbl_qr_image = ctk.CTkLabel(self.qr_frame, text="", image=self.qr_image)
            lbl_qr_image.pack(pady=(10, 0))
            ctk.CTkLabel(self.qr_frame, text="Quét để thanh toán", text_color="#9ca3af", font=("Arial", 12)).pack(pady=(5, 10))
        except Exception as e:
            ctk.CTkLabel(self.qr_frame, text="[ Chưa có ảnh QR ]\nVui lòng thêm vào thư mục assets/img", text_color="#f87171").pack(expand=True)

        self.qr_frame.pack(fill="x", padx=20, pady=10)
    def create_summary_row(self, parent, text, qty_attr, amt_attr):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=8)
        ctk.CTkLabel(row, text=text, font=("Arial", 14), text_color="white").pack(side="left")
        
        lbl_qty = ctk.CTkLabel(row, text="0", font=("Arial", 14), text_color="#9ca3af")
        lbl_qty.pack(side="left", padx=10)
        setattr(self, qty_attr, lbl_qty)
        
        lbl_amt = ctk.CTkLabel(row, text="0", font=("Arial", 16, "bold"), text_color="white")
        lbl_amt.pack(side="right")
        setattr(self, amt_attr, lbl_amt)

    def show_dropdown(self, results):
        self.dropdown_frame.place(x=15, y=55) 
        self.dropdown_frame.lift()
        
        for widget in self.dropdown_frame.winfo_children():
            widget.destroy()
            
        for row in results:
            barcode, name, unit, price, stock = row
            item_frame = ctk.CTkFrame(self.dropdown_frame, fg_color="transparent")
            item_frame.pack(fill="x", pady=2)
            
            btn_text = f"{barcode}  |  {name}  |  Giá: {price:,.0f}  |  Tồn: {stock}"
            btn = ctk.CTkButton(item_frame, text=btn_text, anchor="w", fg_color="transparent", 
                                text_color="white", hover_color="#4b5563", font=("Arial", 13),
                                command=lambda b=barcode, n=name, u=unit, p=price, s=stock: self.controller.add_to_cart(b, n, u, p, s))
            btn.pack(fill="x", expand=True, padx=5, pady=2)
            
    def show_dropdown_empty(self):
        self.dropdown_frame.place(x=15, y=55)
        self.dropdown_frame.lift()
        for widget in self.dropdown_frame.winfo_children():
            widget.destroy()
        ctk.CTkLabel(self.dropdown_frame, text="Trống (Không tìm thấy hàng hóa)", text_color="#9ca3af", font=("Arial", 13)).pack(pady=15)
        
    def hide_dropdown(self):
        self.dropdown_frame.place_forget()

    def render_tabs(self, tabs_dict, current_id):
        for widget in self.tabs_frame.winfo_children():
            widget.destroy()
            
        for t_id in sorted(tabs_dict.keys()):
            data = tabs_dict[t_id]
            color = "#3b82f6" if t_id == current_id else "#374151" 
            
            tab_btn_frame = ctk.CTkFrame(self.tabs_frame, fg_color=color, corner_radius=8)
            tab_btn_frame.pack(side="left", padx=5, pady=10, fill="y")
            
            btn_name = ctk.CTkButton(tab_btn_frame, text=data["name"], width=80, fg_color="transparent",
                                     font=("Arial", 13, "bold"), text_color="white",
                                     command=lambda id=t_id: self.controller.switch_tab(id))
            btn_name.pack(side="left", padx=(5,0))
            
            btn_close = ctk.CTkButton(tab_btn_frame, text="✕", width=20, fg_color="transparent", hover_color="#ef4444", text_color="white",
                                      command=lambda id=t_id: self.controller.close_tab(id))
            btn_close.pack(side="right", padx=(0,5))

    def update_cart_table(self, items_dict):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        stt = 1
        for barcode, data in items_dict.items():
            total = data["qty"] * data["price"]
            self.tree.insert("", "end", values=(
                stt, "🗑️", barcode, data["name"], data["unit"], 
                f"✎ {data['qty']}", f"{data['price']:,.0f}", f"{total:,.0f}", "➕", "➖" 
            ))
            stt += 1

    def handle_cart_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell": return
        column = self.tree.identify_column(event.x)
        item_id = self.tree.identify_row(event.y)
        if not item_id: return
        
        values = self.tree.item(item_id, "values")
        barcode = values[2]
        
        if column == '#2': 
            self.controller.remove_item(barcode)
        elif column == '#9': 
            self.controller.increase_qty(barcode)
        elif column == '#10': 
            self.controller.decrease_qty(barcode)
        elif column == '#6': 
            current_qty = self.controller.tabs[self.controller.current_tab_id]["items"][barcode]["qty"]
            # DÙNG BẢNG NHẬP LIỆU CUSTOM MỚI
            dialog = CustomInputDialog("Sửa số lượng", f"Nhập số lượng mới cho\n{values[3]}:", initial_value=current_qty)
            new_qty = dialog.get_input()
            if new_qty is not None and str(new_qty).isdigit():
                self.controller.update_item_qty(barcode, int(new_qty))

    def on_pay_method_change(self):
        method = self.pay_var.get()
        if method == "Chuyển khoản":
            self.controller.tabs[self.controller.current_tab_id]["customer_pay"] = 0
        self.controller.update_payment_method(method)

    def ask_discount(self):
        dialog = CustomInputDialog("Giảm giá", "Nhập phần trăm giảm giá\n(Từ 0 đến 100):", initial_value="0")
        val = dialog.get_input()
        if val is not None:
            try:
                self.controller.apply_discount(float(val))
            except ValueError:
                pass
            
    def ask_cust_pay(self):
        if self.pay_var.get() == "Tiền mặt":
            current_pay = self.controller.tabs[self.controller.current_tab_id]["customer_pay"]
            dialog = CustomInputDialog("Khách trả", "Nhập số tiền khách đưa:", initial_value=current_pay)
            val = dialog.get_input()
            if val is not None:
                try:
                    self.controller.update_customer_pay(float(val))
                except ValueError:
                    pass

    def update_payment_panel(self, qty, total, discount_pct, final_amt, method, cust_pay):
        self.lbl_total_qty.configure(text=str(qty))
        self.lbl_total_amt.configure(text=f"{total:,.0f}")
        self.btn_discount.configure(text=f"{discount_pct}%")
        self.lbl_final_amt.configure(text=f"{final_amt:,.0f}")
        
        self.pay_var.set(method)
        
        if method == "Tiền mặt":
            self.qr_frame.pack_forget()
            self.quick_cash_frame.pack(fill="x", padx=20, pady=10)
            self.row_change.pack(fill="x", padx=20, pady=10)
            
            if cust_pay == 0:
                cust_pay = final_amt
                self.controller.tabs[self.controller.current_tab_id]["customer_pay"] = cust_pay
                
            self.btn_cust_pay.configure(text=f"{cust_pay:,.0f}")
            change = cust_pay - final_amt if cust_pay > final_amt else 0
            self.lbl_change.configure(text=f"{change:,.0f}")
        else:
            self.quick_cash_frame.pack_forget()
            self.row_change.pack_forget()
            self.qr_frame.pack(fill="x", padx=20, pady=10)
            self.btn_cust_pay.configure(text=f"{final_amt:,.0f}")
            
# =====================================================================
# DIALOG XEM TRƯỚC HÓA ĐƠN MÔ PHỎNG (THERMAL RECEIPT PREVIEW)
# =====================================================================
class InvoicePreviewDialog(ctk.CTkToplevel):
    def __init__(self, master, cart_items, total_amt, discount_pct, final_amt, payment_method):
        super().__init__(master)
        self.title("Xem trước hóa đơn in")
        self.geometry("420x620")
        self.configure(fg_color="#f3f4f6") # Màu nền xám nhẹ làm nổi bật tờ hóa đơn
        self.grab_set() 
        self.attributes("-topmost", True)
        
        self.confirmed = False # Trạng thái người dùng ấn "In" hay "Hủy"
        
        # Khung giấy trắng mô phỏng tờ hóa đơn nhiệt
        receipt_paper = ctk.CTkScrollableFrame(self, fg_color="white", corner_radius=8, border_width=1, border_color="#d1d5db")
        receipt_paper.pack(fill="both", expand=True, padx=20, pady=(20, 10))
        
        # Thông tin cửa hàng
        ctk.CTkLabel(receipt_paper, text="SIÊU THỊ MINI SIÊU CẤP", font=("Arial", 16, "bold"), text_color="black").pack(pady=(10, 2))
        ctk.CTkLabel(receipt_paper, text="Trường Đại Học Hạ Long", font=("Arial", 11), text_color="#4b5563").pack()
        ctk.CTkLabel(receipt_paper, text="--------------------------------------------------", text_color="black").pack()
        
        ctk.CTkLabel(receipt_paper, text="HÓA ĐƠN THANH TOÁN", font=("Arial", 14, "bold"), text_color="black").pack(pady=5)
        
        from datetime import datetime
        now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        ctk.CTkLabel(receipt_paper, text=f"Thời gian: {now_str}", font=("Arial", 11), text_color="black", anchor="w").pack(fill="x", padx=10)
        ctk.CTkLabel(receipt_paper, text=f"Hình thức: {payment_method}", font=("Arial", 11), text_color="black", anchor="w").pack(fill="x", padx=10)
        ctk.CTkLabel(receipt_paper, text="--------------------------------------------------", text_color="black").pack()
        
        # Tiêu đề danh sách (Sử dụng font Courier New để căn chỉnh ký tự cực chuẩn)
        lbl_h = ctk.CTkLabel(receipt_paper, text=f"{'Tên sản phẩm':<20} {'SL':<4} {'Thành tiền':>12}", 
                             font=("Courier New", 12, "bold"), text_color="black", anchor="w")
        lbl_h.pack(fill="x", padx=10)
        
        # Duyệt danh sách mặt hàng đổ vào hóa đơn
        for barcode, data in cart_items.items():
            # Rút gọn tên nếu quá dài để không vỡ dòng hóa đơn
            name_short = data['name'][:18] + ".." if len(data['name']) > 20 else data['name']
            item_total = data['qty'] * data['price']
            line_str = f"{name_short:<20} {data['qty']:<4} {item_total:>11,.0f}đ"
            
            ctk.CTkLabel(receipt_paper, text=line_str, font=("Courier New", 12), text_color="black", anchor="w").pack(fill="x", padx=10)
            
        ctk.CTkLabel(receipt_paper, text="--------------------------------------------------", text_color="black").pack()
        
        # Phần tổng tiền toán học
        ctk.CTkLabel(receipt_paper, text=f"Tổng tiền hàng: {total_amt:>20,.0f} đ", font=("Courier New", 12), text_color="black", anchor="w").pack(fill="x", padx=10)
        ctk.CTkLabel(receipt_paper, text=f"Giảm giá: {discount_pct:>26}%", font=("Courier New", 12), text_color="black", anchor="w").pack(fill="x", padx=10)
        ctk.CTkLabel(receipt_paper, text=f"KHÁCH CẦN TRẢ: {final_amt:>18,.0f} đ", font=("Courier New", 13, "bold"), text_color="#1d4ed8", anchor="w").pack(fill="x", padx=10)
        
        ctk.CTkLabel(receipt_paper, text="--------------------------------------------------", text_color="black").pack()
        ctk.CTkLabel(receipt_paper, text="XIN CẢM ƠN QUÝ KHÁCH!\nHẸN GẶP LẠI", font=("Arial", 12, "italic"), text_color="#4b5563").pack(pady=(5, 10))
        
        # Khu vực nút bấm chức năng (Nằm ngoài khung hóa đơn cuộn)
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(side="bottom", fill="x", pady=15, padx=20)
        
        ctk.CTkButton(btn_frame, text="🖨️ XÁC NHẬN IN", font=("Arial", 13, "bold"), fg_color="#16a34a", hover_color="#15803d", height=40, command=self.on_print).pack(side="left", expand=True, fill="x", padx=(0, 5))
        ctk.CTkButton(btn_frame, text="❌ HỦY BỎ", font=("Arial", 13, "bold"), fg_color="#dc2626", hover_color="#b91c1c", height=40, command=self.on_cancel).pack(side="right", expand=True, fill="x", padx=(5, 0))

    def on_print(self):
        from tkinter import messagebox
        messagebox.showinfo("Thông báo in", "Đang gửi lệnh in đến máy in mô phỏng...\n[Hệ thống đã ghi nhận doanh thu thành công!]")
        self.confirmed = True
        self.destroy()

    def on_cancel(self):
        self.confirmed = False
        self.destroy()