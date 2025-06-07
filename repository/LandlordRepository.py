import sqlite3
from typing import Optional, List, Dict, Any

from RentalManagementApplication.backend.database.Database import Database
from RentalManagementApplication.backend.model.Landlord import Landlord

db = Database()

class LanlordRepository:




    @staticmethod
    def get_landlord_info_by_username(username: str) -> dict | None:
        """
        Trả về dict thông tin chủ trọ dựa trên Username (1 lần JOIN),
        hoặc None nếu không tìm thấy.
        """
        if not db.connect():
            return None

        query = """
                SELECT l.LandlordID    AS landlord_id, 
                       l.Fullname      AS full_name, 
                       l.Birth         AS birth_date, 
                       l.CCCD          AS citizen_id, 
                       l.Gender        AS gender,
                       l.JobTitle      AS job_title, 
                       l.Email         AS email, 
                       l.PhoneNumber   AS phone_number, 
                       l.HomeAddress   AS home_address, 
                       l.MaritalStatus AS marital_status, 
                       COUNT(r.RoomID) AS room_count
                FROM Landlords l
                         JOIN Users u ON l.UserID = u.UserID
                         LEFT JOIN Rooms r ON r.LandlordID = l.LandlordID
                WHERE u.Username = ?
                GROUP BY l.LandlordID 
                """
        cursor = db.execute(query, (username,))
        row = cursor.fetchone() if cursor else None
        db.close()

        if not row:
            return None

        return {
            "landlord_id": row["landlord_id"],
            "full_name": row["full_name"],
            "birth_date": row["birth_date"],
            "citizen_id": row["citizen_id"],
            "gender": row["gender"],
            "job_title": row["job_title"],
            "email": row["email"],
            "phone_number": row["phone_number"],
            "home_address": row["home_address"],
            "marital_status": row["marital_status"],
            "room_count": row["room_count"],
        }
    '''Đã kiểm tra đồng bộ và chuẩn hóa'''
    @staticmethod
    def get_landlord_by_id(landlord_id: int) -> Optional[Landlord]:
        """
        Lấy tất cả thông tin của chủ trọ (kèm username, số phòng,...)
        Trả về instance Landlord hoặc None nếu không tìm thấy.
        """
        if not db.connect():
            return None

        query = """
                SELECT l.LandlordID    AS LandlordID, 
                       l.Fullname      AS Fullname, 
                       l.Birth         AS Birth, 
                       l.CCCD          AS CCCD, 
                       l.Gender        AS Gender, 
                       l.JobTitle      AS JobTitle, 
                       l.MaritalStatus AS MaritalStatus, 
                       l.Email         AS Email, 
                       l.PhoneNumber   AS PhoneNumber, 
                       l.HomeAddress   AS HomeAddress, 
                       l.UserID        AS UserID, 
                       u.Username      AS Username, 
                       COUNT(r.RoomID) AS so_phong
                FROM Landlords l
                         LEFT JOIN Users u ON l.UserID = u.UserID
                         LEFT JOIN Rooms r ON r.LandlordID = l.LandlordID
                WHERE l.LandlordID = ?
                GROUP BY l.LandlordID 
                """
        cursor = db.execute(query, (landlord_id,))
        row = cursor.fetchone() if cursor else None
        db.close()

        if not row:
            return None

        # sqlite3.Row hỗ trợ dict-like access
        data = dict(row)
        return Landlord(data)

    @staticmethod
    def create_empty_landlord(user_id: int) -> Optional[Landlord]:
        """
        Tạo một landlord “rỗng” với tất cả các trường là chuỗi rỗng hoặc None,
        dùng khi mới đăng ký tài khoản chưa cập nhật thông tin.
        """
        return LanlordRepository.add_landlord_to_db(
            user_id=user_id,
            full_name="",
            birth=None,
            cccd="",
            gender="",
            job_title="",
            marital_status="Other",
            email="",
            phone_number="",
            home_address=""
        )

    @staticmethod
    def add_landlord_to_db(
            user_id: int,
            full_name: str,
            birth: Optional[str],
            cccd: str,
            gender: str,
            job_title: str,
            marital_status: str,
            email: str,
            phone_number: str,
            home_address: str
    ) -> Optional[Landlord]:
        """
        Thêm một landlord mới vào CSDL với đầy đủ các thông tin.
        Trả về instance Landlord nếu thành công, hoặc None nếu có lỗi.
        """
        if not db.connect():
            return None

        try:
            insert_sql = """
                         INSERT INTO Landlords(UserID, Fullname, Birth, CCCD, Gender, 
                                               JobTitle, MaritalStatus, Email, PhoneNumber, 
                                               HomeAddress, CreatedAt) 
                         VALUES (?, ?, ?, ?, ?, 
                                 ?, ?, ?, ?, ?, 
                                 datetime('now', 'localtime')); 
                         """
            params = (
                user_id,
                full_name,
                birth,
                cccd,
                gender,
                job_title,
                marital_status,
                email,
                phone_number,
                home_address
            )
            cursor = db.execute(insert_sql, params)
            if not cursor:
                db.close()
                return None

            landlord_id = cursor.lastrowid
            row = db.execute(
                "SELECT * FROM Landlords WHERE LandlordID = ?",
                (landlord_id,)
            ).fetchone()
            db.close()

            if row:
                # sqlite3.Row được chuyển thành dict để khởi tạo model
                return Landlord(dict(row))
            return None

        except Exception as e:
            print(f"[LandlordRepository.add_landlord_to_db] Lỗi khi thêm landlord: {e}")

    @staticmethod
    def get_all_landlords() -> list[Landlord]:
        """
        Lấy tất cả chủ trọ, kèm Username, đếm số phòng, lấy cả CreatedAt.
        Trả về list[Landlord].
        """
        if not db.connect():
            return []

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
                       COUNT(r.RoomID) AS so_phong,  
                       l.CreatedAt     AS CreatedAt
                FROM Landlords AS l
                         LEFT JOIN Users AS u ON l.UserID = u.UserID
                         LEFT JOIN Rooms AS r ON l.LandlordID = r.LandlordID
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
                         u.Username,  
                         l.CreatedAt
                ORDER BY l.LandlordID;  
                """
        cursor = db.execute(query)
        rows = cursor.fetchall() if cursor else []
        db.close()

        landlords: list[Landlord] = []
        for row in rows:
            # row là sqlite3.Row, nên có thể truy cập row["Fullname"], row["CreatedAt"], ...
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
                "so_phong": row["so_phong"],
                "CreatedAt": row["CreatedAt"]
            }
            landlords.append(Landlord(data))
        return landlords

    @staticmethod
    def get_landlord_id_by_user_id(user_id: int) -> int | None:
        """
        Trả về LandlordID tương ứng với UserID, hoặc None nếu không tìm thấy.
        """
        query = "SELECT LandlordID FROM Landlords WHERE UserID = ?"
        # Bảng Landlords có cột UserID liên kết tới Users(UserID) :contentReference[oaicite:0]{index=0}
        db.connect()
        cursor = db.execute(query, (user_id,))
        row = cursor.fetchone()
        db.close()
        return row["LandlordID"] if row else None

    @staticmethod
    def get_id_landlord_from_user_id(user_id: int) -> Optional[int]:
        """
        Lấy LandlordID dựa vào UserID.
        """
        if not db.connect():
            return None

        query = "SELECT LandlordID FROM Landlords WHERE UserID = ?;"
        cursor = db.execute(query, (user_id,))
        row = cursor.fetchone() if cursor else None
        db.close()
        return row["LandlordID"] if row else None

    #-------------Lanlord Home --------------

    @staticmethod
    def get_total_income_from_all_of_rooms(id_landlord):
        db.connect()
        query = """
                SELECT SUM(TotalRoomPrice + TotalElectronicCost + TotalWaterCost +
                           InternetFee + TotalGarbageFee + TotalAnotherFee - Discount)
                FROM Invoices
                WHERE LandlordID = ?  
                """
        cursor = db.execute(query, (id_landlord,))

        if cursor is None:
            print("⚠️ [Fallback] Không thể truy vấn bảng Invoices. Trả về sample mẫu.")
            db.close()
            return 50_000_000  # SAMPLE

        result = cursor.fetchone()
        db.close()
        if not result or result[0] is None:
            print("⚠️ [Sample] Không có dữ liệu, trả về tổng thu nhập mẫu.")
            return 50_000_000  # sample

        return result[0]

    @staticmethod
    def get_total_income_last_month(id_landlord):
        try:
            db.connect()
            query = """
                    SELECT COALESCE(
                                   SUM(
                                           TotalRoomPrice
                                               + TotalElectronicCost
                                               + TotalWaterCost
                                               + InternetFee
                                               + TotalGarbageFee
                                               + TotalAnotherFee
                                               - Discount
                                   ),
                                   0
                           ) AS total_income
                    FROM Invoices
                    WHERE LandlordID = ?
                      AND strftime('%m-%Y', issue_date)
                        = strftime('%m-%Y', 'now', 'start of month', '-1 month') \
                    """
            cursor = db.execute(query, (id_landlord,))
            row = cursor.fetchone()
            if row is None:
                print(f"[LỖI] Không có kết quả trả về cho LandlordID={id_landlord}")
                return 0
            # row[0] đã chắc chắn là số (0 nếu không có bản ghi)
            return row[0]

        except Exception as e:
            print(f"[LỖI] get_total_income_last_month(): {e}")
            return 0

        finally:
            db.close()

    @staticmethod
    def get_data_for_handel_percent_income(id_landlord):
        db.connect()
        query = """
                SELECT SUM(CASE  
                               WHEN strftime('%m-%Y', issue_date) = strftime('%m-%Y', date('now','start of month','-1 month'))  
                                   THEN TotalRoomPrice + TotalElectronicCost + TotalWaterCost + InternetFee +  
                                        TotalGarbageFee + TotalAnotherFee - Discount  
                               ELSE 0 END) AS last_month,  
                       SUM(CASE  
                               WHEN strftime('%m-%Y', issue_date) = strftime('%m-%Y', date('now','start of month','-2 month'))  
                                   THEN TotalRoomPrice + TotalElectronicCost + TotalWaterCost + InternetFee +  
                                        TotalGarbageFee + TotalAnotherFee - Discount  
                               ELSE 0 END) AS month_before
                FROM Invoices
                WHERE LandlordID = ?  
                """
        cursor = db.execute(query, (id_landlord,))
        result = cursor.fetchone()
        db.close()
        """if not result or result[0] is None or result[1] is None:
            print("⚠️ [Sample] Không có dữ liệu hai tháng gần nhất, trả mẫu.")
            return (30_000_000, 28_000_000)"""

        return result
        #return income_last_month,income_last_month_sub_1

    @staticmethod
    def get_total_number_room_have_invoice_not_complete(id_landlord):
        db.connect()
        query = """
                SELECT COUNT(*)
                FROM Invoices
                WHERE LandlordID = ?  
                  AND Status = 'Chưa thanh toán'  
                """
        cursor = db.execute(query, (id_landlord,))
        total_current = cursor.fetchone()[0] if cursor else 0

        query_last_month = """
                           SELECT COUNT(*)
                           FROM Invoices
                           WHERE LandlordID = ?  
                             AND Status = 'Chưa thanh toán'
                             AND strftime('%m-%Y', issue_date) = strftime('%m-%Y', date('now','start of month','-1 month'))  
                           """
        cursor = db.execute(query_last_month, (id_landlord,))
        total_last = cursor.fetchone()[0] if cursor else 0
        db.close()
        return total_current, total_last

    @staticmethod
    def get_to_total_number_not_tenant(id_landlord):
        db.connect()

        # Phòng hiện tại không có người thuê
        query = """
                SELECT COUNT(*)  
                FROM Rooms
                WHERE LandlordID = ?  
                  AND TenantID IS NULL  
                """
        cursor = db.execute(query, (id_landlord,))
        total_current = cursor.fetchone()[0] if cursor else 0

        # Phòng tháng trước cũng trống: RentalDate là NULL hoặc đã từng null trong tháng trước
        # Lấy số phòng mà:
        # 1. Hiện tại không có Tenant
        # 2. Và tháng trước vẫn chưa có tenant (RentalDate IS NULL hoặc < đầu tháng hiện tại)
        query_last_month = """
                           SELECT COUNT(*)  
                           FROM Rooms
                           WHERE LandlordID = ?
                             AND TenantID IS NULL
                             AND (
                               RentalDate IS NULL OR
                               strftime('%Y-%m', RentalDate) <= strftime('%Y-%m', date('now', 'start of month', '-1 month'))
                               )  
                           """
        cursor = db.execute(query_last_month, (id_landlord,))
        total_last = cursor.fetchone()[0] if cursor else 0

        db.close()

        """# Nếu không có dữ liệu, trả về dữ liệu mẫu để test
        if total_current == 0 and total_last == 0:
            print("⚠️ [Sample] Không có phòng trống, trả về dữ liệu mẫu.")
            return 2, 3"""

        return total_current, total_last

        #return total_number_room_not_teant,total_rooms_not_tenant_last_month
    # -------------Lanlord Infor --------------
    @staticmethod
    def get_infor_lanlord(id_landlord):
        """
        Lấy thông tin chi tiết của chủ trọ:
          - name       : Fullname
          - birth      : Birth
          - cccd       : CCCD
          - sex        : Gender
          - job        : JobTitle
          - phone      : PhoneNumber
          - email      : Email
          - marriage   : MaritalStatus
          - password   : để mặc định là '**********' (không trả về mật khẩu thực)
        """
        try:
            # Kết nối đến DB
            if not db.connect():
                return None

            query = """
                    SELECT Fullname,  
                           Birth,  
                           CCCD,  
                           Gender,  
                           JobTitle,  
                           Email,  
                           PhoneNumber,  
                           MaritalStatus
                    FROM Landlords
                    WHERE LandlordID = ?  
                    """
            cursor = db.execute(query, (id_landlord,))
            row = cursor.fetchone() if cursor else None
            db.close()

            if not row:
                # Nếu không có kết quả, trả về None hoặc dict mặc định
                return None

            # Đọc kết quả từ row (sqlite3.Row) và trả về dict theo key mà UI mong đợi
            return {
                'name': row['Fullname'],
                'birth': row['Birth'],
                'cccd': row['CCCD'],
                'sex': row['Gender'],
                'job': row['JobTitle'],
                'phone': row['PhoneNumber'],
                'email': row['Email'],
                'marriage': row['MaritalStatus'],
                # Ở đây ta không tiết lộ mật khẩu, cứ để là ký tự ẩn
            }
        except Exception as e:
            print(f"[LanlordRepository.get_infor_lanlord] Lỗi khi truy vấn: {e}")
            try:
                db.close()
            except:
                pass
            return None

    @staticmethod
    def update_field(id_landlord: int, field: str, value) -> bool:
        """
        Cập nhật một trường đơn (field) cho landlord xác định bởi LandlordID.
        Ví dụ: update_field(3, "Email", "new@example.com").
        - Không cho phép update cột CreatedAt tại đây.
        - Trả về True nếu thành công, False nếu có lỗi hoặc field không hợp lệ.
        """
        # Chỉ cho phép update các cột an toàn. Nếu cần thêm, bổ sung vào tập này.
        allowed_fields = {
            "Fullname", "Birth", "CCCD", "Gender",
            "JobTitle", "MaritalStatus", "Email",
            "PhoneNumber", "HomeAddress"
        }
        if field not in allowed_fields:
            print(f"[LandlordRepository.update_field] Trường `{field}` không được phép cập nhật.")
            return False

        if not db.connect():
            return False

        try:
            sql = f"UPDATE Landlords SET {field} = ? WHERE LandlordID = ?;"
            db.execute(sql, (value, id_landlord))
            db.close()
            print(f"[LandlordRepository.update_field] Đã cập nhật `{field}` = {value} cho landlord_id={id_landlord}")
            return True
        except Exception as e:
            print(f"[LandlordRepository.update_field] Lỗi khi update: {e}")
            db.close()
            return False

    @staticmethod
    def update_user_info(user_id: int, data: dict) -> bool:
        """
        Cập nhật thông tin Landlord dựa vào UserID:
        - data là dict có thể chứa: Fullname, Birth, CCCD, Gender, JobTitle, MaritalStatus,
          Email, PhoneNumber, HomeAddress.
        - Không cập nhật CreatedAt, UserID.
        - Trả về True nếu thành công, False nếu có lỗi.
        """
        landlord_id = LanlordRepository.get_id_landlord_from_user_id(user_id)
        if landlord_id is None:
            print(f"[LanlordRepository.update_user_info] Không tìm thấy landlord tương ứng user_id={user_id}")
            return False

        # Tập hợp các cột sẽ update
        fields = []
        values = []
        for key in ("Fullname", "Birth", "CCCD", "Gender", "JobTitle", "MaritalStatus", "Email", "PhoneNumber",
                    "HomeAddress"):
            if key in data and data[key] is not None:
                fields.append(f"{key} = ?")
                values.append(data[key])

        if not fields:
            print(f"[LanlordRepository.update_user_info] Không có trường nào để cập nhật cho landlord_id={landlord_id}")
            return False

        if not db.connect():
            return False

        try:
            sql = f"UPDATE Landlords SET {', '.join(fields)} WHERE LandlordID = ?;"
            values.append(landlord_id)
            db.execute(sql, tuple(values))
            db.close()
            print(f"[LanlordRepository.update_user_info] Đã cập nhật landlord_id={landlord_id} với data={data}")
            return True
        except Exception as e:
            print(f"[LanlordRepository.update_user_info] Lỗi khi UPDATE: {e}")
            db.close()
            return False


    @staticmethod
    def get_landlord_monthly_income(landlord_id):
        try:
            db.connect()
            query = """
                    SELECT month, year, TotalIncome
                    FROM LandlordAnalytics
                    WHERE LandlordID = ?
                    ORDER BY year DESC, month DESC
                        LIMIT 12  
                    """
            cursor = db.execute(query, (landlord_id,))
            if cursor is None:
                print("⚠️ Cursor is None, trả về dữ liệu mẫu")
                return [
                    {'month': '01/2024', 'total_income': 5_000_000},
                    {'month': '02/2024', 'total_income': 6_200_000},
                    {'month': '03/2024', 'total_income': 5_800_000},
                    {'month': '04/2024', 'total_income': 7_500_000},
                    {'month': '05/2024', 'total_income': 8_000_000},
                    {'month': '06/2024', 'total_income': 9_200_000}
                ]

            result = cursor.fetchall()
            db.close()

            if not result:
                print("⚠️ Không có dữ liệu từ database")
                return []

            return [
                {'month': f"{str(row[0]).zfill(2)}/{row[1]}", 'total_income': row[2]}
                for row in result[::-1]
            ]
        except Exception as e:
            print(f"❌ Lỗi get_landlord_monthly_income: {e}")
            return []

    @staticmethod
    def get_landlord_analytics_data(id_landlord: int) -> List[Dict[str, Any]]:
        """
        Lấy dữ liệu analytics (LandlordAnalytics) của một chủ trọ cụ thể,
        trả về list[dict] với các khóa:
          - 'LandlordID'
          - 'month'
          - 'year'
          - 'total_income'
          - 'rented_rooms'
          - 'average_price'
          - 'growth_rate'
        """
        try:
            db.connect()
            query = """
                    SELECT LandlordID, month, year, TotalIncome AS total_income, NumberOfRentedRooms AS rented_rooms, AveragePrice AS average_price, GrowthRate AS growth_rate
                    FROM LandlordAnalytics
                    WHERE LandlordID = ?
                    ORDER BY year DESC, month DESC
                        LIMIT 12  
                    """
            cursor= db.execute(query, (id_landlord,))
            rows = cursor.fetchall()
            analytics_list = []
            for row in rows:
                analytics_list.append({
                    'LandlordID': row['LandlordID'],
                    'month': row['month'],
                    'year': row['year'],
                    'total_income': row['total_income'],
                    'rented_rooms': row['rented_rooms'],
                    'average_price': row['average_price'],
                    'growth_rate': row['growth_rate'],
                })

            db.close()
            return analytics_list

        except Exception as e:
            print(f"[LanlordRepository.get_landlord_analytics_data] Lỗi khi truy vấn: {e}")
            try:
                db.close()
            except:
                pass
            return []

    @staticmethod
    def get_landlord_name_by_id(landlord_id):
        db.connect()
        query = "SELECT Fullname FROM Landlords WHERE LandlordID = ?"
        cursor = db.execute(query, (landlord_id,))
        db.close()
        return cursor["Fullname"] if cursor else "None"

    @staticmethod
    def get_user_id_lanlord_from_lanlord_id(id_lanlord: int):
        """Trả về user_id từ landlord_id"""
        try:
            db.connect()
            query = "SELECT UserID FROM Landlords WHERE LandlordID = ?"
            cursor = db.execute(query, (id_lanlord,))
            row = cursor.fetchone()
            db.close()
            if row:
                return row[0]
            else:
                print(f"⚠️ Không tìm thấy UserID cho LandlordID: {id_lanlord}")
                return None
        except Exception as e:
            print(f"❌ Lỗi khi truy vấn get_user_id_lanlord_from_lanlord_id: {e}")
            return None

    @staticmethod
    def get_landlord_data_for_invoice_view(landlord_id: int) -> Optional[Dict[str, Any]]:
        """
        Lấy dữ liệu chủ trọ cần hiển thị trên hóa đơn, bao gồm:
          - full_name     → Fullname
          - citizen_id    → CCCD
          - address       → HomeAddress hoặc Address (tùy schema)
          - phone         → PhoneNumber
          - email         → Email
        Trả về dict nếu tìm thấy, ngược lại trả về None.
        """
        # 1) Kết nối DB
        if not db.connect():
            return None

        try:
            query = """
                    SELECT Fullname    AS full_name,  
                           CCCD        AS citizen_id,  
                           HomeAddress AS address,  
                           Email       AS email,  
                           PhoneNumber AS phone
                    FROM Landlords
                    WHERE LandlordID = ? LIMIT 1;  
                    """
            cursor = db.execute(query, (landlord_id,))
            row = cursor.fetchone() if cursor else None
            db.close()

            if not row:
                return None

            return {
                "full_name": row["full_name"],
                "citizen_id": row["citizen_id"],
                "address": row["address"],
                "email": row["email"],
                "phone": row["phone"]
            }

        except sqlite3.Error as e:
            print(f"[⚠️ LanlordRepository.get_landlord_data_for_invoice_view] Lỗi truy vấn: {e}")
            db.close()
            return None


