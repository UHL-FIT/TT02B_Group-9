import customtkinter as ctk
from views.main_view import MainView
from models.database import SupermarketDB
from controllers.inventory_controller import InventoryController
from views.sale_view import SalesView
from controllers.stats_controller import StatsController
from utils.logger import setup_logger
from tkinter import messagebox, filedialog
from controllers.sale_controller import SaleController 

logger = setup_logger()

class MainController:
    def __init__(self):
        self.db = SupermarketDB()
        
        self.app = ctk.CTk()
        self.app.title("Hệ thống Quản lý Siêu thị - Nhóm 9")
        self.app.geometry("1200x700")

        self.main_view = MainView(self.app)

        # Nút 3 gạch
        self.main_view.btn_menu.configure(command=self.main_view.toggle_menu) 
        
        self.main_view.btn_sales.configure(command=self.show_sales)
        self.main_view.btn_inventory.configure(command=self.show_inventory)
        self.main_view.btn_stats.configure(command=self.show_stats)

        self.main_view.btn_help.configure(command=self.open_user_manual)
        
        self.current_view = None
        self.show_sales() 

    def clear_content(self):
        for widget in self.main_view.content_area.winfo_children():
            widget.destroy()
        self.current_view = None

    def show_sales(self):
        self.clear_content()
        sale_controller = SaleController(self.main_view.content_area, self.db)
        self.current_view = sale_controller.get_view()
        self.current_view.pack(fill="both", expand=True)
        if self.main_view.menu_visible:
            self.main_view.toggle_menu()

    def show_inventory(self):
        self.clear_content()
        inv_controller = InventoryController(self.main_view.content_area, self.db)
        self.current_view = inv_controller.get_view()
        self.current_view.pack(fill="both", expand=True)
        if self.main_view.menu_visible:
            self.main_view.toggle_menu()

    def show_stats(self):
        self.clear_content()
        stats_controller = StatsController(self.main_view.content_area, self.db)
        self.current_view = stats_controller.get_view()
        self.current_view.pack(fill="both", expand=True)
        if self.main_view.menu_visible:
            self.main_view.toggle_menu()
            
    def open_user_manual(self):
        import os
        import sys
        from tkinter import messagebox

        # Tìm đường dẫn gốc chứa file PDF
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        pdf_path = os.path.join(base_dir, "HƯỚNG DẪN SỬ DỤNG PHẦN MỀM.pdf")

        if os.path.exists(pdf_path):
            try:
                os.startfile(pdf_path) 
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể mở file PDF do lỗi: {e}")
        else:
            messagebox.showwarning("Cảnh báo", "Không tìm thấy file 'HƯỚNG DẪN SỬ DỤNG PHẦN MỀM.pdf' trong thư mục dự án!\nVui lòng kiểm tra lại.")
               
    def run(self):
        self.app.mainloop()

def chay_ung_dung():
    controller = MainController()
    controller.run()