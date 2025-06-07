from datetime import datetime

from RentalManagementApplication.Repository.AdminRepository import AdminRepository
from RentalManagementApplication.Repository.InvoiceRepository import InvoiceRepository
from RentalManagementApplication.Repository.LandlordRepository import LanlordRepository
from RentalManagementApplication.Repository.RoomRepository import RoomRepository
from RentalManagementApplication.Repository.TenantRepository import TenantRepository
from RentalManagementApplication.Repository.UserRepository import UserRepository


class AdminService:

    @staticmethod
    def get_all_users() -> list[dict]:
        users = UserRepository.get_all_users()
        role_map = {
            "admin": "admin",
            "landlord": "Chủ trọ",
            "tenant": "Người thuê trọ"
        }

        ui_list = []
        for idx, user in enumerate(users, start=1):
            ui_list.append({
                "stt": idx,
                "username": user.username,
                "role": role_map.get(user.role, user.role),
                "status": "Active" if user.is_active else "Inactive"
            })
        return ui_list

    @staticmethod
    def get_all_landlords() -> list[dict]:
        landlord_models = LanlordRepository.get_all_landlords()
        result = []
        for idx, l in enumerate(landlord_models, start=1):
            result.append({
                "stt": idx,
                "name": l.fullname,
                "cccd": l.cccd,
                "phone": l.phone_number,
                "email": l.email,
                "so_phong": l.so_phong,
                "username": l.username,
                "created_at": l.created_at,  # xử lý hiển thị ngay tại đây nếu cần format
                "id_landlord": l.landlord_id
            })
        return result

    @staticmethod
    def get_all_tenants() -> list[dict]:
        tenant_models = TenantRepository.get_all_tenants()
        result = []
        for idx, t in enumerate(tenant_models, start=1):
            result.append({
                "stt": idx,
                "name": t.fullname,
                "cccd": t.cccd,
                "phone": t.phone_number,
                "email": t.email,
                "ngay_thue": t.rent_start_date,  # hoặc chuyển format tại đây
                "username": t.username,
                "created_at": t.created_at,
                "id_tenant": t.tenant_id
            })
        return result

    @staticmethod
    def get_all_rooms():
        """Trả về danh sách phòng trọ"""
        raw_data = RoomRepository.get_all_rooms()
        result = []
        for idx, room in enumerate(raw_data, 1):
            result.append({
                "stt": idx,
                "room_name": room.get("room_name", "N/A"),
                "room_type": room.get("room_type", "N/A"),
                "landlord": room.get("landlord_name", "N/A"),
                "address": room.get("address", "N/A"),
                "status": room.get("status", "N/A"),
                "room_id": room.get("room_id","N/A")
            })
        return result



    @staticmethod
    def get_previous_month_and_year(month, year):
        if month == 1:
            return 12, year - 1
        else:
            return month - 1, year

    @staticmethod
    def calc_percent(current, previous):
        if previous == 0:
            return 0.0
        return round((current - previous) / previous * 100, 1)

    @staticmethod
    def get_summary_dashboard_data_with_growth():
        """
        Trả về dữ liệu thống kê tổng quát kèm phần trăm tăng trưởng cho dashboard admin
        Gồm: landlord, tenant, room, paid_invoice
        """
        # Lấy tháng hiện tại và tháng trước
        now = datetime.now()
        this_month, this_year = now.month, now.year
        last_month, last_year = AdminService.get_previous_month_and_year(this_month, this_year)

        # Dữ liệu tháng này
        current_landlords = AdminRepository.count_landlords_by_month(this_month, this_year)
        current_tenants = AdminRepository.count_tenants_by_month(this_month, this_year)
        current_rooms = AdminRepository.count_rooms_by_month(this_month, this_year)
        current_paid = InvoiceRepository.count_paid_invoices_by_month(this_month, this_year)

        # Dữ liệu tháng trước
        last_landlords = AdminRepository.count_landlords_by_month(last_month, last_year)
        last_tenants = AdminRepository.count_tenants_by_month(last_month, last_year)
        last_rooms = AdminRepository.count_rooms_by_month(last_month, last_year)
        last_paid = InvoiceRepository.count_paid_invoices_by_month(last_month, last_year)

        # Tính % tăng trưởng
        percent_landlords = AdminService.calc_percent(current_landlords, last_landlords)
        percent_tenants = AdminService.calc_percent(current_tenants, last_tenants)
        percent_rooms = AdminService.calc_percent(current_rooms, last_rooms)
        percent_paid = AdminService.calc_percent(current_paid, last_paid)

        # Trả về dữ liệu thống kê
        return {
            "num_landlords": current_landlords,
            "percent_landlords": percent_landlords,

            "num_tenants": current_tenants,
            "percent_tenants": percent_tenants,

            "num_rooms": current_rooms,
            "percent_rooms": percent_rooms,

            "num_paid_invoices": current_paid,
            "percent_paid_invoices": percent_paid,
        }

    @staticmethod
    def get_all_invoices_for_admin():
        """Trả về tất cả hóa đơn trong hệ thống với thông tin chủ trọ và người thuê"""
        raw_data = InvoiceRepository.get_all_invoices()
        result = []

        for idx, invoice in enumerate(raw_data, 1):
            # Tính tổng chi phí
            total = (
                    invoice.get("rent_price", 0)
                    + invoice.get("electric_fee", 0)
                    + invoice.get("water_fee", 0)
                    + invoice.get("garbage_fee", 0)
                    + invoice.get("internet_fee", 0)
                    + invoice.get("other_fee", 0)
            )

            result.append({
                "STT": str(idx),
                "Họ tên chủ trọ": invoice.get("landlord_name", "Chưa có"),
                "Họ tên người thuê": invoice.get("tenant_name", "Chưa có"),
                "Tổng chi phí": f"{total:,} VNĐ",
                "Ngày xuất hóa đơn": invoice.get("created_at", "N/A"),
                "Chi tiết hóa đơn": "Xem",
                "id_invoice": invoice.get("invoice_id")
            })
        return result

    @staticmethod
    def get_system_stats_by_month():
        """
        Trả về tối đa 12 tháng gần nhất từ kết quả thống kê.
        """
        all_stats = AdminRepository.get_system_stats_by_month()

        # Chuyển định dạng tháng từ "MM/YYYY" thành datetime để dễ sắp xếp
        for item in all_stats:
            item["_dt"] = datetime.strptime(item["month"], "%m/%Y")

        # Sắp xếp theo thời gian giảm dần (mới nhất trước)
        all_stats.sort(key=lambda x: x["_dt"], reverse=True)

        # Lấy 12 tháng gần nhất
        latest_12 = all_stats[:12]

        # Sắp xếp lại theo thời gian tăng dần (mới -> cũ → cũ -> mới)
        latest_12.sort(key=lambda x: x["_dt"])

        # Xóa trường phụ trợ _dt
        for item in latest_12:
            del item["_dt"]

        return latest_12

