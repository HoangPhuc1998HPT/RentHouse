from PyQt5.QtCore import Qt


from QLNHATRO.RentalManagementApplication.Repository.UserRepository import UserRepository
from QLNHATRO.RentalManagementApplication.backend.model.Admin import Admin
from QLNHATRO.RentalManagementApplication.backend.model.User import User
from QLNHATRO.RentalManagementApplication.frontend.Component.ConfirmDialog import ConfirmDialog
from QLNHATRO.RentalManagementApplication.frontend.Component.ErrorDialog import ErrorDialog
from QLNHATRO.RentalManagementApplication.frontend.Component.SuccessDialog import SuccessDialog
from QLNHATRO.RentalManagementApplication.services.LandlordService import LandlordService
from QLNHATRO.RentalManagementApplication.services.LoginService import LoginService
from QLNHATRO.RentalManagementApplication.services.TenantService import TenantService
from QLNHATRO.RentalManagementApplication.services.UserService import UserService

from QLNHATRO.RentalManagementApplication.utils.Validators import Validators



class RegisterController:
    def __init__(self):
        self.user_model = User
        self.admin_model = Admin


    ''' Đã check register_user - đã chuẩn hóa'''
    @staticmethod
    def register_user(username, password, confirm_password, role, main_window):
        # 1. Validate input
        if not Validators.check_password_confirmpassword(password, confirm_password):
            ErrorDialog.show_error("Mật khẩu và xác nhận mật khẩu không khớp.", main_window)
            return

        if UserRepository.check_duplicate_user(username):
            ErrorDialog.show_error("Tên đăng nhập đã tồn tại. Vui lòng chọn tên khác.", main_window)
            return

        try:
            # 2. Thêm user mới vào database
            UserService.add_user(username, password, role)
            user_id = LoginService.get_user_id_from_username(username)
            if role == "landlord":
                lan = LandlordService.create_empty_landlord(user_id)
                if lan is None:
                    ErrorDialog.show_error("Lỗi khởi tạo chủ trọ.", main_window)
                    return
            elif role == "tenant":
                ten = TenantService.create_empty_tenant(user_id)
                if ten is None:
                    ErrorDialog.show_error("Lỗi khởi tạo tenant.", main_window)
                    return

            # 3. Điều hướng đến màn hình cập nhật thông tin cá nhân
            RegisterController.navigate_to_update_info(main_window, user_id,username, role)

        except Exception as e:
            ErrorDialog.show_error(f"Đăng ký thất bại: {str(e)}", main_window)

    '''Đã check navigate_to_update_info điều hướng tốt '''
    @staticmethod
    def navigate_to_update_info(main_window, user_id, username, role):
        """
        Mở cửa sổ cập nhật thông tin sau đăng ký thành công.
        Không chuyển trang mà mở form riêng.
        """
        from QLNHATRO.RentalManagementApplication.frontend.views.Login_Register.Login.HomeLogin import LoginWindow
        from QLNHATRO.RentalManagementApplication.frontend.views.Login_Register.Register.UpdateInfomationAfterRegister import \
            OptimizedUpdateInfoView

        update_window = OptimizedUpdateInfoView(main_window = main_window,
            role=role,
            username=username,
            user_id=user_id,
            save_callback=lambda: (
                RegisterController.complete_registration(main_window),
                update_window.close(),
                main_window.switch_to_page(LoginWindow)
            ),
            cancel_callback=lambda: (
                RegisterController.cancel_registration(main_window, username),
                update_window.close(),
                main_window.switch_to_page(LoginWindow)
            )
        )
        update_window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        update_window.show()
        update_window.activateWindow()

    ''' Đã check cancel_registration - đã chuẩn hóa '''
    @staticmethod
    def complete_registration(main_window):
        SuccessDialog.show_success("Đăng ký thành công! Vui lòng đăng nhập.", "Active", main_window)
        main_window.switch_to_login_view()

    ''' Đã check cancel_registration - đã chuẩn hóa '''
    @staticmethod
    def cancel_registration(main_window, username):
        """
        Xác nhận hủy đăng ký và xoá người dùng khỏi hệ thống.
        Điều phối show dialog, gọi service, và điều hướng view.
        """
        confirm = ConfirmDialog.ask(main_window, "Bạn có chắc muốn hủy đăng ký?\nTài khoản sẽ bị xóa?")
        if not confirm:
            return

        try:
            from QLNHATRO.RentalManagementApplication.services.UserService import UserService
            deleted = UserService.cancel_registration(username)
            if deleted:
                SuccessDialog.show_success("Đã hủy đăng ký và xóa tài khoản tạm thời.", "Pending", main_window)
            else:
                ErrorDialog.show_error("Không tìm thấy tài khoản để xóa.", main_window)
            main_window.switch_to_register_view()
        except Exception as e:
            ErrorDialog.show_error(f"Lỗi khi hủy đăng ký: {str(e)}", main_window)

