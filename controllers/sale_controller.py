import customtkinter as ctk
from tkinter import messagebox
from views.sale_view import SalesView
from utils.logger import setup_logger

logger = setup_logger()

class SaleController:
    def __init__(self, parent_frame, db):
        self.db = db
        self.tabs = {}
        self.current_tab_id = 1
        self.max_tabs = 10
        
        self.view = SalesView(parent_frame, self)
        self.add_new_tab()
        
        root_window = self.view.winfo_toplevel()
        root_window.bind("<F1>", lambda e: self.add_new_tab())
        root_window.bind("<F2>", lambda e: self.view.sw_print_invoice.toggle())
        root_window.bind("<F3>", lambda e: self.view.entry_search.focus())
        root_window.bind("<F4>", lambda e: self.process_checkout())
        
        self.view.entry_search.bind("<KeyRelease>", self.handle_search_typing)

    def get_view(self):
        return self.view
    
    # ================= QUẢN LÝ TAB (HÓA ĐƠN) =================
    def add_new_tab(self):
        if len(self.tabs) >= self.max_tabs:
            messagebox.showwarning("Giới hạn", f"Chỉ được treo tối đa {self.max_tabs} hóa đơn!")
            return
            
        # Tìm số thứ tự tab nhỏ nhất đang còn trống (từ 1 đến 10)
        tab_id = 1
        while tab_id in self.tabs:
            tab_id += 1
            
        self.tabs[tab_id] = {
            "name": f"Hóa đơn {tab_id}",
            "items": {}, 
            "discount": 0, 
            "pay_method": "Chuyển khoản",
            "customer_pay": 0
        }
        self.current_tab_id = tab_id
        
        self.view.render_tabs(self.tabs, self.current_tab_id)
        self.refresh_cart_view()

    def switch_tab(self, tab_id):
        self.current_tab_id = tab_id
        self.view.render_tabs(self.tabs, self.current_tab_id)
        self.refresh_cart_view()
        
    def close_tab(self, tab_id):
        if len(self.tabs) <= 1:
            messagebox.showwarning("Cảnh báo", "Phải giữ lại ít nhất 1 hóa đơn!")
            return
            
        del self.tabs[tab_id]
        if self.current_tab_id == tab_id:
            self.current_tab_id = list(self.tabs.keys())[0]
            
        self.view.render_tabs(self.tabs, self.current_tab_id)
        self.refresh_cart_view()

    # ================= TÌM KIẾM & THÊM VÀO GIỎ =================
    def handle_search_typing(self, event):
        if event.keysym in ['Up', 'Down', 'Left', 'Right', 'Return']:
            return
            
        keyword = self.view.entry_search.get().strip()
        if not keyword:
            self.view.hide_dropdown()
            return
            
        try:
            query = "SELECT barcode, name, unit, price_out, stock FROM Products WHERE (barcode LIKE ? OR name LIKE ?) AND is_active = 1 LIMIT 10"
            self.db.cursor.execute(query, (f'%{keyword}%', f'%{keyword}%'))
            results = self.db.cursor.fetchall()
            
            if results:
                self.view.show_dropdown(results)
            else:
                self.view.show_dropdown_empty()
        except Exception as e:
            logger.error(f"Lỗi tìm kiếm POS: {e}")

    def add_to_cart(self, barcode, name, unit, price, stock):
        self.view.hide_dropdown()
        self.view.entry_search.delete(0, 'end')
        
        cart = self.tabs[self.current_tab_id]["items"]
        if barcode in cart:
            if cart[barcode]["qty"] < stock:
                cart[barcode]["qty"] += 1
            else:
                messagebox.showwarning("Hết hàng", f"Sản phẩm này chỉ còn {stock} trong kho!")
        else:
            if stock > 0:
                cart[barcode] = {"name": name, "unit": unit, "price": price, "qty": 1, "stock": stock}
            else:
                messagebox.showwarning("Hết hàng", "Sản phẩm này đã hết hàng!")
                return
        self.refresh_cart_view()

    # ================= CÁC THAO TÁC TRONG GIỎ HÀNG =================
    def increase_qty(self, barcode):
        item = self.tabs[self.current_tab_id]["items"][barcode]
        if item["qty"] < item["stock"]:
            item["qty"] += 1
            self.refresh_cart_view()
        else:
            messagebox.showwarning("Kho", "Không đủ số lượng tồn kho!")

    def decrease_qty(self, barcode):
        item = self.tabs[self.current_tab_id]["items"][barcode]
        if item["qty"] > 1:
            item["qty"] -= 1
        else:
            self.remove_item(barcode)
        self.refresh_cart_view()

    def remove_item(self, barcode):
        cart = self.tabs[self.current_tab_id]["items"]
        if barcode in cart:
            del cart[barcode]
            self.refresh_cart_view()

    def update_item_qty(self, barcode, new_qty):
        item = self.tabs[self.current_tab_id]["items"][barcode]
        try:
            qty = int(new_qty)
            if 0 < qty <= item["stock"]:
                item["qty"] = qty
            elif qty > item["stock"]:
                messagebox.showwarning("Kho", f"Chỉ còn {item['stock']} sản phẩm!")
                item["qty"] = item["stock"]
            else:
                self.remove_item(barcode)
                return
        except:
            pass
        self.refresh_cart_view()

    # ================= CẬP NHẬT GIAO DIỆN & THANH TOÁN =================
    def apply_discount(self, percent):
        try:
            p = float(percent)
            if 0 <= p <= 100:
                self.tabs[self.current_tab_id]["discount"] = p
                self.refresh_cart_view()
        except:
            pass

    def update_payment_method(self, method):
        self.tabs[self.current_tab_id]["pay_method"] = method
        self.refresh_cart_view()

    def update_customer_pay(self, amount):
        self.tabs[self.current_tab_id]["customer_pay"] = amount
        self.refresh_cart_view()

    def refresh_cart_view(self):
        tab_data = self.tabs[self.current_tab_id]
        self.view.update_cart_table(tab_data["items"])
        
        total_qty = sum(item["qty"] for item in tab_data["items"].values())
        total_amount = sum(item["qty"] * item["price"] for item in tab_data["items"].values())
        
        discount_amount = total_amount * (tab_data["discount"] / 100)
        final_amount = total_amount - discount_amount
        
        self.view.update_payment_panel(
            total_qty, total_amount, tab_data["discount"], 
            final_amount, tab_data["pay_method"], tab_data["customer_pay"]
        )

    def process_checkout(self):
        tab_data = self.tabs[self.current_tab_id]
        if not tab_data["items"]:
            messagebox.showinfo("Trống", "Giỏ hàng đang trống!")
            return
            
        total_amount = sum(item["qty"] * item["price"] for item in tab_data["items"].values())
        final_amount = total_amount * (1 - tab_data["discount"]/100)
        
        method = tab_data["pay_method"]
        cust_pay = tab_data["customer_pay"] if method == "Tiền mặt" else final_amount
        change = cust_pay - final_amount if cust_pay > final_amount else 0
        
        if method == "Tiền mặt" and cust_pay < final_amount:
            messagebox.showerror("Lỗi", "Khách đưa thiếu tiền!")
            return

        # ==========================================
        # LOGIC BẬT/TẮT IN HÓA ĐƠN
        # ==========================================
        # Lấy giá trị của công tắc in hóa đơn từ View
        if self.view.sw_print_invoice.get() == 1: 
            # Bắt buộc import ở đây để tránh lỗi vòng lặp (circular import)
            from views.sale_view import InvoicePreviewDialog
            
            # Gọi hiển thị form xem trước hóa đơn
            dialog = InvoicePreviewDialog(
                self.view, 
                tab_data["items"], 
                total_amount, 
                tab_data["discount"], 
                final_amount, 
                method
            )
            
            # Tạm dừng code, chờ người dùng thao tác trên form hóa đơn
            self.view.wait_window(dialog) 
            
            # Nếu người dùng ấn nút "HỦY BỎ" trên form, dừng việc thanh toán lại
            if not dialog.confirmed:
                return 
        # ==========================================

        # TIẾN HÀNH LƯU DATABASE
        cart_items_db = [(barcode, data["qty"], data["price"]) for barcode, data in tab_data["items"].items()]
        
        success, msg = self.db.process_sale(cart_items_db, final_amount, method, cust_pay, change)
        
        if success:
            messagebox.showinfo("Thành công", f"Thanh toán thành công! Tiền thối: {change:,.0f} đ")
            
            # Xóa tab hiện tại sau khi thanh toán xong
            old_tab_id = self.current_tab_id
            if len(self.tabs) > 1:
                del self.tabs[old_tab_id]
                self.current_tab_id = list(self.tabs.keys())[0]
            else:
                self.tabs[old_tab_id]["items"] = {}
                self.tabs[old_tab_id]["discount"] = 0
                self.tabs[old_tab_id]["customer_pay"] = 0
                
            self.view.render_tabs(self.tabs, self.current_tab_id)
            self.refresh_cart_view()
        else:
            messagebox.showerror("Lỗi", msg)