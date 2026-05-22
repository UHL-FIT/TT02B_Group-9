import traceback, datetime
from views.stats_view import StatsView

class StatsController:
    def __init__(self, master, db_instance):
        self.db = db_instance
        self.view = StatsView(master, controller=self)
        
        self.view.time_filter.configure(command=self.load_data_to_dashboard)
        self.load_data_to_dashboard("Tất cả")
    
    def get_view(self):
        return self.view
        
    def load_data_to_dashboard(self, selected_time=None):
        if selected_time is None:
            selected_time = self.view.time_filter.get()

        date_condition = ""
        if selected_time == "Hôm nay":
            date_condition = "AND DATE(s.timestamp) = DATE('now', 'localtime')"
        elif selected_time == "7 ngày qua":
            date_condition = "AND DATE(s.timestamp) >= DATE('now', '-7 days', 'localtime')"
        elif selected_time == "Tháng này":
            date_condition = "AND strftime('%Y-%m', s.timestamp) = strftime('%Y-%m', 'now', 'localtime')"
            
        try:
            # 1. Doanh thu tổng & Giá vốn
            query_kpi = f"""
                SELECT COUNT(DISTINCT s.sale_id), SUM(sd.quantity * sd.unit_price), SUM(sd.quantity * p.price_in)
                FROM Sale_Details sd 
                JOIN Sales s ON sd.sale_id = s.sale_id
                JOIN Products p ON sd.product_barcode = p.barcode
                WHERE 1=1 {date_condition};
            """
            self.db.cursor.execute(query_kpi)
            kpi_data = self.db.cursor.fetchall()
            total_orders = kpi_data[0][0] if kpi_data and kpi_data[0][0] else 0
            total_revenue = kpi_data[0][1] if kpi_data and kpi_data[0][1] else 0
            total_cost = kpi_data[0][2] if kpi_data and kpi_data[0][2] else 0
            profit = total_revenue - total_cost
            
            # 2. Dòng tiền Tiền mặt / Chuyển khoản
            query_payments = f"""
                SELECT payment_method, SUM(total_amount)
                FROM Sales s WHERE 1=1 {date_condition} GROUP BY payment_method;
            """
            self.db.cursor.execute(query_payments)
            payment_data = self.db.cursor.fetchall()
            cash_amount = 0
            transfer_amount = 0
            for method, amount in payment_data:
                if method:
                    method_lower = method.lower()
                    if "tiền mặt" in method_lower or "cash" in method_lower:
                        cash_amount += amount if amount else 0
                    elif "chuyển khoản" in method_lower or "transfer" in method_lower or "banking" in method_lower or "quẹt thẻ" in method_lower:
                        transfer_amount += amount if amount else 0
            
            # ========================================================
            # 3. LẤY SỐ LƯỢNG VÀ DANH SÁCH SẢN PHẨM <= 10
            # ========================================================
            # Lấy hẳn danh sách ra thay vì chỉ lấy hàm đếm COUNT
            query_stock = "SELECT barcode, name, stock FROM Products WHERE stock <= 10 AND is_active = 1 ORDER BY stock ASC;"
            self.db.cursor.execute(query_stock)
            low_stock_data = self.db.cursor.fetchall()
            
            # Số lượng thẻ ghi trên KPI chính là chiều dài của danh sách này
            low_stock_count = len(low_stock_data)
            
            # Đẩy lên giao diện thẻ KPI
            self.view.update_kpi(total_revenue, profit, total_orders, cash_amount, transfer_amount, low_stock_count)
            
            # Đẩy danh sách lên bảng 2 (Tab 2)
            self.view.update_low_stock_treeview(low_stock_data)
            
            # 4. Biểu đồ xu hướng
            trend_x = []
            trend_y = []
            if selected_time == "Hôm nay":
                query_trend = f"SELECT strftime('%H:00', s.timestamp) as Gio, SUM(sd.quantity * sd.unit_price) FROM Sale_Details sd JOIN Sales s ON sd.sale_id = s.sale_id WHERE DATE(s.timestamp) = DATE('now', 'localtime') GROUP BY Gio ORDER BY Gio ASC;"
            elif selected_time == "7 ngày qua" or selected_time == "Tháng này":
                query_trend = f"SELECT strftime('%d-%m', s.timestamp) as Ngay, SUM(sd.quantity * sd.unit_price) FROM Sale_Details sd JOIN Sales s ON sd.sale_id = s.sale_id WHERE 1=1 {date_condition} GROUP BY Ngay ORDER BY DATE(s.timestamp) ASC;"
            else:
                query_trend = f"SELECT strftime('%m/%Y', s.timestamp) as Thang, SUM(sd.quantity * sd.unit_price) FROM Sale_Details sd JOIN Sales s ON sd.sale_id = s.sale_id GROUP BY Thang ORDER BY s.timestamp ASC;"
                
            self.db.cursor.execute(query_trend)
            trend_data = self.db.cursor.fetchall()
            for row in trend_data:
                if row[0] is not None:
                    trend_x.append(row[0])
                    trend_y.append(row[1] if row[1] else 0)
                    
            self.view.draw_trend_chart(trend_x, trend_y, selected_time)
            
            # 5. Top 5 sản phẩm bán chạy (Bảng 1 - Tab 1)
            query_top = f"""
                SELECT p.barcode, p.name, SUM(sd.quantity) as TongBan 
                FROM Sale_Details sd 
                JOIN Products p ON sd.product_barcode = p.barcode 
                JOIN Sales s ON sd.sale_id = s.sale_id
                WHERE 1=1 {date_condition}
                GROUP BY p.barcode ORDER BY TongBan DESC LIMIT 5;
            """
            self.db.cursor.execute(query_top)
            top_products = self.db.cursor.fetchall()
            self.view.update_treeview(top_products)
            
            # 6. Doanh thu theo danh mục
            query_category = f"""
                SELECT p.category, SUM(sd.quantity * sd.unit_price) 
                FROM Sale_Details sd JOIN Products p ON sd.product_barcode = p.barcode JOIN Sales s ON sd.sale_id = s.sale_id
                WHERE 1=1 {date_condition} GROUP BY p.category;
            """
            self.db.cursor.execute(query_category)
            category_data = self.db.cursor.fetchall()
            labels = []
            sizes = []
            for row in category_data:
                if row[0] is not None and row[1] is not None:
                    labels.append(row[0])
                    sizes.append(row[1])
            self.view.draw_pie_chart(labels, sizes)
            
        except Exception as e:
            print(f"Lỗi khi xử lý dữ liệu biểu đồ: {e}")
            traceback.print_exc()

    def show_order_details(self):
        selected_time = self.view.time_filter.get()
        # Lấy dữ liệu chi tiết từ database
        detailed_sales_data = self.db.get_detailed_sales_data(selected_time)
        
        # Hiển thị cửa sổ chi tiết đơn hàng
        from views.stats_view import OrderDetailsDialog # Import ở đây để tránh lỗi vòng lặp
        OrderDetailsDialog(self.view.winfo_toplevel(), f"Chi tiết đơn hàng ({selected_time})", detailed_sales_data)