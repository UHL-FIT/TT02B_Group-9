from views.inventory_view import InventoryView, ProductForm
from utils.logger import setup_logger
from tkinter import messagebox, filedialog
from models.database import SupermarketDB
import os
import shutil

logger = setup_logger()

class InventoryController:
    def __init__(self, parent_frame, db: SupermarketDB):
        self.db = db    
        self.view = InventoryView(parent_frame, self)
        self.view.entry_search.bind("<Return>", lambda event: self.search_data())
        self.load_data()

    def get_view(self):
        return self.view

    def load_data(self):
        """Tải dữ liệu từ Database lên RAM 1 lần duy nhất, sau đó tự động khởi tạo danh mục"""
        try:
            self.all_products_cache = self.db.get_all_products()
            
            categories = set(str(p[2]) for p in self.all_products_cache if p[2])
            cat_list = ["Tất cả danh mục"] + sorted(list(categories))
            
            self.view.cb_category.configure(values=cat_list)
            
            self.view.cb_category.set("Tất cả danh mục")
            self.view.cb_stock.set("Tất cả trạng thái")
            
            # Dọn dẹp text
            self.view.entry_search.delete(0, 'end')

            # ==========================================
            # 🆕 SỬA THÀNH 2 DÒNG NÀY: Giả lập thao tác click vào -> click ra
            self.view.entry_search.focus_set()         # 1. Ép focus vào ô tìm kiếm
            self.view.winfo_toplevel().focus_set()     # 2. Lập tức ép focus ra cửa sổ chính
            # ==========================================

            self.view.update_table(self.all_products_cache)
        except Exception as e:
            logger.error(f"Lỗi khi tải dữ liệu Kho hàng: {e}")

    def apply_filters(self, *args):
        """Hàm xử lý bộ lọc ngay trên RAM mà không đụng chạm vào file database.py"""
        try:
            keyword = self.view.entry_search.get().strip().lower()
            category = self.view.cb_category.get()
            stock_status = self.view.cb_stock.get()

            if not hasattr(self, 'all_products_cache'):
                self.all_products_cache = self.db.get_all_products()

            filtered_data = []
            
            for p in self.all_products_cache:
                p_barcode = str(p[0]).lower() if p[0] else ""
                p_name = str(p[1]).lower() if p[1] else ""
                p_category = str(p[2]) if p[2] else ""
                p_stock = int(p[5]) if p[5] else 0

                if keyword and (keyword not in p_barcode and keyword not in p_name):
                    continue
                
                if category != "Tất cả danh mục" and p_category != category:
                    continue
                
                if stock_status == "Còn hàng" and p_stock <= 0:
                    continue
                if stock_status == "Sắp hết (<=10)" and p_stock > 10:
                    continue
                    
                filtered_data.append(p)

            self.view.update_table(filtered_data)
            
        except Exception as e:
            logger.error(f"Lỗi khi áp dụng bộ lọc: {e}")

    def search_data(self):
        self.apply_filters()

    def save_image(self, barcode, source_path):
        """Hàm phụ: Copy ảnh từ máy người dùng vào thư mục data của dự án"""
        if not source_path or not os.path.exists(source_path):
            return ""
        
        target_dir = os.path.join("assets", "img", "products")
        os.makedirs(target_dir, exist_ok=True)
        
        ext = os.path.splitext(source_path)[1]
        target_path = os.path.join(target_dir, f"{barcode}{ext}")
        
        try:
            shutil.copy(source_path, target_path)
            return target_path
        except Exception as e:
            logger.error(f"Lỗi lưu ảnh: {e}")
            return ""

    def handle_add(self):
        ProductForm(self.view, "Thêm Sản Phẩm Mới", self.execute_add)

    def execute_add(self, data, form_window):
        try:
            p_out = float(data["price_out"])
            stock = int(data["stock"])
            p_in = float(data["price_in"]) if data["price_in"] else 0.0
        except ValueError:
            messagebox.showerror("Lỗi nhập liệu", "Giá bán và Tồn kho phải là số hợp lệ!")
            return 

        img_path = self.save_image(data["barcode"], data.get("image_path", ""))

        db_data = (data["barcode"], data["name"], data["category"], p_in, p_out, stock, 5, data["unit"], img_path)
        success, msg = self.db.add_product(db_data)
        
        if success:
            messagebox.showinfo("Thành công", msg)
            form_window.destroy()
            self.load_data()
        else:
            messagebox.showerror("Lỗi", msg)

    def handle_edit(self):
        selected_item = self.view.tree.selection()
        if not selected_item:
            messagebox.showwarning("Chú ý", "Vui lòng chọn một sản phẩm trên bảng để sửa!")
            return
        
        item_data = self.view.tree.item(selected_item)['values']
        ProductForm(self.view, "Sửa Sản Phẩm", self.execute_edit, product_data=item_data)

    def execute_edit(self, data, form_window):
        try:
            price_in = float(data["price_in"]) if data["price_in"] else 0.0 # Lưu Giá Nhập khi sửa
            price_out = float(data["price_out"]) if data["price_out"] else 0.0
            stock = int(data["stock"]) if data["stock"] else 0
        except ValueError:
            messagebox.showerror("Lỗi nhập liệu", "Vui lòng nhập SỐ cho Giá tiền và Tồn kho!")
            return

        updates = {
            "name": data["name"],
            "category": data["category"],
            "price_in": price_in, # Cập nhật Giá Nhập vào dict update
            "price_out": price_out,
            "stock": stock,
            "unit": data["unit"]
        }
        
        new_img_path = self.save_image(data["barcode"], data.get("image_path", ""))
        if new_img_path:
            updates["image_path"] = new_img_path
        
        success, msg = self.db.update_product(data["barcode"], updates)
        if success:
            messagebox.showinfo("Thành công", msg)
            form_window.destroy()
            self.load_data()
        else:
            messagebox.showerror("Lỗi", msg)

    def handle_delete(self):
        checked_barcodes = self.view.get_checked_barcodes()
        
        if checked_barcodes:
            confirm = messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa {len(checked_barcodes)} sản phẩm đã chọn?")
            if confirm:
                for bc in checked_barcodes:
                    self.db.cursor.execute("SELECT image_path FROM Products WHERE barcode = ?", (bc,))
                    res = self.db.cursor.fetchone()
                    if res and res[0]:
                        self.delete_product_image(res[0]) 
                        
                success, msg = self.db.delete_multiple_products_soft(checked_barcodes)
                if success:
                    messagebox.showinfo("Thành công", msg)
                    self.load_data()
                else:
                    messagebox.showerror("Lỗi", msg)
        else:
            selected_item = self.view.tree.selection()
            if not selected_item:
                messagebox.showwarning("Chú ý", "Vui lòng tick chọn (☐) hoặc click bôi xanh 1 sản phẩm để xóa!")
                return
            
            item_data = self.view.tree.item(selected_item)['values']
            barcode = str(item_data[2]) 
            name = str(item_data[3])    
            
            confirm = messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa '{name}' không?")
            if confirm:
                self.db.cursor.execute("SELECT image_path FROM Products WHERE barcode = ?", (barcode,))
                res = self.db.cursor.fetchone()
                if res and res[0]:
                    self.delete_product_image(res[0]) 
                    
                success, msg = self.db.delete_product_soft(barcode)
                if success:
                    messagebox.showinfo("Thành công", "Đã xóa sản phẩm khỏi danh sách!")
                    self.load_data()
                else:
                    messagebox.showerror("Lỗi", msg)
                        
    def delete_product_image(self, image_path):
        if image_path and os.path.exists(image_path):
            if "default_product.png" not in image_path:
                try:
                    os.remove(image_path)
                    logger.info(f"Đã dọn dẹp file ảnh vật lý: {image_path}")
                except Exception as e:
                    logger.error(f"Không thể xóa file ảnh: {e}")
                    
    def handle_export(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            success, msg = self.db.export_inventory_csv(file_path)
            if success:
                messagebox.showinfo("Thành công", msg)
            else:
                messagebox.showerror("Lỗi", msg)

    def handle_import(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            success, msg = self.db.import_inventory_csv(file_path)
            if success:
                messagebox.showinfo("Kết quả", msg)
                self.load_data()
            else:
                messagebox.showerror("Lỗi", msg)
                
    def toggle_pin(self, barcode, current_pin_symbol):
        new_status = 0 if current_pin_symbol == "★" else 1
        success, msg = self.db.update_product(barcode, {"is_pinned": new_status})
        if success:
            self.load_data() 
        else:
            messagebox.showerror("Lỗi", "Không thể cập nhật trạng thái ghim!")