import os
import sqlite3

# Đường dẫn tuyệt đối (hoặc tương đối) đến file SQLite và file schema SQL
DB_PATH       = r"H:\My Drive\01.UIT\HK7\03.DOAN\QLNHATRO\RentalManagementApplication\backend\database\rent_house_database.sqlite"
SCHEMA_SQL    = r"H:\My Drive\01.UIT\HK7\03.DOAN\QLNHATRO\RentalManagementApplication\backend\database\init_db.sql"

def database_exists_and_initialized(db_path: str) -> bool:
    """
    Kiểm tra xem file SQLite đã tồn tại và bảng LandlordAnalytics đã được tạo hay chưa.
    Nếu file chưa tồn tại, return False.
    Nếu file tồn tại nhưng chưa có table LandlordAnalytics, return False.
    Ngược lại return True.
    """
    if not os.path.isfile(db_path):
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Kiểm tra bảng LandlordAnalytics có tồn tại hay không
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='LandlordAnalytics';
        """)
        row = cursor.fetchone()
        conn.close()
        return (row is not None)
    except Exception as e:
        print(f"[database_exists_and_initialized] Lỗi khi kiểm tra: {e}")
        return False

def initialize_database():
    """
    Nếu lần đầu run (chưa có file hoặc chưa có bảng LandlordAnalytics),
    thì nạp toàn bộ schema từ init_db.sql.
    Còn nếu đã khởi tạo trước đó, sẽ bỏ qua (không exec).
    """
    first_run = not database_exists_and_initialized(DB_PATH)
    if first_run:
        print("ℹ️ Lần đầu khởi tạo database hoặc schema chưa tồn tại. Bắt đầu tạo mới...")
        try:
            # Mở kết nối, bật PRAGMA FK, rồi exec toàn bộ script
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("PRAGMA foreign_keys = ON;")
                with open(SCHEMA_SQL, 'r', encoding='utf-8') as f:
                    sql_script = f.read()
                    conn.executescript(sql_script)
                print("✅ Database schema & triggers đã được khởi tạo thành công.")
        except Exception as e:
            print(f"❌ Lỗi khi khởi tạo schema: {e}")
    else:
        print("ℹ️ Database đã được khởi tạo trước đó. Bỏ qua bước exec schema.")

if __name__ == "__main__":
    initialize_database()
