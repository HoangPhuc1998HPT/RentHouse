from PyQt5.QtWidgets import QApplication



from RentalManagementApplication.frontend.Component.ErrorDialog import ErrorDialog
from RentalManagementApplication.frontend.views.Admin.AdminUserManager import AdminUserManagement
from RentalManagementApplication.services.AdminService import AdminService
from RentalManagementApplication.services.RoomService import RoomService


class AdminController:

    _user_windows = []

    @staticmethod
    def go_to_home(view):
        from RentalManagementApplication.frontend.views.Admin.AdminHomePage import AdminHome
        from RentalManagementApplication.services.AdminService import AdminService

        summary_data = AdminService.get_summary_dashboard_data_with_growth()
        monthly_data = AdminService.get_system_stats_by_month()
        admin_home = AdminHome(view.main_window, summary_data, monthly_data)
        view.set_right_frame(lambda *_: admin_home)

    @staticmethod
    def go_to_user_management(view):
        user_list = AdminService.get_all_users()
        view.set_right_frame(lambda: AdminUserManagement(view.main_window, user_list))

    @staticmethod
    def go_to_landlord_list(view):
        from RentalManagementApplication.frontend.views.Admin.AdminLandlordList import AdminLandlordList
        # Tạm thời dùng mock data; sau này sẽ gọi từ AdminService
        landlord_list = AdminService.get_all_landlords() # đã có id_landlord
        view.set_right_frame(lambda: AdminLandlordList(view.main_window, landlord_list))

    @staticmethod
    def go_to_tenant_list(view):
        from RentalManagementApplication.frontend.views.Admin.AdminTenantList import AdminTenantList
        tenant_list = AdminService.get_all_tenants()  # Hoặc dữ liệu giả lập
        view.set_right_frame(lambda: AdminTenantList(view.main_window, tenant_list))

    @staticmethod
    def go_to_room_list(view):
        from RentalManagementApplication.frontend.views.Admin.AdminRoomList import AdminRoomList
        room_list = RoomService.get_all_rooms()  # Dữ liệu thật hoặc giả lập
        view.set_right_frame(lambda: AdminRoomList(view.main_window, room_list))

    @staticmethod
    def go_to_invoice_list(view):
        #print("[INFO] Điều hướng đến Danh sách hóa đơn")

        from RentalManagementApplication.frontend.views.Admin.AdminInvoiceList import AdminInvoiceList
        from RentalManagementApplication.services.AdminService import AdminService

        invoice_list = AdminService.get_all_invoices_for_admin()
        view.set_right_frame(lambda: AdminInvoiceList(view.main_window, invoice_list))

    @staticmethod
    def handle_exit(view):
        print("[INFO] Đóng ứng dụng")
        QApplication.quit()

    @staticmethod
    def handel_exit_window(view):
        view.main_window.close()
    '''--------------------------------------------------------------------'''

    @staticmethod
    def go_to_open_infor_lanlord(username):
        from RentalManagementApplication.frontend.views.Landlord.LandlordInfo import LandlordInfo
        from RentalManagementApplication.frontend.Component.UserInfoWindow import UserInfoWindow

        from RentalManagementApplication.Repository.LandlordRepository import LanlordRepository
        information_data = LanlordRepository.get_landlord_info_by_username(username)

        id_landlord = information_data.pop('id_landlord', None)

        content_widget = LandlordInfo(None, information_data)

        window = UserInfoWindow(content_widget, title=f"Thông tin Chủ trọ: {username}")
        window.show()
        window.activateWindow()
        AdminController._user_windows.append(window)

    @staticmethod
    def go_to_infor_tenant(username: str):
        from RentalManagementApplication.frontend.views.Tenant.TenantInfo import TenantInfo
        from RentalManagementApplication.frontend.Component.UserInfoWindow import UserInfoWindow
        from RentalManagementApplication.Repository.TenantRepository import TenantRepository

        # 1 truy vấn duy nhất, trả về dict hoặc None
        initial_data = TenantRepository.get_tenant_info_by_username(username)
        if not initial_data:
            ErrorDialog.show_error(f"Không tìm thấy thông tin Tenant cho user '{username}'.")
            return

        # tenant_id cần nếu bạn cập nhật sau này
        tenant_id = initial_data.pop("tenant_id", None)

        # Gởi thẳng dict vào view
        content_widget = TenantInfo(None, initial_data, tenant_id)
        window = UserInfoWindow(content_widget, title=f"Thông tin Người thuê: {username}")
        window.show()
        window.activateWindow()
        AdminController._user_windows.append(window)

    @staticmethod
    def open_infor_admin_page(username):
        from RentalManagementApplication.frontend.views.Admin.AdminInfor import AdminInfo
        window = AdminInfo()
        window.show()
        window.activateWindow()
        AdminController._user_windows.append(window)

    '''--------------------------------------------------------------------'''