from PyQt5.QtWidgets import QApplication

from QLNHATRO.RentalManagementApplication.frontend.Component.ErrorDialog import ErrorDialog
from QLNHATRO.RentalManagementApplication.frontend.views.Landlord.LandlordInfo import LandlordInfo
from QLNHATRO.RentalManagementApplication.frontend.views.Landlord.LandlordListInvoices import ListInvoices
from QLNHATRO.RentalManagementApplication.services.InvoiceService import InvoiceService
from QLNHATRO.RentalManagementApplication.services.LandlordService import LandlordService
from QLNHATRO.RentalManagementApplication.services.RoomService import RoomService

class LandlordController:
    def __init__(self):
        pass

    @staticmethod
    def update_landlord_field(id_lanlord, field, value):
        LandlordService.update_field(id_lanlord, field, value)

    @staticmethod
    def go_to_home_page(view, id_lanlord):
        information_data = LandlordService.handle_data_for_home_page(id_lanlord)
        monthly_income = LandlordService.get_monthly_income(id_lanlord)

        from QLNHATRO.RentalManagementApplication.frontend.views.Landlord.LandlordHome import LandlordHome
        lanlord_home = LandlordHome(view.main_window, id_lanlord, information_data, monthly_income)
        view.set_right_frame(lambda *_: lanlord_home)

    '''Đã kiểm tra đồng bộ và chuẩn hóa'''
    @staticmethod
    def go_to_info_page(view, landlord_id: int):
        landlord = LandlordService.handle_data_infor_page(landlord_id)
        if not landlord:
            ErrorDialog.show_error("Không tìm thấy thông tin chủ trọ.", view)
            return
        # truyền thẳng instance Landlord vào view
        content = LandlordInfo(view.main_window, landlord)
        view.set_right_frame(lambda *_: content)

    '''Đã kiểm tra đồng bộ và chuẩn hóa'''
    @staticmethod
    def go_to_room_list(view, id_lanlord):
        room_data = RoomService.handle_data_for_room_list_page(id_lanlord)
        # truyền vào view
        print("đây là room list",room_data)
        from QLNHATRO.RentalManagementApplication.frontend.views.Landlord.LandlordRoomList import RoomList
        room_list_view = RoomList(view.main_window, room_data, id_lanlord)
        view.set_right_frame(lambda *_: room_list_view)

    @staticmethod
    def go_to_invoice_list(view, id_lanlord):
        invoice_list = InvoiceService.handle_data_for_invoice_list_page(id_lanlord)
        print("đây là invoice list", invoice_list)
        invoice_list_view = ListInvoices(view.main_window, invoice_list, id_lanlord)
        view.set_right_frame(lambda *_: invoice_list_view)

    @staticmethod
    def handle_logout(view):
        """Quay về màn hình đăng nhập"""
        from QLNHATRO.RentalManagementApplication.frontend.views.Login_Register.Login.HomeLogin import LoginWindow
        #print("[INFO] Đăng xuất khỏi dashboard landlord...")

        main_window = view.main_window
        login_widget = LoginWindow(main_window)  # truyền lại main_window nếu cần

        # Đặt lại central widget
        main_window.setCentralWidget(login_widget)

        # Reset kích thước chuẩn
        main_window.resize(800, 620)
        main_window.setMinimumSize(825, 600)
        main_window.setMaximumSize(825, 600)

        # Reset tiêu đề
        main_window.setWindowTitle("Đăng nhập hệ thống")

    @staticmethod
    def handle_exit():
        print("[INFO] Đóng ứng dụng")
        QApplication.quit()

    @staticmethod
    def go_to_LanlordFindNewTenant(view, id_lanlord):
        from QLNHATRO.RentalManagementApplication.frontend.views.Landlord.LandlordFindNewTenant import FindNewTenant

        ds_phong = RoomService.get_list_room_by_id_landlord(id_lanlord)
        find_new_tenant_view = FindNewTenant(view.main_window, ds_phong=ds_phong)
        view.set_right_frame(lambda *_: find_new_tenant_view)

    @staticmethod
    def go_to_create_new_room(view, id_lanlord):
        from QLNHATRO.RentalManagementApplication.frontend.views.Landlord.LandlordCreateNewRoom import CreateNewRoom

        create_new_room_view = CreateNewRoom(view.main_window, id_lanlord)
        view.set_right_frame(lambda *_: create_new_room_view)