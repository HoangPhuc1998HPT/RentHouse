from RentalManagementApplication.Repository.RoomRepository import RoomRepository
from RentalManagementApplication.frontend.views.Rooms.ManageInvoicePage import InvoiceInputPage
from RentalManagementApplication.frontend.views.Rooms.RoomUpdateTenantPage import RoomUpdateTenantPage
from RentalManagementApplication.frontend.views.Rooms.RoomsHome import RoomsHome
from RentalManagementApplication.frontend.views.Rooms.RoomsInfor import RoomsInfor
from RentalManagementApplication.services.InvoiceService import InvoiceService
from RentalManagementApplication.services.RoomService import RoomService
from RentalManagementApplication.services.TenantService import TenantService


class RoomMenuController:
    def __init__(self):
        self.room_service = RoomService()
        self.tenant_service = TenantService()
        self.invoice_service = InvoiceService()

    def get_room_data_list(self):
        """Lấy danh sách thông tin phòng"""
        rooms = self.room_service.get_all_rooms()
        if not rooms:
            print("[⚠️ RoomMenuController] Danh sách phòng trống, đang dùng dữ liệu mẫu.")
        return rooms


    def find_tenant_by_cccd(self, cccd):
        """Tìm người thuê theo CCCD"""
        return self.tenant_service.get_tenant_by_cccd(cccd)


    def update_tenant_for_room(self, room_id, tenant_id):
        """Cập nhật người thuê cho phòng"""
        return self.room_service.update_room_tenant(room_id, tenant_id)

    ## Xử lý nạp dữ liệu cho RoomUpdateTenant page
    def go_to_open_right_frame_room_menu(self, room_menu_instance, main_window, room_id):

        # Nếu bạn chỉ có room_id, có thể fetch landlord_id từ service trước:
        room = RoomService.get_room_by_id(room_id)
        landlord_id = room.landlord_id
        room_data_list = RoomService.handle_data_for_room_list_page(landlord_id)

        tenant_callback = self.find_tenant_by_cccd
        update_callback = self.update_tenant_for_room

        room_menu_instance.set_right_frame(
            RoomUpdateTenantPage,
            main_window,
            room_data_list,
            tenant_callback,
            update_callback,
            room_id
        )

    def go_to_open_right_frame_rooms_infor(self, room_menu_instance, main_window, room_id):
        data_room_infor = RoomService.get_translated_room_info(room_id)
        # sử dụng class + đúng số tham số match __init__(main_window, room_id, data)
        room_menu_instance.set_right_frame(
            RoomsInfor,
            main_window,
            room_id,
            data_room_infor
        )



    def open_room_detail_popup_for_tenant(self, room_id):
        try:
            print(f"[DEBUG] Đang mở chi tiết phòng cho tenant với ID: {room_id}")
            from RentalManagementApplication.frontend.views.Rooms.RoomInforFromTenantFindRoom import \
                RoomsInforViewFromTenant
            data_room_infor = RoomService.get_translated_room_info(room_id)

            popup = RoomsInforViewFromTenant(room_id, data_room_infor)
            popup.exec_()

        except Exception as e:
            import traceback
            traceback.print_exc()
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(None, "Lỗi", f"Không thể hiển thị thông tin phòng: {str(e)}")


    def go_to_open_right_frame_room_home(self, room_menu_instance, main_window, room_id):
        # xử lý dữ liệu từ service
        data_room_home = RoomService.handle_data_for_room_home(room_id)
        # truyền dữ liệu vào RoomHomes data_home
        monthly_data = RoomService.get_room_monthly_stats(room_id)
        room_menu_instance.set_right_frame(RoomsHome, main_window, room_id,data_room_home,monthly_data)


    def go_to_open_right_frame_ManagerInvoicePage(self, room_menu_instance, main_window, room_id):
        room_data_list = self.get_room_data_list()  # tất cả các phòng
        tenant_finder_callback = self.tenant_service.get_tenant_by_room_id  # theo room_id

        def preview_callback(invoice_data):
            invoice = self.invoice_service.create_invoice({
                'room': invoice_data['room'],
                'tenant': invoice_data['tenant'],
                'chi_so_dien_moi': invoice_data['chi_so_dien'],
                'chi_so_nuoc_moi': invoice_data['chi_so_nuoc'],
                'so_nguoi': invoice_data['so_nguoi'],
                'phi_khac': invoice_data['phi_khac']
            })
            print("✅ Đã tạo hóa đơn:", invoice)
            self.go_to_open_right_frame_room_home(room_menu_instance, main_window, room_id)
        # Nạp dữ liệu cho room_data_list
        room_menu_instance.set_right_frame(
            InvoiceInputPage,
            main_window,
            room_data_list,
            tenant_finder_callback,
            preview_callback
        )

    @staticmethod
    def go_to_room_management(room_id):
        print(" đây là roomMenucontroller")
        from RentalManagementApplication.frontend.views.Rooms.MainWindowRoom import MainWindowRoom
        room_window = MainWindowRoom(room_id)
        room_window.show()
    '''Đã kiểm tra đồng bộ và chuẩn hóa'''
    @staticmethod
    def go_to_handel_data_for_create_room(id_landlord, room_create_data) -> bool:
        # Trả về True/False do Service trả về
        return RoomService.handle_data_for_create_new_room(id_landlord, room_create_data)

    def delete_room(self, room_id, callback_success=None, callback_fail=None):
        result = RoomRepository.delete_room(room_id)
        if result.get('success'):
            if callback_success:
                callback_success(result)
        else:
            if callback_fail:
                callback_fail(result)


'''
room_list = RoomService.handle_data_for_room_list_page(id_lanlord)
        print("đây là room list",room_list)
        from QLNHATRO.RentalManagementApplication.frontend.views.Landlord.RoomList import RoomList
        room_list_view = RoomList(view.main_window, room_list, id_lanlord)
        view.set_right_frame(lambda *_: room_list_view)'''