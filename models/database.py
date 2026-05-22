import sqlite3
import os 
import sys 
import pandas as pd
import numpy as np
from utils.logger import setup_logger 
from datetime import datetime # Đã sửa lại import datetime cho chuẩn

logger = setup_logger()

if getattr(sys, 'frozen', False): 
    _USER_DIR = os.path.join(os.path.expanduser("~"), "Supermarket_Data")
    _BASE_DIR = _USER_DIR
    _USER_DATA = os.path.join(_BASE_DIR, "data")
    
    if not os.path.exists(_USER_DATA):
        os.makedirs(_USER_DATA, exist_ok=True)
else:
    _BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    _USER_DATA = os.path.join(_BASE_DIR, "data")
    if not os.path.exists(_USER_DATA):
        os.makedirs(_USER_DATA, exist_ok=True)

DB_FILE = os.path.join(_USER_DATA, "supermarket.db") 

class SupermarketDB:
    def __init__(self):
        self.db_path = DB_FILE
        self.conn = sqlite3.connect(self.db_path) 
        self.cursor = self.conn.cursor()          
        self.create_tables()
        logger.info(f"Kết nối Database thành công tại: {self.db_path}") 

    def create_tables(self):
        """Khởi tạo cấu trúc các bảng trong hệ thống"""
        # 1. Bảng Sản phẩm (Kho hàng)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Products (
                barcode TEXT PRIMARY KEY,       
                name TEXT NOT NULL,             
                category TEXT,                  
                price_in REAL DEFAULT 0,        
                price_out REAL DEFAULT 0,       
                stock INTEGER DEFAULT 0,        
                min_stock INTEGER DEFAULT 5,    
                unit TEXT,                      
                image_path TEXT DEFAULT '',     -- ĐÃ SỬA: Thêm dấu phẩy ở đây để không bị lỗi SQL
                is_pinned INTEGER DEFAULT 0,    
                is_active INTEGER DEFAULT 1,    
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 2. Bảng Hóa đơn
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Sales (
                sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,        
                total_amount REAL NOT NULL,     
                payment_method TEXT,            
                customer_pay REAL,              
                change_amount REAL              
            )
        """)

        # 3. Bảng Chi tiết hóa đơn
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Sale_Details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER,
                product_barcode TEXT,
                quantity INTEGER,
                unit_price REAL,                
                FOREIGN KEY(sale_id) REFERENCES Sales(sale_id),
                FOREIGN KEY(product_barcode) REFERENCES Products(barcode)
            )
        """)
        self.conn.commit()

    # ================= QUẢN LÝ KHO HÀNG (INVENTORY) =================

    def add_product(self, data):
        """ Thêm 1 sản phẩm vào kho """
        try:
            # Data truyền vào phải có 9 giá trị tương ứng
            query = """INSERT INTO Products 
                       (barcode, name, category, price_in, price_out, stock, min_stock, unit, image_path) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
            self.cursor.execute(query, data)
            self.conn.commit()
            logger.info(f"Đã thêm sản phẩm: {data[1]} ({data[0]})")
            return True, "Thêm sản phẩm thành công!"
        except sqlite3.IntegrityError:
            logger.error(f"Lỗi thêm sản phẩm: Mã hàng {data[0]} đã tồn tại.")
            return False, "Mã hàng đã tồn tại!"
        except Exception as e:
            logger.error(f"Lỗi database: {e}")
            return False, f"Lỗi hệ thống: {e}"

    def update_product(self, barcode, updates):
        """ Cập nhật thông tin sản phẩm """
        try:
            keys = list(updates.keys())
            values = list(updates.values())
            set_query = ", ".join([f"{k} = ?" for k in keys])
            values.append(barcode)
            
            query = f"UPDATE Products SET {set_query} WHERE barcode = ?"
            self.cursor.execute(query, values)
            self.conn.commit()
            logger.info(f"Đã cập nhật sản phẩm: {barcode}")
            return True, "Cập nhật thành công!"
        except Exception as e:
            logger.error(f"Lỗi cập nhật sản phẩm {barcode}: {e}")
            return False, f"Lỗi hệ thống: {e}"

    def delete_product_soft(self, barcode):
        """Xóa mềm 1 sản phẩm"""
        try:
            self.cursor.execute("UPDATE Products SET is_active = 0 WHERE barcode = ?", (barcode,))
            self.conn.commit()
            logger.info(f"Đã xóa mềm sản phẩm: {barcode}")
            return True, "Đã ngừng kinh doanh mặt hàng này!"
        except Exception as e:
            logger.error(f"Lỗi xóa sản phẩm {barcode}: {e}")
            return False, f"Lỗi: {e}"

    def delete_multiple_products_soft(self, barcode_list):
        """Tính năng mở rộng: Xóa mềm nhiều sản phẩm cùng lúc"""
        if not barcode_list:
            return False, "Danh sách rỗng!"
        try:
            placeholders = ",".join("?" * len(barcode_list))
            query = f"UPDATE Products SET is_active = 0 WHERE barcode IN ({placeholders})"
            self.cursor.execute(query, barcode_list)
            self.conn.commit()
            logger.info(f"Đã xóa mềm {len(barcode_list)} sản phẩm.")
            return True, f"Đã xóa {len(barcode_list)} mặt hàng thành công!"
        except Exception as e:
            logger.error(f"Lỗi xóa nhiều sản phẩm: {e}")
            return False, f"Lỗi hệ thống: {e}"

    def get_all_products(self, active_only=True):
        """Lấy danh sách hàng, ưu tiên hàng được GHIM lên đầu"""
        query = "SELECT * FROM Products "
        if active_only:
            query += "WHERE is_active = 1 "
        query += "ORDER BY is_pinned DESC, name ASC"
        
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def search_products(self, keyword):
        """Tìm kiếm theo mã hoặc tên (chỉ hàng đang kinh doanh)"""
        query = """SELECT * FROM Products 
                   WHERE (name LIKE ? OR barcode LIKE ?) AND is_active = 1
                   ORDER BY is_pinned DESC"""
        self.cursor.execute(query, (f'%{keyword}%', f'%{keyword}%'))
        return self.cursor.fetchall()

    def export_inventory_csv(self, file_path):
        """Sử dụng Pandas để lấy dữ liệu từ DB và xuất ra file CSV"""
        try:
            # ĐÃ SỬA: Thêm cột image_path vào câu lệnh xuất
            query = "SELECT barcode, name, category, price_in, price_out, stock, unit, image_path FROM Products WHERE is_active = 1"
            df = pd.read_sql_query(query, self.conn)
            df.to_csv(file_path, index=False, encoding='utf-8-sig', sep=';')
            logger.info(f"Đã xuất dữ liệu kho ra file: {file_path}")
            return True, "Xuất file CSV thành công!"
        except Exception as e:
            logger.error(f"Lỗi xuất CSV: {e}")
            return False, f"Lỗi xuất file: {e}"

    def import_inventory_csv(self, file_path):
        """Đọc CSV cập nhật SQLite có hỗ trợ cột ảnh."""
        try:
            df = pd.read_csv(file_path, sep=';', encoding='utf-8-sig')
            df = df.astype(object)
            df = df.where(pd.notnull(df), None)

            # Nếu file CSV cũ không có cột image_path, tạo sẵn một cột rỗng để tránh lỗi
            if 'image_path' not in df.columns:
                df['image_path'] = ''

            required_columns = ['barcode', 'name', 'category', 'price_in', 'price_out', 'stock', 'unit']
            for col in required_columns:
                if col not in df.columns:
                    return False, f"File CSV thiếu cột: {col}"

            cursor = self.conn.cursor()
            count_updated = 0
            count_inserted = 0

            for _, row in df.iterrows():
                barcode_raw = row['barcode']
                if barcode_raw is None:
                    continue
                
                barcode = str(barcode_raw).strip()
                if barcode == "":
                    continue

                # Lấy giá trị ảnh, nếu None thì gán chuỗi rỗng
                img_path = row['image_path'] if row['image_path'] else ''

                cursor.execute("SELECT barcode FROM Products WHERE barcode = ?", (barcode,))
                exists = cursor.fetchone()

                if exists:
                    # ĐÃ SỬA: Cập nhật thêm cột image_path
                    query = """
                        UPDATE Products 
                        SET name = ?, category = ?, price_in = ?, price_out = ?, stock = ?, unit = ?, image_path = ?, is_active = 1
                        WHERE barcode = ?
                    """
                    cursor.execute(query, (
                        row['name'], row['category'], row['price_in'], 
                        row['price_out'], row['stock'], row['unit'], img_path, barcode
                    ))
                    count_updated += 1
                else:
                    # ĐÃ SỬA: Insert thêm cột image_path
                    query = """
                        INSERT INTO Products (barcode, name, category, price_in, price_out, stock, unit, image_path, is_active)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
                    """
                    cursor.execute(query, (
                        barcode, row['name'], row['category'], 
                        row['price_in'], row['price_out'], row['stock'], row['unit'], img_path
                    ))
                    count_inserted += 1

            self.conn.commit()
            return True, f"Thành công! Thêm mới: {count_inserted}, Cập nhật: {count_updated}"

        except Exception as e:
            if self.conn:
                self.conn.rollback()
            logger.error(f"Lỗi xử lý dữ liệu CSV: {e}")
            return False, f"Lỗi: {str(e)}"
            
    # ================= QUẢN LÝ BÁN HÀNG & THỐNG KÊ =================

    def process_sale(self, cart_items, total_amount, method, guest_pay, change):
        """Lưu hóa đơn và trừ kho đồng thời"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute("""INSERT INTO Sales 
                (timestamp, total_amount, payment_method, customer_pay, change_amount) 
                VALUES (?, ?, ?, ?, ?)""", (timestamp, total_amount, method, guest_pay, change))
            
            sale_id = self.cursor.lastrowid

            for item in cart_items:
                self.cursor.execute("INSERT INTO Sale_Details (sale_id, product_barcode, quantity, unit_price) VALUES (?, ?, ?, ?)",
                                   (sale_id, item[0], item[1], item[2]))
                self.cursor.execute("UPDATE Products SET stock = stock - ? WHERE barcode = ?", (item[1], item[0]))

            self.conn.commit()
            logger.info(f"Giao dịch thành công - Hóa đơn ID: {sale_id} - Tổng tiền: {total_amount}")
            return True, "Thanh toán hoàn tất!"
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Lỗi thanh toán hóa đơn: {e}")
            return False, f"Lỗi hệ thống: {e}"

    def get_revenue_by_date(self, date_str):
        """Lấy doanh thu theo ngày (date_str: 'YYYY-MM-DD')"""
        query = "SELECT SUM(total_amount) FROM Sales WHERE timestamp LIKE ?"
        self.cursor.execute(query, (f'{date_str}%',))
        result = self.cursor.fetchone()[0]
        return result if result else 0

    def __del__(self):
        try:
            self.conn.close()
        except:
            pass