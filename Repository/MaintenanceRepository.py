import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

from QLNHATRO.RentalManagementApplication.backend.database.Database import Database

db = Database()
class MaintenanceRepository:
    # Dữ liệu yêu cầu sửa chữa giả lập
    requests = []

    @staticmethod
    def create_maintenance_request(
            tenant_id: int,
            room_id: int,
            issue_type: str,
            urgency_level: str,
            description: str,
            contact_phone: Optional[str] = None,
            available_time: Optional[str] = None,
            discovery_date: Optional[str] = None,
            image_path: Optional[str] = None
    ) -> Optional[int]:
        """
        Chèn một hàng mới vào table maintenance_requests.
        Trả về request_id (lastrowid) nếu thành công, None nếu lỗi.
        """
        try:
            db.connect()  # Kết nối và tự động set row_factory = sqlite3.Row
            # Mặc định discovery_date = ngày hiện tại nếu không truyền
            discovery_date = discovery_date or datetime.now().strftime('%Y-%m-%d')

            query = """
                    INSERT INTO maintenance_requests
                    (TenantID, RoomID, issue_type, urgency_level, description,
                     contact_phone, available_time, discovery_date, image_path, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending', ?)  
                    """
            # Tạo created_at dạng ISO: "YYYY-MM-DDTHH:MM:SS"
            now_iso = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

            cursor = db.execute(query, (
                tenant_id, room_id, issue_type, urgency_level, description,
                contact_phone, available_time, discovery_date, image_path, now_iso
            ))

            new_id = cursor.lastrowid
            return new_id

        except sqlite3.Error as e:
            print(f"❌ [Repository] Lỗi tạo maintenance request: {e}")
            return None
        finally:
            db.close()

    @staticmethod
    def get_maintenance_request_by_id(request_id: int) -> Optional[Dict]:
        """
        Lấy chi tiết một yêu cầu bảo trì theo request_id.
        Trả về dict (with keys) hoặc None.
        """
        try:
            db.connect()
            query = """
                    SELECT mr.request_id,  
                           mr.TenantID       AS tenant_id,  
                           mr.RoomID         AS room_id,  
                           mr.issue_type     AS issue_type,  
                           mr.urgency_level  AS urgency_level,  
                           mr.description    AS description,  
                           mr.contact_phone  AS contact_phone,  
                           mr.available_time AS available_time,  
                           mr.discovery_date AS discovery_date,  
                           mr.image_path     AS image_path,  
                           mr.status         AS status,  
                           mr.created_at     AS created_at,  
                           r.RoomName        AS room_name,  
                           r.Address         AS room_address,  
                           t.Fullname        AS tenant_name,  
                           t.PhoneNumber     AS tenant_phone,  
                           t.Email           AS tenant_email
                    FROM maintenance_requests mr
                             JOIN Rooms r ON mr.RoomID = r.RoomID
                             JOIN Tenants t ON mr.TenantID = t.TenantID
                    WHERE mr.request_id = ? LIMIT 1  
                    """
            cursor = db.execute(query, (request_id,))
            row = cursor.fetchone()
            if row:
                # sqlite3.Row có thể dict(row)
                return dict(row)
            return None

        except sqlite3.Error as e:
            print(f"❌ [Repository] Lỗi get_maintenance_request_by_id: {e}")
            return None
        finally:
            db.close()

    @staticmethod
    def get_maintenance_requests_by_landlord(landlord_id: int) -> List[Dict]:
        """
        Lấy tất cả yêu cầu bảo trì (với thông tin Tenant, Room) theo landlord_id.
        Trả về list of dict.
        """
        try:
            db.connect()
            query = """
                    SELECT mr.request_id,  
                           mr.TenantID       AS tenant_id,  
                           mr.RoomID         AS room_id,  
                           mr.issue_type     AS issue_type,  
                           mr.urgency_level  AS urgency_level,  
                           mr.description    AS description,  
                           mr.contact_phone  AS contact_phone,  
                           mr.available_time AS available_time,  
                           mr.discovery_date AS discovery_date,  
                           mr.image_path     AS image_path,  
                           mr.status         AS status,  
                           mr.created_at     AS created_at,  
                           r.RoomName        AS room_name,  
                           t.Fullname        AS tenant_name,  
                           t.PhoneNumber     AS tenant_phone
                    FROM maintenance_requests mr
                             JOIN Rooms r ON mr.RoomID = r.RoomID
                             JOIN Tenants t ON mr.TenantID = t.TenantID
                    WHERE r.LandlordID = ?
                    ORDER BY CASE mr.urgency_level  
                                 WHEN 'Khẩn cấp' THEN 1  
                                 WHEN 'Bình thường' THEN 2  
                                 ELSE 3  
                                 END,  
                             mr.created_at DESC  
                    """
            cursor = db.execute(query, (landlord_id,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

        except sqlite3.Error as e:
            print(f"❌ [Repository] Lỗi get_maintenance_requests_by_landlord: {e}")
            return []
        finally:
            db.close()

    @staticmethod
    def get_requests_by_tenant_id(tenant_id: int) -> List[Dict]:
        """
        Lấy danh sách yêu cầu bảo trì cho một TenantID nhất định.
        """
        try:
            db.connect()
            query = """
                    SELECT mr.request_id,  
                           mr.TenantID       AS tenant_id,  
                           mr.RoomID         AS room_id,  
                           mr.issue_type     AS issue_type,  
                           mr.urgency_level  AS urgency_level,  
                           mr.description    AS description,  
                           mr.contact_phone  AS contact_phone,  
                           mr.available_time AS available_time,  
                           mr.discovery_date AS discovery_date,  
                           mr.image_path     AS image_path,  
                           mr.status         AS status,  
                           mr.created_at     AS created_at
                    FROM maintenance_requests mr
                    WHERE mr.TenantID = ?
                    ORDER BY mr.created_at DESC  
                    """
            cursor = db.execute(query, (tenant_id,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

        except sqlite3.Error as e:
            print(f"❌ [Repository] Lỗi get_requests_by_tenant_id: {e}")
            return []
        finally:
            db.close()

    @staticmethod
    def update_maintenance_status(request_id: int, new_status: str) -> bool:
        """
        Cập nhật status của yêu cầu. Trả về True nếu affected_row > 0.
        """
        try:
            db.connect()
            query = """
                    UPDATE maintenance_requests
                    SET status     = ?,
                        created_at = ?
                    WHERE request_id = ?  
                    """
            # Cập nhật created_at thành ISO mới
            now_iso = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            cursor = db.execute(query, (new_status, now_iso, request_id))
            return cursor.rowcount > 0

        except sqlite3.Error as e:
            print(f"❌ [Repository] Lỗi update_maintenance_status: {e}")
            return False
        finally:
            db.close()

    @staticmethod
    def get_maintenance_statistics(landlord_id: int) -> Dict:
        """
        Lấy thống kê (total, pending, in_progress, resolved, urgent) cho landlord.
        """
        try:
            db.connect()
            query = """
                    SELECT COUNT(*)                                                                 AS total_requests,  
                           SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END)                      AS pending_count,  
                           SUM(CASE WHEN status IN ('In Progress', 'Đang xử lý') THEN 1 ELSE 0 END) AS in_progress_count,  
                           SUM(CASE WHEN status IN ('Resolved', 'Đã hoàn thành') THEN 1 ELSE 0 END) AS resolved_count,  
                           SUM(CASE WHEN urgency_level = 'Khẩn cấp' THEN 1 ELSE 0 END)              AS urgent_count
                    FROM maintenance_requests mr
                             JOIN Rooms r ON mr.RoomID = r.RoomID
                    WHERE r.LandlordID = ?  
                    """
            cursor = db.execute(query, (landlord_id,))
            row = cursor.fetchone()
            if row:
                return {
                    'total_requests': row['total_requests'] or 0,
                    'pending_count': row['pending_count'] or 0,
                    'in_progress_count': row['in_progress_count'] or 0,
                    'resolved_count': row['resolved_count'] or 0,
                    'urgent_count': row['urgent_count'] or 0
                }
            return {}
        except sqlite3.Error as e:
            print(f"❌ [Repository] Lỗi get_maintenance_statistics: {e}")
            return {}
        finally:
            db.close()

    @staticmethod
    def delete_maintenance_request(request_id: int) -> bool:
        """
        Xóa một yêu cầu bảo trì. Trả về True nếu delete thành công.
        """
        try:
            db.connect()
            query = "DELETE FROM maintenance_requests WHERE request_id = ?"
            cursor = db.execute(query, (request_id,))
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"❌ [Repository] Lỗi delete_maintenance_request: {e}")
            return False
        finally:
            db.close()

    @staticmethod
    def save_request(request_data: Dict) -> None:
        """
        Lưu tạm yêu cầu (nếu đang test mà không có DB).
        """
        MaintenanceRepository.requests.append(request_data)
        print(f"[DEBUG][Repository] Đã lưu yêu cầu: {request_data}")

    @staticmethod
    def get_all_requests() -> List[Dict]:
        """
        Trả về danh sách yêu cầu đang lưu tạm.
        """
        return MaintenanceRepository.requests

    @staticmethod
    def get_requests_by_room_id(room_id: int) -> List[Dict]:

        maintenance_history = [
            {
                "id": 1,
                "description": "Vòi nước bị rỉ",
                "status": "Đã hoàn thành",
                "date": "01/04/2025"
            },
            {
                "id": 2,
                "description": "Đèn phòng tắm không sáng",
                "status": "Đang xử lý",
                "date": "20/04/2025"
            }
        ]

        return maintenance_history


    @staticmethod
    def get_maintenance_requests_by_status(landlord_id: int, status: str) -> List[Dict]:
        """
        Lấy danh sách yêu cầu bảo trì theo trạng thái cụ thể.
        """
        # Thử kết nối
        try:
            db.connect()
        except Exception:
            return []

        try:
            query = """
                    SELECT mr.request_id,  
                           mr.issue_type,  
                           mr.urgency_level,  
                           mr.description,  
                           mr.status,  
                           mr.created_at,  
                           r.RoomName AS room_name,  
                           t.Fullname AS tenant_name
                    FROM maintenance_requests mr
                             JOIN Rooms r ON mr.RoomID = r.RoomID
                             JOIN Tenants t ON mr.TenantID = t.TenantID
                    WHERE r.LandlordID = ?
                      AND mr.status = ?
                    ORDER BY mr.created_at DESC;  
                    """
            cursor = db.execute(query, (landlord_id, status))
            rows = cursor.fetchall()

            result = [dict(row) for row in rows]
            db.close()
            return result

        except sqlite3.Error as e:
            print(f"❌ Lỗi truy vấn theo trạng thái: {e}")
            db.close()
            return []

    @staticmethod
    def get_maintenance_requests_by_urgency(landlord_id: int, urgency: str) -> List[Dict]:
        """
        Lấy danh sách yêu cầu bảo trì theo mức độ khẩn cấp cụ thể.
        """
        # Thử kết nối
        try:
            db.connect()
        except Exception:
            return []

        try:
            query = """
                    SELECT mr.request_id,  
                           mr.issue_type,  
                           mr.urgency_level,  
                           mr.description,  
                           mr.status,  
                           mr.created_at,  
                           r.RoomName AS room_name,  
                           t.Fullname AS tenant_name
                    FROM maintenance_requests mr
                             JOIN Rooms r ON mr.RoomID = r.RoomID
                             JOIN Tenants t ON mr.TenantID = t.TenantID
                    WHERE r.LandlordID = ?
                      AND mr.urgency_level = ?
                    ORDER BY mr.created_at DESC;  
                    """
            cursor = db.execute(query, (landlord_id, urgency))
            rows = cursor.fetchall()

            result = [dict(row) for row in rows]
            db.close()
            return result

        except sqlite3.Error as e:
            print(f"❌ Lỗi truy vấn theo mức độ khẩn cấp: {e}")
            db.close()
            return []