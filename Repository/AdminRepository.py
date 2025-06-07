from QLNHATRO.RentalManagementApplication.backend.database.Database import Database
from QLNHATRO.RentalManagementApplication.backend.model.Landlord import Landlord
from QLNHATRO.RentalManagementApplication.backend.model.Tenant import Tenant
from QLNHATRO.RentalManagementApplication.backend.model.User import User

db = Database(db_filename="rent_house_database.sqlite")

class AdminRepository:



    @staticmethod
    def get_all_landlords():
        """
        Lấy tất cả chủ trọ từ bảng Landlords (kết hợp Users để lấy username và Rooms để đếm số phòng).
        Trả về: list[Landlord] với đủ các thuộc tính như Landlord.fullname, .cccd, .phone_number, .email, .username, .so_phong, .landlord_id.
        """

        # 1. Khởi tạo Database và kết nối
        connected = db.connect()
        if not connected:
            return []  # Nếu không kết nối được, trả về list rỗng

        # 2. Chạy truy vấn SQL
        query = """
                SELECT l.LandlordID, 
                       l.Fullname, 
                       l.Birth, 
                       l.CCCD, 
                       l.Gender, 
                       l.JobTitle, 
                       l.MaritalStatus, 
                       l.Email, 
                       l.PhoneNumber, 
                       l.HomeAddress, 
                       l.UserID, 
                       u.Username      AS Username, 
                       COUNT(r.RoomID) AS so_phong
                FROM Landlords l
                         LEFT JOIN Users u ON l.UserID = u.UserID
                         LEFT JOIN Rooms r ON l.LandlordID = r.LandlordID
                GROUP BY l.LandlordID, 
                         l.Fullname, 
                         l.Birth, 
                         l.CCCD, 
                         l.Gender, 
                         l.JobTitle, 
                         l.MaritalStatus, 
                         l.Email, 
                         l.PhoneNumber, 
                         l.HomeAddress, 
                         l.UserID, 
                         u.Username
                ORDER BY l.LandlordID 
                """
        cursor = db.execute(query)
        rows = cursor.fetchall() if cursor else []
        db.close()

        # 3. Chuyển mỗi row thành model Landlord
        landlords = []
        for row in rows:
            # Vì Database.conn.row_factory = sqlite3.Row, ta có thể truy cập theo tên cột
            data = {
                "LandlordID": row["LandlordID"],
                "Fullname": row["Fullname"],
                "Birth": row["Birth"],
                "CCCD": row["CCCD"],
                "Gender": row["Gender"],
                "JobTitle": row["JobTitle"],
                "MaritalStatus": row["MaritalStatus"],
                "Email": row["Email"],
                "PhoneNumber": row["PhoneNumber"],
                "HomeAddress": row["HomeAddress"],
                "UserID": row["UserID"],
                "Username": row["Username"],
                "so_phong": row["so_phong"]
            }
            landlords.append(Landlord(data))
        return landlords

    @staticmethod
    def get_all_tenants():
        """
        Lấy tất cả người thuê (Tenants) từ bảng Tenants,
        kết hợp với bảng Users để lấy Username.
        Trả về list[Tenant] (model), mỗi object chứa:
         - tenant_id
         - fullname
         - birth
         - cccd
         - gender
         - job_title
         - marital_status
         - email
         - phone_number
         - home_address
         - rent_start_date
         - rent_end_date
         - user_id
         - username (từ Users)
        """

        # 1. Khởi tạo Database và kết nối
        conn_obj = db.connect()  # trả về sqlite3.Connection nếu thành công, ngược lại None
        if not conn_obj:
            return []

        # 2. Query lấy thông tin Tenant + Username
        query = """
                SELECT t.TenantID, 
                       t.Fullname, 
                       t.Birth, 
                       t.CCCD, 
                       t.Gender, 
                       t.JobTitle, 
                       t.MaritalStatus, \
                       t.Email, \
                       t.PhoneNumber, \
                       t.HomeAddress, \
                       t.RentStartDate, 
                       t.RentEndDate, 
                       t.UserID, \
                       u.Username AS Username
                FROM Tenants t
                         LEFT JOIN Users u ON t.UserID = u.UserID
                ORDER BY t.TenantID \
                """
        cursor = db.execute(query)
        rows = cursor.fetchall() if cursor else []
        db.close()

        # 3. Chuyển mỗi row thành object Tenant
        tenants = []
        for row in rows:
            # Vì Database.conn.row_factory mặc định trả về tuple, ta truy cập theo index
            data = {
                "TenantID": row[0],
                "Fullname": row[1],
                "Birth": row[2],
                "CCCD": row[3],
                "Gender": row[4],
                "JobTitle": row[5],
                "MaritalStatus": row[6],
                "Email": row[7],
                "PhoneNumber": row[8],
                "HomeAddress": row[9],
                "RentStartDate": row[10],
                "RentEndDate": row[11],
                "UserID": row[12],
                "Username": row[13]
            }
            tenants.append(Tenant(data))
        return tenants

    @staticmethod
    def count_landlords_by_month(month, year):
        """
        Đếm số lượng chủ trọ được tạo theo tháng/năm từ cột CreatedAt trong bảng Landlords.
        """
        db.connect()
        query = """
                SELECT COUNT(*) \
                FROM Landlords
                WHERE strftime('%m', CreatedAt) = ? \
                  AND strftime('%Y', CreatedAt) = ? \
                """
        cursor = db.execute(query, (f"{int(month):02d}", str(year)))
        result = cursor.fetchone()[0] if cursor else 0
        db.close()
        return result

    @staticmethod
    def count_tenants_by_month(month, year):
        """
        Đếm số lượng người thuê được tạo theo tháng/năm từ cột CreatedAt trong bảng Tenants.
        """
        db.connect()
        query = """
                SELECT COUNT(*) \
                FROM Tenants
                WHERE strftime('%m', CreatedAt) = ? \
                  AND strftime('%Y', CreatedAt) = ? \
                """
        cursor = db.execute(query, (f"{int(month):02d}", str(year)))
        result = cursor.fetchone()[0] if cursor else 0
        db.close()
        return result

    @staticmethod
    def count_rooms_by_month(month, year):
        """
        Đếm số phòng tạo mới theo tháng/năm dựa trên RentalDate (ngày bắt đầu cho thuê).
        """
        db.connect()
        query = """
                SELECT COUNT(*) \
                FROM Rooms
                WHERE RentalDate IS NOT NULL
                  AND strftime('%m', RentalDate) = ? \
                  AND strftime('%Y', RentalDate) = ? \
                """
        cursor = db.execute(query, (f"{int(month):02d}", str(year)))
        result = cursor.fetchone()[0] if cursor else 0
        db.close()
        return result

    @staticmethod
    def get_system_stats_by_month():
        """
        Thống kê số lượng landlord, tenant, room, invoice theo từng tháng.
        Trả về danh sách dict theo tháng có định dạng: {"month": "MM/YYYY", "landlord": ..., "tenant": ..., "room": ..., "invoice": ...}
        """
        db.connect()
        query = """
                WITH months AS (SELECT '01' AS m \
                                UNION SELECT '02' UNION SELECT '03' UNION SELECT '04' NION SELECT '05' \
                                UNION SELECT '06' UNION SELECT '07' UNION SELECT '08' UNION SELECT '09' \
                                UNION SELECT '10' UNION SELECT '11' UNION SELECT '12')
                SELECT printf('%02d/%d', m, y) AS month,
              (SELECT COUNT(*) FROM Landlords
                 WHERE CreatedAt IS NOT NULL
                   AND strftime('%m', CreatedAt) = printf('%02d', m)
                   AND strftime('%Y', CreatedAt) = y
              ) AS landlord,
              (SELECT COUNT(*) FROM Tenants
                 WHERE CreatedAt IS NOT NULL
                   AND strftime('%m', CreatedAt) = printf('%02d', m)
                   AND strftime('%Y', CreatedAt) = y
              ) AS tenant,
              (SELECT COUNT(*) FROM Rooms
                 WHERE RentalDate IS NOT NULL
                   AND strftime('%m', RentalDate) = printf('%02d', m)
                   AND strftime('%Y', RentalDate) = y
              ) AS room,
              (SELECT COUNT(*) FROM Invoices
                 WHERE issue_date IS NOT NULL
                   AND strftime('%m', issue_date) = printf('%02d', m)
                   AND strftime('%Y', issue_date) = y
              ) AS invoice
                FROM months, (
                    SELECT DISTINCT CAST (strftime('%Y', CreatedAt) AS INTEGER) AS y FROM Landlords
                    WHERE CreatedAt IS NOT NULL
                    UNION
                    SELECT DISTINCT CAST (strftime('%Y', CreatedAt) AS INTEGER) FROM Tenants
                    WHERE CreatedAt IS NOT NULL
                    UNION
                    SELECT DISTINCT CAST (strftime('%Y', RentalDate) AS INTEGER) FROM Rooms
                    WHERE RentalDate IS NOT NULL
                    UNION
                    SELECT DISTINCT CAST (strftime('%Y', issue_date) AS INTEGER) FROM Invoices
                    WHERE issue_date IS NOT NULL
                    ) years
                ORDER BY y, m  
                """

        cursor = db.execute(query)
        result = []
        if cursor:
            for row in cursor.fetchall():
                result.append({
                    "month": row["month"],
                    "landlord": row["landlord"],
                    "tenant": row["tenant"],
                    "room": row["room"],
                    "invoice": row["invoice"]
                })
        db.close()
        return result

