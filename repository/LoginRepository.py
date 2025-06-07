from QLNHATRO.RentalManagementApplication.Repository.UserRepository import UserRepository
from QLNHATRO.RentalManagementApplication.backend.database.Database import Database


db = Database()
class LoginRepository:


    @staticmethod
    def get_user(username):
        return UserRepository.get_user_by_username(username)

    @staticmethod
    def get_role_from_user_id(user_id: int) -> str | None:
        """
        Trả về role của user dựa trên user_id.
        Nếu không tìm thấy hoặc có lỗi, trả về None.
        """
        try:
            db.connect()
            query = "SELECT Role FROM Users WHERE UserID = ?"
            cursor = db.execute(query, (user_id,))
            row = cursor.fetchone()
            if row:
                # Giả sử Database đã thiết lập row_factory để có thể truy cập theo tên cột
                return row["Role"]
            else:
                print(f"⚠ Không tìm thấy User với UserID = {user_id}")
                return None
        except Exception as e:
            print(f"[LỖI] get_role_from_user_id: {e}")
            return None
        finally:
            db.close()

    @staticmethod
    def create_new_user_name(username: str, hashed_password: str, role: str) -> int | None:
        """
        Chèn 1 record mới vào bảng Users (Username, Password, Role, IsActive).
        Trả về user_id (cursor.lastrowid) nếu thành công, ngược lại trả về None.
        """
        try:
            db.connect()
            # Nếu role = 'admin' thì IsActive = 1, còn lại = 0
            is_active = 1 if role == "admin" else 0

            query = """
                    INSERT INTO Users (Username, Password, Role, IsActive)
                    VALUES (?, ?, ?, ?)  
                    """
            cursor = db.execute(query, (username, hashed_password, role, is_active))
            new_id = cursor.lastrowid
            return new_id
        except Exception as e:
            print(f"[LỖI] LoginRepository.create_new_user_name: {e}")
            return None
        finally:
            db.close()

    @staticmethod
    def change_password_into_database(username: str, new_hashed_password: str):
        """
        Cập nhật mật khẩu đã được hash cho user có username tương ứng.
        Đây là hàm UPDATE, sẽ không trả về gì.
        Nếu có lỗi sẽ in ra thông báo, nhưng không raise exception hay return giá trị.
        """
        try:
            db.connect()
            query = """
                    UPDATE Users
                    SET Password = ?
                    WHERE Username = ?  
                    """
            db.execute(query, (new_hashed_password, username))
            # Chỉ cần gọi execute, commit đã được thực hiện bên trong db.execute
            print(f"[INFO] Đã cập nhật mật khẩu cho '{username}'")
        except Exception as e:
            print(f"[LỖI] LoginRepository.change_password_into_database: {e}")
        finally:
            db.close()

    @staticmethod
    def get_sdt_from_username(username: str) -> str | None:
        """
        Trả về số điện thoại (PhoneNumber) của user dựa vào username.
        Sơ đồ lưu trữ:
          - Nếu role = 'landlord', thông tin phone ở bảng Landlords.
          - Nếu role = 'tenant', thông tin phone ở bảng Tenants.
          - Nếu role = 'admin', bảng Admins không chứa Phone, nên trả về None.
        Chúng ta sử dụng CASE WHEN ... END kết hợp subquery để chỉ phải gọi một lần bảng Users.
        """
        try:
            db.connect()
            query = """
                    SELECT CASE u.Role  
                               WHEN 'landlord' THEN (SELECT PhoneNumber  
                                                     FROM Landlords l  
                                                     WHERE l.UserID = u.UserID)  
                               WHEN 'tenant' THEN (SELECT PhoneNumber  
                                                   FROM Tenants t  
                                                   WHERE t.UserID = u.UserID)  
                               ELSE NULL  
                               END AS phone
                    FROM Users u
                    WHERE u.Username = ?  
                    """
            cursor = db.execute(query, (username,))
            row = cursor.fetchone()
            if row:
                return row["phone"]
            return None
        except Exception as e:
            print(f"[LỖI] LoginRepository.get_sdt_from_username: {e}")
            return None
        finally:
            db.close()

    @staticmethod
    def get_email_from_username(username: str) -> str | None:
        """
        Trả về email của user dựa vào username.
        Cấu trúc tương tự như get_sdt_from_username:
          - Nếu role = 'landlord', email ở Landlords.
          - Nếu role = 'tenant', email ở Tenants.
          - Nếu role = 'admin', bảng Admins không có cột Email → trả về None.
        """
        try:
            db.connect()
            query = """
                    SELECT CASE u.Role  
                               WHEN 'landlord' THEN (SELECT Email  
                                                     FROM Landlords l  
                                                     WHERE l.UserID = u.UserID)  
                               WHEN 'tenant' THEN (SELECT Email  
                                                   FROM Tenants t  
                                                   WHERE t.UserID = u.UserID)  
                               ELSE NULL  
                               END AS email
                    FROM Users u
                    WHERE u.Username = ?  
                    """
            cursor = db.execute(query, (username,))
            row = cursor.fetchone()
            if row:
                return row["email"]
            return None
        except Exception as e:
            print(f"[LỖI] LoginRepository.get_email_from_username: {e}")
            return None
        finally:
            db.close()

    @staticmethod
    def is_username_exists(username: str) -> bool:
        try:
            db.connect()
            query = "SELECT 1 FROM Users WHERE Username = ? LIMIT 1"
            cursor = db.execute(query, (username,))
            row = cursor.fetchone()
            return row is not None  # luôn trả True hoặc False
        except Exception as e:
            print(f"[LỖI] LoginRepository.is_username_exists: {e}")
            return False  # nếu lỗi, cũng trả False (compatible with bool)
        finally:
            db.close()
