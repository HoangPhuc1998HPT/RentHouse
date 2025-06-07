import sqlite3
from typing import Optional, Dict, Any, List

from QLNHATRO.RentalManagementApplication.backend.database.Database import Database
from QLNHATRO.RentalManagementApplication.backend.model.Tenant import Tenant

db = Database()
class TenantRepository:

    @staticmethod
    def get_tenant_info_by_username(username: str) -> dict | None:
        """
        Trả về dict thông tin tenant (full_name, birth_date, ...) dựa trên Username,
        trong 1 lần JOIN Users ↔ Tenants, hoặc None nếu không tìm thấy.
        """
        if not db.connect():
            return None

        query = """
                SELECT t.TenantID      AS tenant_id,  
                       t.Fullname      AS full_name,  
                       t.Birth         AS birth_date,  
                       t.CCCD          AS citizen_id,  
                       t.Gender        AS gender,  
                       t.JobTitle      AS occupation,  
                       t.Email         AS email,  
                       t.PhoneNumber   AS phone_number,  
                       t.MaritalStatus AS marital_status
                FROM Tenants t
                         JOIN Users u ON t.UserID = u.UserID
                WHERE u.Username = ? LIMIT 1;  
                """
        cursor = db.execute(query, (username,))
        row = cursor.fetchone() if cursor else None
        db.close()

        if not row:
            return None

        return {
            "tenant_id": row["tenant_id"],
            "full_name": row["full_name"],
            "birth_date": row["birth_date"],
            "citizen_id": row["citizen_id"],
            "gender": row["gender"],
            "occupation": row["occupation"],
            "email": row["email"],
            "phone_number": row["phone_number"],
            "marital_status": row["marital_status"],
        }

    @staticmethod
    def create_empty_tenant(user_id: int) -> Optional[Tenant]:
        # Sử dụng add_tenant_to_db, truyền đầy đủ các trường null hoặc rỗng
        return TenantRepository.add_tenant_to_db(
            user_id=user_id,
            full_name="", cccd="", gender="", job_title="", marital_status="Other",
            email="", phone_number="", home_address="", rent_start=None, rent_end=None
        )

    @staticmethod
    def get_room_infor_by_id_tenant(tenant_id: int) -> Optional[Dict[str, Any]]:
        """
        Lấy thông tin phòng ứng với tenant_id:
        Bước 1: Tìm RoomID trong bảng Rooms mà TenantID = tenant_id.
        Bước 2: Dùng RoomID để lấy chi tiết các trường cần thiết.
        Trả về dict với các key như mẫu, hoặc None nếu không tìm thấy.
        """
        # 1) Kết nối DB
        if not db.connect():
            return None

        try:
            # 2) Truy vấn lấy toàn bộ thông tin cần của phòng từ Rooms
            #    với điều kiện Rooms.TenantID = ?
            query = """
                    SELECT r.RoomID                AS id,  
                           r.RoomName              AS room_name,  
                           r.Address               AS address,  
                           r.RoomType              AS room_type,  
                           r.Area                  AS area,  
                           r.RoomPrice             AS rent_price,  
                           r.Deposit               AS deposit,  
                           r.ElectricityPrice      AS electricity_price,  
                           r.WaterPrice            AS water_price,  
                           r.InternetPrice         AS internet_price,  
                           r.GarbageServicePrice   AS garbage_price,  
                           r.OtherFees             AS other_fees,  
                           r.RentalDate            AS available_date,  
                           r.CurrentElectricityNum AS current_electricity,  
                           r.CurrentWaterNum       AS current_water,  
                           r.TenantID              AS tenant_id,  
                           r.LandlordID            AS landlord_id
                    FROM Rooms r
                    WHERE r.TenantID = ? LIMIT 1;  
                    """
            cursor = db.execute(query, (tenant_id,))
            row = cursor.fetchone() if cursor else None

            # 3) Đóng kết nối
            db.close()

            if not row:
                # Nếu không tìm thấy phòng nào gắn với tenant_id đã cho
                return None

            # 4) Chuyển sqlite3.Row thành dict
            result = {
                "id": row["id"],
                "room_name": row["room_name"],
                "address": row["address"],
                "room_type": row["room_type"],
                "area": row["area"],
                "rent_price": row["rent_price"],
                "deposit": row["deposit"],
                "electricity_price": row["electricity_price"],
                "water_price": row["water_price"],
                "internet_price": row["internet_price"],
                "garbage_price": row["garbage_price"],
                "other_fees": row["other_fees"],
                "available_date": row["available_date"],
                "current_electricity": row["current_electricity"],
                "current_water": row["current_water"],
                "tenant_id": row["tenant_id"],
                "landlord_id": row["landlord_id"]
            }
            return result

        except Exception as e:
            print(f"[⚠️ TenantRepository.get_room_infor_by_id_tenant] Lỗi khi truy vấn: {e}")
            db.close()
            return None

    @staticmethod
    def get_chart_income_month(id_tenant: int) -> Optional[List[Dict[str, Any]]]:
        """
        Trả về dữ liệu thu nhập hàng tháng của tenant (dùng để vẽ biểu đồ)
        Dữ liệu trả về là danh sách các dict có cấu trúc:
            {
                "month": "MM/YYYY",
                "total_income": <số tiền thu được trong tháng đó>
            }
        Sắp xếp theo month tăng dần.
        """
        # 1) Kết nối đến DB
        if not db.connect():
            return None

        try:
            query = """
                    SELECT strftime('%m/%Y', issue_date) AS month,
                        SUM(
                            (CurrElectric - PreElectric) * ElectricityPrice
                          + (CurrWater - PreWater) * WaterPrice
                          + TotalRoomPrice
                          + InternetFee
                          + TotalGarbageFee
                          + TotalAnotherFee
                          - Discount
                        ) AS total_income
                    FROM Invoices AS i
                        JOIN Rooms AS r  
                    ON i.RoomID = r.RoomID
                    WHERE i.TenantID = ?
                      AND i.Status = 'Đã thanh toán'
                    GROUP BY strftime('%Y-%m', issue_date)
                    ORDER BY strftime('%Y-%m', issue_date);  
                    """
            cursor = db.execute(query, (id_tenant,))
            rows = cursor.fetchall() if cursor else []
            db.close()

            # Chuyển sqlite3.Row thành list[dict]
            chart_data: List[Dict[str, Any]] = []
            for row in rows:
                chart_data.append({
                    "month": row["month"],
                    "total_income": row["total_income"] or 0.0
                })
            return chart_data

        except Exception as e:
            print(f"[⚠️ TenantRepository.get_chart_income_month] Lỗi truy vấn: {e}")
            db.close()
            return None

    @staticmethod
    def get_tenant_data_for_invoice_view(tenant_id: int) -> Optional[Dict[str, Any]]:
        """
        Lấy thông tin cơ bản của tenant để hiển thị trên giao diện xuất hóa đơn, bao gồm:
            - full_name
            - citizen_id (CCCD)
            - address (địa chỉ nhà)
            - phone (số điện thoại)
        """
        if not db.connect():
            return None

        try:
            query = """
                    SELECT Fullname    AS full_name,  
                           CCCD        AS citizen_id,  
                           HomeAddress AS address,  
                           PhoneNumber AS phone
                    FROM Tenants
                    WHERE TenantID = ? LIMIT 1;  
                    """
            cursor = db.execute(query, (tenant_id,))
            row = cursor.fetchone() if cursor else None
            db.close()

            if not row:
                return None

            return {
                "full_name": row["full_name"],
                "citizen_id": row["citizen_id"],
                "address": row["address"],
                "phone": row["phone"]
            }

        except Exception as e:
            print(f"[⚠️ TenantRepository.get_tenant_data_for_invoice_view] Lỗi truy vấn: {e}")
            db.close()
            return None

    @staticmethod
    def get_number_e_and_number_w_from(tenant_id: int, month: int, year: int) -> Optional[Dict[str, Any]]:
        """
        Lấy số điện (number_e) và số nước (number_w) tiêu thụ trong tháng/year của tenant,
        dựa vào hóa đơn (Invoice) đã phát hành.
        Giả sử CurrElectric và PreElectric, CurrWater và PreWater đã lưu trên bảng Invoices.
        Trả về:
            {
                "number_e": <CurrElectric - PreElectric>,
                "number_w": <CurrWater - PreWater>
            }
        Nếu có nhiều hóa đơn trong cùng tháng, chỉ lấy bản ghi gần nhất (issue_date lớn nhất).
        """
        if not db.connect():
            return None

        try:
            # 1) Tìm hóa đơn (nếu có) của tháng/year tương ứng, lấy bản ghi mới nhất
            query = """
                    SELECT (CurrElectric - PreElectric) AS number_e,  
                           (CurrWater - PreWater)       AS number_w
                    FROM Invoices
                    WHERE TenantID = ?
                      AND strftime('%m', issue_date) = printf('%02d', ?)
                      AND strftime('%Y', issue_date) = ?
                    ORDER BY issue_date DESC LIMIT 1;  
                    """
            cursor = db.execute(query, (tenant_id, month, year))
            row = cursor.fetchone() if cursor else None
            db.close()

            if not row:
                return None

            return {
                "number_e": row["number_e"] or 0,
                "number_w": row["number_w"] or 0
            }

        except Exception as e:
            print(f"[⚠️ TenantRepository.get_number_e_and_number_w_from] Lỗi truy vấn: {e}")
            db.close()
            return None

    @staticmethod
    def get_all_tenants():
        """
        Lấy tất cả Tenants, kèm Username và CreatedAt.
        Trả về list[Tenant].
        """
        if not db.connect():
            return []

        query = """
                SELECT t.TenantID,  
                       t.Fullname,  
                       t.Birth,  
                       t.CCCD,  
                       t.Gender,  
                       t.JobTitle,  
                       t.MaritalStatus,  
                       t.Email,  
                       t.PhoneNumber,  
                       t.HomeAddress,  
                       t.RentStartDate,  
                       t.RentEndDate,  
                       t.UserID,  
                       u.Username  AS Username,  
                       t.CreatedAt AS CreatedAt
                FROM Tenants AS t
                         LEFT JOIN Users AS u ON t.UserID = u.UserID
                ORDER BY t.TenantID;  
                """
        cursor = db.execute(query)
        rows = cursor.fetchall() if cursor else []
        db.close()

        tenants: list[Tenant] = []
        for row in rows:
            data = {
                "TenantID": row["TenantID"],
                "Fullname": row["Fullname"],
                "Birth": row["Birth"],
                "CCCD": row["CCCD"],
                "Gender": row["Gender"],
                "JobTitle": row["JobTitle"],
                "MaritalStatus": row["MaritalStatus"],
                "Email": row["Email"],
                "PhoneNumber": row["PhoneNumber"],
                "HomeAddress": row["HomeAddress"],
                "RentStartDate": row["RentStartDate"],
                "RentEndDate": row["RentEndDate"],
                "UserID": row["UserID"],
                "Username": row["Username"],
                "CreatedAt": row["CreatedAt"]
            }
            tenants.append(Tenant(data))
        return tenants

    @staticmethod
    def add_tenant_to_db( user_id: int, full_name: str, cccd: str, gender: str, job_title: str, marital_status: str,
            email: str, phone_number: str,  home_address: str, rent_start: str, rent_end: Optional[str]
                    ) -> Optional[Tenant]:

        if not db.connect():
            return None
        try:
            # 1) Thực hiện INSERT, gán CreatedAt = datetime('now','localtime')
            insert_sql = """
                         INSERT INTO Tenants(UserID, Fullname, CCCD, Gender, JobTitle, MaritalStatus,  
                                             Email, PhoneNumber, HomeAddress, RentStartDate, RentEndDate, CreatedAt)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now', 'localtime'));  
                         """
            params = (
                user_id, full_name, cccd, gender, job_title, marital_status, email, phone_number, home_address,
                rent_start, rent_end
            )
            cursor = db.execute(insert_sql, params)
            if cursor is None:
                db.close()
                return None

            tenant_id = cursor.lastrowid

            # 2) Lấy lại toàn bộ cột của record vừa insert
            select_sql = "SELECT * FROM Tenants WHERE TenantID = ?;"
            cursor = db.execute(select_sql, (tenant_id,))
            row = cursor.fetchone() if cursor else None

            db.close()

            if row:
                # row là sqlite3.Row, nên có thể truy cập row["ColumnName"] được
                columns = [column[0] for column in cursor.description]
                data = {col: row[col] for col in columns}
                return Tenant(data)
            else:
                return None

        except Exception as e:
            print(f"[TenantRepository.add_tenant_to_db] Lỗi: {e}")
            db.close()
            return None

    @staticmethod
    def get_tenant_by_id(tenant_id: int) -> Optional[Tenant]:
        """
        Lấy thông tin người thuê theo TenantID.
        Trả về instance Tenant hoặc None nếu không tìm thấy.
        """
        if not db.connect():
            return None

        query = "SELECT * FROM Tenants WHERE TenantID = ?;"
        cursor = db.execute(query, (tenant_id,))
        row = cursor.fetchone() if cursor else None
        db.close()

        if row:
            columns = [column[0] for column in cursor.description]
            data = {col: row[col] for col in columns}
            return Tenant(data)
        else:
            print(f"[⚠️ TenantRepository] Không tìm thấy tenant với ID: {tenant_id}")
            return None

    @staticmethod
    def get_tenant_by_cccd(cccd: str) -> Optional[Tenant]:
        """
        Trả về đối tượng Tenant từ số CCCD.
        """
        if not db.connect():
            return None

        query = "SELECT * FROM Tenants WHERE CCCD = ?;"
        cursor = db.execute(query, (cccd,))
        row = cursor.fetchone() if cursor else None
        db.close()

        if row:
            columns = [column[0] for column in cursor.description]
            data = {col: row[col] for col in columns}
            return Tenant(data)
        else:
            print(f"[⚠️ TenantRepository] Không tìm thấy tenant với CCCD: {cccd}")
            return None

    @staticmethod
    def get_tenant_by_room_id(room_id: int) -> Optional[Tenant]:
        """
        Lấy thông tin Tenant dựa vào RoomID (giả sử trong bảng Rooms có cột TenantID).
        """
        if not db.connect():
            return None

        query = """
                SELECT t.*
                FROM Tenants t
                         JOIN Rooms r ON t.TenantID = r.TenantID
                WHERE r.RoomID = ?;  
                """
        cursor = db.execute(query, (room_id,))
        row = cursor.fetchone() if cursor else None
        db.close()

        if row:
            columns = [column[0] for column in cursor.description]
            data = {col: row[col] for col in columns}
            return Tenant(data)
        else:
            print(f"[⚠️ TenantRepository] Không tìm thấy tenant gắn với RoomID: {room_id}")
            return None

    @staticmethod
    def get_tenant_id_from_user_id(user_id: int) -> Optional[int]:
        """
        Lấy TenantID dựa vào UserID.
        """
        if not db.connect():
            return None

        query = "SELECT TenantID FROM Tenants WHERE UserID = ?;"
        cursor = db.execute(query, (user_id,))
        row = cursor.fetchone() if cursor else None
        db.close()
        return row["TenantID"] if row else None

    @staticmethod
    def get_data_for_tenant_home_page(id_tenant: int, month: int, year: int) -> Optional[Dict[str, Any]]:
        """
        Lấy dữ liệu chi phí của tenant trong tháng/year nhất định:
        - tien_dien: (CurrElectric - PreElectric) * ElectricityPrice
        - tien_nuoc: (CurrWater - PreWater) * WaterPrice
        - tong_chi_phi: tổng tất cả các khoản (điện + nước + thuê + internet + rác + phí khác - discount)
        - ngay_den_han: Lấy cột DueDate nếu có, ngược lại lấy issue_date.
        Trả về None nếu không tìm thấy hóa đơn nào trong tháng đó.
        """
        # 1) Kết nối DB
        if not db.connect():
            return None

        try:
            # 2) Truy vấn hóa đơn gần nhất của tháng/year, sắp theo issue_date giảm dần
            query = """
                    SELECT (CurrElectric - PreElectric) * ElectricityPrice AS tien_dien,  
                           (CurrWater - PreWater) * WaterPrice             AS tien_nuoc,  
                           ((CurrElectric - PreElectric) * ElectricityPrice  
                                + (CurrWater - PreWater) * WaterPrice  
                                + TotalRoomPrice  
                                + InternetFee  
                                + TotalGarbageFee  
                                + TotalAnotherFee  
                               - Discount)                                 AS tong_chi_phi,  
                           COALESCE(DueDate, issue_date)                   AS ngay_den_han
                    FROM Invoices
                    WHERE TenantID = ?
                      AND strftime('%m', issue_date) = printf('%02d', ?)
                      AND strftime('%Y', issue_date) = ?
                    ORDER BY issue_date DESC LIMIT 1;  
                    """
            cursor = db.execute(query, (id_tenant, month, year))
            row = cursor.fetchone() if cursor else None
            db.close()

            if not row:
                return None

            return {
                "tien_dien": row["tien_dien"] or 0.0,
                "tien_nuoc": row["tien_nuoc"] or 0.0,
                "tong_chi_phi": row["tong_chi_phi"] or 0.0,
                "ngay_den_han": row["ngay_den_han"]
            }

        except sqlite3.Error as e:
            print(f"[⚠️ TenantRepository.get_data_for_tenant_home_page] Lỗi truy vấn: {e}")
            db.close()
            return None

    @staticmethod
    def get_month_with_last_invoice(id_tenant: int) -> Optional[tuple[int, int]]:
        """
        Lấy tháng và năm của hóa đơn gần nhất (issue_date) cho tenant.
        Trả về (month, year) dạng int, hoặc None nếu không tìm thấy bất cứ hóa đơn nào.
        """
        if not db.connect():
            return None

        try:
            query = """
                    SELECT CAST(strftime('%m', issue_date) AS INTEGER) AS month,
                    CAST(strftime('%Y', issue_date) AS INTEGER) AS year
                    FROM Invoices
                    WHERE TenantID = ?
                    ORDER BY issue_date DESC
                        LIMIT 1;  
                    """
            cursor = db.execute(query, (id_tenant,))
            row = cursor.fetchone() if cursor else None
            db.close()

            if not row:
                return None

            return row["month"], row["year"]

        except sqlite3.Error as e:
            print(f"[⚠️ TenantRepository.get_month_with_last_invoice] Lỗi truy vấn: {e}")
            db.close()
            return None

    @staticmethod
    def get_tenant_infor_by_id_tenant(id_tenant: int) -> Optional[Dict[str, Any]]:
        """
        Lấy thông tin cơ bản của tenant để hiển thị trang thông tin:
            - full_name, birth_date, citizen_id, gender,
              job_title, marital_status, email, phone_number
        """
        if not db.connect():
            return None

        try:
            query = """
                    SELECT Fullname      AS full_name,  
                           Birth         AS birth_date,  
                           CCCD          AS citizen_id,  
                           Gender        AS gender,  
                           JobTitle      AS job_title,  
                           MaritalStatus AS marital_status,  
                           Email         AS email,  
                           PhoneNumber   AS phone_number
                    FROM Tenants
                    WHERE TenantID = ? LIMIT 1;  
                    """
            cursor = db.execute(query, (id_tenant,))
            row = cursor.fetchone() if cursor else None
            db.close()

            if not row:
                return None

            return {
                "full_name": row["full_name"],
                "birth_date": row["birth_date"],
                "citizen_id": row["citizen_id"],
                "gender": row["gender"],
                "job_title": row["job_title"],
                "marital_status": row["marital_status"],
                "email": row["email"],
                "phone_number": row["phone_number"]
            }

        except sqlite3.Error as e:
            print(f"[⚠️ TenantRepository.get_tenant_infor_by_id_tenant] Lỗi truy vấn: {e}")
            db.close()
            return None

    @staticmethod
    def update_user_info(user_id: int, data: dict) -> bool:
        """
        Cập nhật thông tin Tenant dựa vào UserID:
        - data có thể chứa các key: Fullname, Birth, CCCD, Gender, JobTitle, MaritalStatus,
          Email, PhoneNumber, HomeAddress, RentStartDate, RentEndDate.
        - Không cập nhật CreatedAt, UserID.
        - Trả về True nếu thành công, False nếu có lỗi.
        """
        # 1. Tìm tenant_id từ user_id
        tenant_id = TenantRepository.get_tenant_id_from_user_id(user_id)
        if tenant_id is None:
            print(f"[TenantRepository.update_user_info] Không tìm thấy tenant tương ứng user_id={user_id}")
            return False

        # 2. Chuẩn bị danh sách cột và giá trị cần update
        fields = []
        values = []
        for key in (
                "Fullname", "Birth", "CCCD", "Gender", "JobTitle",
                "MaritalStatus", "Email", "PhoneNumber", "HomeAddress",
                "RentStartDate", "RentEndDate"
        ):
            if key in data and data[key] is not None:
                fields.append(f"{key} = ?")
                values.append(data[key])

        if not fields:
            # Nếu data không chứa bất kỳ trường nào để update
            print(f"[TenantRepository.update_user_info] Không có trường nào để cập nhật cho tenant_id={tenant_id}")
            return False

        # 3. Mở kết nối database (thiếu khởi tạo trước đó)
        if not db.connect():
            return False

        try:
            # 4. Build câu SQL UPDATE
            sql = f"UPDATE Tenants SET {', '.join(fields)} WHERE TenantID = ?;"
            values.append(tenant_id)

            # 5. Thực thi và commit
            db.execute(sql, tuple(values))
            db.conn.commit()  # Phải commit để lưu thay đổi
            db.close()

            print(f"[TenantRepository.update_user_info] Đã cập nhật tenant_id={tenant_id} với data={data}")
            return True

        except Exception as e:
            print(f"[TenantRepository.update_user_info] Lỗi khi UPDATE: {e}")
            db.close()
            return False


    @staticmethod
    def get_user_id_from_id_tenant(id_tenant: int) -> Optional[int]:
        """
        Lấy UserID dựa vào TenantID.
        Trả về int nếu tìm thấy, hoặc None nếu không có.
        """
        if not db.connect():
            return None

        query = "SELECT UserID FROM Tenants WHERE TenantID = ?;"
        cursor = db.execute(query, (id_tenant,))
        row = cursor.fetchone() if cursor else None
        db.close()
        return row["UserID"] if row else None

    @staticmethod
    def get_tenant_monthly_costs(id_tenant: int) -> Optional[List[Dict[str, Any]]]:
        """
        Lấy chi phí hàng tháng của tenant bao gồm tiền điện, nước và tổng chi phí.
        Trả về danh sách dict có cấu trúc:
          [
            {
              "month": "MM/YYYY",
              "tien_dien": <số tiền điện trong tháng đó>,
              "tien_nuoc": <số tiền nước trong tháng đó>,
              "tong": <tổng chi phí (điện + nước + thuê + internet + rác + phí khác - discount)>
            },
            ...
          ]
        Sắp xếp theo month tăng dần.
        """
        # 1) Kết nối đến DB
        if not db.connect():
            return None

        try:
            query = """
                    SELECT strftime('%m/%Y', i.issue_date) AS month,
                        SUM((i.CurrElectric - i.PreElectric) * r.ElectricityPrice) AS tien_dien,
                        SUM((i.CurrWater - i.PreWater) * r.WaterPrice)       AS tien_nuoc,
                        SUM(
                            (i.CurrElectric - i.PreElectric) * r.ElectricityPrice
                          + (i.CurrWater - i.PreWater)       * r.WaterPrice
                          + i.TotalRoomPrice
                          + i.InternetFee
                          + i.TotalGarbageFee
                          + i.TotalAnotherFee
                          - i.Discount
                        ) AS tong
                    FROM Invoices AS i
                        JOIN Rooms AS r  
                    ON i.RoomID = r.RoomID
                    WHERE i.TenantID = ?
                      AND i.Status IN ('Chưa thanh toán'  
                        , 'Đã thanh toán')
                    GROUP BY strftime('%Y-%m', i.issue_date)
                    ORDER BY strftime('%Y-%m', i.issue_date);  
                    """
            cursor = db.execute(query, (id_tenant,))
            rows = cursor.fetchall() if cursor else []
            db.close()

            result: List[Dict[str, Any]] = []
            for row in rows:
                result.append({
                    "month": row["month"],
                    "tien_dien": row["tien_dien"] or 0.0,
                    "tien_nuoc": row["tien_nuoc"] or 0.0,
                    "tong": row["tong"] or 0.0
                })
            return result

        except sqlite3.Error as e:
            print(f"[⚠️ TenantRepository.get_tenant_monthly_costs] Lỗi truy vấn: {e}")
            db.close()
            return None

    @staticmethod
    def update_tenant_info(tenant_id: int, updated_data: Dict[str, Any]) -> bool:
        """
        Cập nhật thông tin tenant với tenant_id dựa trên updated_data dict.
        Các key trong updated_data tương ứng:
          - full_name     → Fullname
          - birth_date    → Birth
          - citizen_id    → CCCD
          - gender        → Gender
          - occupation    → JobTitle
          - phone_number  → PhoneNumber
          - marital_status → MaritalStatus
        Trả về True nếu có ít nhất 1 hàng bị ảnh hưởng, ngược lại False.
        """
        # Bắt buộc phải có tenant_id
        if tenant_id is None:
            return False

        # Kết nối DB
        if not db.connect():
            return False

        try:
            query = """
                    UPDATE Tenants
                    SET Fullname      = ?,
                        Birth         = ?,
                        CCCD          = ?,
                        Gender        = ?,
                        JobTitle      = ?,
                        PhoneNumber   = ?,
                        MaritalStatus = ?
                    WHERE TenantID = ?;  
                    """
            # Lấy từng giá trị từ updated_data, nếu key không có, dùng giá trị cũ hoặc rỗng
            full_name = updated_data.get("full_name", "")
            birth_date = updated_data.get("birth_date", "")
            citizen_id = updated_data.get("citizen_id", "")
            gender = updated_data.get("gender", "")
            occupation = updated_data.get("occupation", "")
            phone_number = updated_data.get("phone_number", "")
            marital_status = updated_data.get("marital_status", "")

            cursor = db.execute(query, (
                full_name,
                birth_date,
                citizen_id,
                gender,
                occupation,
                phone_number,
                marital_status,
                tenant_id
            ))

            return cursor.rowcount > 0

        except sqlite3.Error as e:
            print(f"[⚠️ TenantRepository.update_tenant_info] Lỗi: {e}")
            return False

        finally:
            db.close()

    @staticmethod
    def get_room_id_by_tenant(tenant_id: int) -> Optional[int]:
        """
        Trả về RoomID ứng với tenant_id. Nếu không tìm thấy, trả về None.
        """
        if not db.connect():
            return None

        try:
            query = """
                    SELECT RoomID
                    FROM Rooms
                    WHERE TenantID = ? LIMIT 1;  
                    """
            cursor = db.execute(query, (tenant_id,))
            row = cursor.fetchone() if cursor else None
            db.close()

            if row:
                # row["RoomID"] hoặc row[0]
                return row["RoomID"]
            return None

        except sqlite3.Error as e:
            print(f"[⚠️ TenantRepository.get_room_id_by_tenant] Lỗi truy vấn: {e}")
            db.close()
            return None