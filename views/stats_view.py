import customtkinter as ctk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.ticker as ticker

# =====================================================================
# CỬA SỔ HIỂN THỊ CHI TIẾT ĐƠN HÀNG
# =====================================================================
class OrderDetailsDialog(ctk.CTkToplevel):
    def __init__(self, master, title, data):
        super().__init__(master)
        self.title(title)
        self.geometry("1400x900")
        self.configure(fg_color="#1a1a1a") # Màu tối đồng bộ với Inventory/Sales
        self.resizable(True, True)
        self.lift() # Đưa cửa sổ lên trên cùng
        self.focus_force() # Tập trung vào cửa sổ mới
        self.grab_set() # Khóa cửa sổ nền

        lbl_header = ctk.CTkLabel(self, text="📊 NHẬT KÝ CHI TIẾT GIAO DỊCH", font=("Segoe UI", 32, "bold"), text_color="#3b82f6")
        lbl_header.pack(pady=(20, 5))
        
        # Đường kẻ trang trí phía dưới tiêu đề
        ctk.CTkFrame(self, height=2, fg_color="#1e293b").pack(fill="x", padx=50, pady=(0, 20))

        # Cấu hình Style cho Treeview trong cửa sổ này
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Order.Treeview.Heading", font=("Arial", 13, "bold"),
                        background="#3b3b3b", foreground="white", borderwidth=0, padding=5)
        style.configure("Order.Treeview", font=("Segoe UI", 18), rowheight=75,
                        background="#2b2b2b", foreground="#ffffff", fieldbackground="#2b2b2b", borderwidth=0)
        style.map('Order.Treeview', background=[('selected', '#1d4ed8')], foreground=[('selected', 'white')])

        # Sử dụng show="tree" để ẩn hoàn toàn các tiêu đề cột và vách ngăn, chỉ giữ lại danh sách văn bản
        container = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=15)
        container.pack(fill="both", expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(container, show="tree", style="Order.Treeview")

        # Cấu hình cột hiển thị văn bản duy nhất chiếm toàn bộ chiều rộng cửa sổ
        self.tree.column("#0", width=1300, anchor="w")

        scrollbar = ctk.CTkScrollbar(container, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)
        self.tree.pack(fill="both", expand=True, padx=(10, 0), pady=10)

        # Nhóm dữ liệu theo Sale ID
        # row: (timestamp, barcode, name, category, price, qty, total_item, sale_id)
        orders = {}
        for row in data:
            s_id = row[7]
            if s_id not in orders:
                orders[s_id] = {"time": row[0], "items": [], "total_bill": 0}
            orders[s_id]["items"].append(row)
            orders[s_id]["total_bill"] += row[6]

        # Hiển thị dữ liệu phân theo đơn
        for s_id in sorted(orders.keys(), reverse=True):
            order_info = orders[s_id]
            # Hàng cha đại diện cho Đơn hàng
            header_text = f"  📦  ĐƠN HÀNG #{s_id:<5}   •   🕒 {order_info['time']}   •   💰 TỔNG CỘNG: {order_info['total_bill']:>12,.0f} đ"
            parent = self.tree.insert("", "end", text=header_text, tags=('order_header',))
            
            # Hàng con là các sản phẩm - Sẽ tự động thụt vào 1 ô so với hàng cha
            items = order_info["items"]
            for i, item in enumerate(items):
                # item: (timestamp, barcode, name, category, price, qty, total_item, sale_id)
                branch = "      └──" if i == len(items) - 1 else "      ├──"
                # Căn lề ảo cho đẹp mắt
                p_name = f"{item[2][:30]:<30}"
                qty = f"x{item[5]:<3}"
                price = f"Giá: {item[4]:>10,.0f}"
                total = f"Thành tiền: {item[6]:>12,.0f} đ"
                detail_text = f"{branch}  {p_name}  {qty} | {price} | {total}"
                self.tree.insert(parent, "end", text=detail_text, tags=('order_item',))
        
        # Cấu hình màu sắc cho "Cục" đơn hàng nổi bật hơn
        self.tree.tag_configure('order_header', background='#3b3b3b', foreground='#60a5fa', font=("Segoe UI", 22, "bold"))
        self.tree.tag_configure('order_item', foreground='#cccccc')

        # Nút đóng cửa sổ
        btn_close = ctk.CTkButton(self, text="Đóng", width=100, height=32, 
                                  fg_color="#374151", hover_color="#4b5563", 
                                  font=("Segoe UI", 13, "bold"), command=self.destroy)
        btn_close.pack(pady=15)

class StatsView(ctk.CTkScrollableFrame):
    def __init__(self, master, controller=None, **kwargs):
        """
        Khởi tạo Giao diện Thống Kê (Dashboard Cuộn dọc - Đã bỏ cuộn bảng Top 5)
        """
        super().__init__(master, fg_color="transparent", **kwargs)

        self.controller = controller
        
        # --- KHU VỰC 1: TOP (Tiêu đề và Lọc thời gian) ---
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(fill="x", pady=(0, 15))
        
        self.lbl_title = ctk.CTkLabel(self.top_frame, text="📊 BẢNG THỐNG KÊ", font=("Segoe UI", 24, "bold"))
        self.lbl_title.pack(side="left")
        
        self.time_filter = ctk.CTkComboBox(self.top_frame, values=["Tất cả", "Hôm nay", "7 ngày qua", "Tháng này"], 
                                           width=150, font=("Segoe UI", 13), state="readonly")
        self.time_filter.pack(side="right")
        self.time_filter.set("Tất cả")
        
        # --- KHU VỰC 2: CÁC THẺ KPI ---
        self.kpi_container = ctk.CTkFrame(self, fg_color="transparent")
        self.kpi_container.pack(fill="x", pady=(0, 15))
        self.kpi_container.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Hàng KPI 1: Doanh thu - Lợi nhuận - Đơn hàng
        self.lbl_revenue = self.create_kpi_card(self.kpi_container, 0, 0, "💰 Tổng Doanh Thu", "0 đ", text_color="#2ecc71", padx=(0, 10))
        self.lbl_profit = self.create_kpi_card(self.kpi_container, 0, 1, "📈 Tổng Lợi Nhuận", "0 đ", text_color="#1abc9c", padx=10)
        self.lbl_orders = self.create_kpi_card(self.kpi_container, 0, 2, "🧾 Số Đơn Hàng", "0 đơn", text_color="#3498db", padx=(10, 0), command=self.controller.show_order_details)
        
        # Hàng KPI 2: Tiền mặt - Chuyển khoản - Tồn kho
        self.lbl_cash = self.create_kpi_card(self.kpi_container, 1, 0, "💵 Doanh Thu Tiền Mặt", "0 đ", text_color="#f1c40f", padx=(0, 10))
        self.lbl_transfer = self.create_kpi_card(self.kpi_container, 1, 1, "💳 Doanh Thu Chuyển Khoản", "0 đ", text_color="#9b59b6", padx=10)
        self.lbl_low_stock = self.create_kpi_card(self.kpi_container, 1, 2, "⚠️ Sắp Hết Kho (<=10)", "0 SP", text_color="#e74c3c", padx=(10, 0))
        
        # --- KHU VỰC 3: HÀNG BIỂU ĐỒ ---
        CHART_HEIGHT = 360
        self.charts_row_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.charts_row_frame.pack(fill="x", pady=(0, 15))
        self.charts_row_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Biểu đồ xu hướng (Bên trái)
        self.trend_frame = ctk.CTkFrame(self.charts_row_frame, corner_radius=10, height=CHART_HEIGHT)
        self.trend_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.trend_frame.grid_propagate(False)
        
        self.lbl_trend_title = ctk.CTkLabel(self.trend_frame, text="📈 Xu hướng doanh thu", font=("Segoe UI", 14, "bold"))
        self.lbl_trend_title.pack(pady=(12, 5))
        
        self.canvas_trend_frame = ctk.CTkFrame(self.trend_frame, fg_color="transparent")
        self.canvas_trend_frame.pack(fill="both", expand=True, padx=10, pady=(0, 15))
        
        # Biểu đồ tròn danh mục (Bên phải)
        self.pie_frame = ctk.CTkFrame(self.charts_row_frame, corner_radius=10, height=CHART_HEIGHT)
        self.pie_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        self.pie_frame.grid_propagate(False)
        
        lbl_pie_title = ctk.CTkLabel(self.pie_frame, text="🍕 Cơ cấu theo danh mục", font=("Segoe UI", 14, "bold"))
        lbl_pie_title.pack(pady=(12, 5))
        
        self.canvas_pie_frame = ctk.CTkFrame(self.pie_frame, fg_color="transparent")
        self.canvas_pie_frame.pack(fill="both", expand=True, padx=10, pady=(0, 15))
        
        # --- KHU VỰC 4: HÀNG CÁC BẢNG ---
        TABLE_HEIGHT = 320
        self.tables_row_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.tables_row_frame.pack(fill="x", pady=(0, 10))
        self.tables_row_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Cấu hình phong cách bảng Treeview
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", 
                        borderwidth=0, rowheight=35, font=("Segoe UI", 13))
        style.configure("Treeview.Heading", background="#1f1f1f", foreground="white", 
                        font=("Segoe UI", 14, "bold"), borderwidth=0, padding=6)
        style.map('Treeview', background=[('selected', '#1f538d')])
        
        # --------------------------------------------------------
        # BẢNG 1: TOP 5 BÁN CHẠY (ĐỂ TRẦN - KHÔNG DÙNG THANH CUỘN)
        # --------------------------------------------------------
        self.table_top_container = ctk.CTkFrame(self.tables_row_frame, corner_radius=10, height=TABLE_HEIGHT)
        self.table_top_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.table_top_container.grid_propagate(False)
        
        lbl_table_top_title = ctk.CTkLabel(self.table_top_container, text="🔥 Top 5 Sản Phẩm Bán Chạy", font=("Segoe UI", 14, "bold"))
        lbl_table_top_title.pack(pady=(10, 5))
        
        columns_top = ("barcode", "name", "quantity")
        # Đã loại bỏ hoàn toàn tham số yscrollcommand
        self.tree_top = ttk.Treeview(self.table_top_container, columns=columns_top, show="headings")
        self.tree_top.heading("barcode", text="Mã")
        self.tree_top.heading("name", text="Tên Sản Phẩm")
        self.tree_top.heading("quantity", text="Đã bán")
        self.tree_top.column("barcode", width=70, anchor="center")
        self.tree_top.column("name", width=180, anchor="w")
        self.tree_top.column("quantity", width=60, anchor="center")
        # Sử dụng pack giãn đều hai lề trái phải (padx=10)
        self.tree_top.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # --------------------------------------------------------
        # BẢNG 2: HÀNG SẮP HẾT KHO (VẪN GIỮ CUỘN VÌ DANH SÁCH DÀI)
        # --------------------------------------------------------
        self.table_low_container = ctk.CTkFrame(self.tables_row_frame, corner_radius=10, height=TABLE_HEIGHT)
        self.table_low_container.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        self.table_low_container.grid_propagate(False)
        
        lbl_table_low_title = ctk.CTkLabel(self.table_low_container, text="⚠️ Danh Sách Hàng Sắp Hết Kho", font=("Segoe UI", 14, "bold"))
        lbl_table_low_title.pack(pady=(10, 5))
        
        scroll_low = ctk.CTkScrollbar(self.table_low_container, orientation="vertical")
        scroll_low.pack(side="right", fill="y", pady=(0, 10))
        
        columns_low = ("barcode", "name", "stock")
        self.tree_low = ttk.Treeview(self.table_low_container, columns=columns_low, show="headings", yscrollcommand=scroll_low.set)
        self.tree_low.heading("barcode", text="Mã")
        self.tree_low.heading("name", text="Tên Sản Phẩm")
        self.tree_low.heading("stock", text="Tồn kho")
        self.tree_low.column("barcode", width=70, anchor="center")
        self.tree_low.column("name", width=180, anchor="w")
        self.tree_low.column("stock", width=60, anchor="center")
        self.tree_low.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=(0, 10))
        scroll_low.configure(command=self.tree_low.yview)

    def create_kpi_card(self, parent, row, col, title, default_val, text_color, padx, command=None):
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.grid(row=row, column=col, sticky="nsew", padx=padx, pady=(0, 12))
        
        lbl_title = ctk.CTkLabel(card, text=title, font=("Segoe UI", 13, "bold"), text_color="gray70")
        lbl_title.pack(pady=(12, 2))
        
        lbl_val = ctk.CTkLabel(card, text=default_val, font=("Arial", 24, "bold"), text_color=text_color)
        lbl_val.pack(pady=(0, 5))
        
        if command:
            btn_view = ctk.CTkButton(card, text="Xem chi tiết 🔍", font=("Arial", 11), 
                                     height=24, width=100, fg_color="#374151", 
                                     hover_color="#4b5563", command=command)
            btn_view.pack(pady=(0, 12))
            
        return lbl_val

    def update_kpi(self, revenue, profit, orders, cash, transfer, low_stock):
        self.lbl_revenue.configure(text=f"{revenue:,.0f} đ")
        self.lbl_profit.configure(text=f"{profit:,.0f} đ")
        self.lbl_orders.configure(text=f"{orders} đơn")
        self.lbl_cash.configure(text=f"{cash:,.0f} đ")
        self.lbl_transfer.configure(text=f"{transfer:,.0f} đ")
        self.lbl_low_stock.configure(text=f"{low_stock} SP")

    def draw_trend_chart(self, x_data, y_data, current_filter):
        for widget in self.canvas_trend_frame.winfo_children():
            widget.destroy()
            
        fig = Figure(figsize=(5, 2.8), dpi=100)
        fig.patch.set_facecolor('#2b2b2b')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#2b2b2b')
        
        title_map = {"Hôm nay": "Doanh thu theo Giờ", "7 ngày qua": "Doanh thu 7 Ngày gần đây", 
                     "Tháng này": "Doanh thu các Ngày trong tháng", "Tất cả": "Doanh thu các Tháng"}
        self.lbl_trend_title.configure(text=f"📈 {title_map.get(current_filter, 'Xu hướng doanh thu')}")
        
        if not x_data or sum(y_data) == 0:
            ax.text(0.5, 0.5, "Không có dữ liệu thời gian này", ha='center', va='center', color='gray', fontsize=11)
            ax.axis('off')
        else:
            bars = ax.bar(x_data, y_data, color='#3498db', width=0.3 if len(x_data) < 5 else 0.5)
            ax.get_yaxis().set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
            
            if len(x_data) == 1:
                ax.set_xlim(-1.5, 1.5)
            elif len(x_data) == 2:
                ax.set_xlim(-0.8, 1.8)
            
            for bar in bars:
                yval = bar.get_height()
                if yval > 0:
                    if yval >= 1000000:
                        text_val = f"{yval/1000000:.1f}Tr"
                    elif yval >= 1000:
                        text_val = f"{yval/1000:.0f}K"
                    else:
                        text_val = f"{int(yval)}"
                        
                    ax.text(bar.get_x() + bar.get_width()/2, yval, text_val, 
                            ha='center', va='bottom', color='#f1c40f', fontsize=9, fontweight='bold')
            
            ax.tick_params(colors='white', labelsize=9)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('gray')
            ax.spines['bottom'].set_color('gray')
            ax.yaxis.grid(True, linestyle='--', alpha=0.3, color='gray')
            ax.set_axisbelow(True)
            
            if len(x_data) > 6:
                ax.set_xticklabels(x_data, rotation=30, ha='right')
        
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_trend_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def draw_pie_chart(self, labels, sizes):
        for widget in self.canvas_pie_frame.winfo_children():
            widget.destroy()
            
        # Tăng kích thước tổng thể để chữ to không bị tràn
        fig = Figure(figsize=(9, 4.5), dpi=100)
        fig.patch.set_facecolor('#2b2b2b')
        ax = fig.add_subplot(111)
        
        if sum(sizes) == 0:
            ax.text(0.5, 0.5, "Chưa có dữ liệu danh mục", ha='center', va='center', color='gray', fontsize=11)
            ax.axis('off')
        else:
            colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0', '#ffb3e6']
            wedges, texts, autotexts = ax.pie(sizes, autopct='%1.1f%%', startangle=140, colors=colors,
                   textprops=dict(color="w", fontsize=16, fontweight='bold'),
                   wedgeprops={'edgecolor': '#2b2b2b', 'linewidth': 1.2},
                   pctdistance=0.75)
            ax.axis('equal')
            
            # Chú thích to hơn 3 cỡ (16) và sát cạnh biểu đồ
            legend = ax.legend(wedges, labels,
                              loc="center left", 
                              bbox_to_anchor=(0.98, 0.5), 
                              frameon=False,
                              fontsize=16,
                              handletextpad=0.5)
            
            # Đổi màu chữ của chú thích thành màu trắng để hiển thị tốt trên Dark Mode
            for text in legend.get_texts():
                text.set_color("white")
            
        # Dành 50% diện tích cho biểu đồ và 50% cho phần chú thích chữ lớn
        fig.subplots_adjust(top=0.95, bottom=0.05, left=0.05, right=0.5)
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_pie_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def update_treeview(self, data):
        for item in self.tree_top.get_children():
            self.tree_top.delete(item)
        for row in data:
            self.tree_top.insert("", "end", values=row)

    def update_low_stock_treeview(self, data):
        for item in self.tree_low.get_children():
            self.tree_low.delete(item)
        for row in data:
            self.tree_low.insert("", "end", values=row)