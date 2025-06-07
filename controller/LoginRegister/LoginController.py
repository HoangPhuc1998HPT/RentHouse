from RentalManagementApplication.services.LandlordService import LandlordService
from RentalManagementApplication.services.TenantService import TenantService


class LoginController:

    def __init__(self):
        self.main_window = None
        self.window = None

    ''' Đã check - đã chuẩn hóa'''
    @staticmethod
    def on_click_btn_login(main_window, username, password):
        from RentalManagementApplication.services.LoginService import LoginService
        from RentalManagementApplication.frontend.Component.ErrorDialog import ErrorDialog

        success, user, error_msg = LoginService.authenticate(username, password)
        if not success:
            ErrorDialog.show_error(error_msg or "Sai tài khoản hoặc mật khẩu", main_window)
            return

        role = user.role
        user_id = user.user_id

        if role == 'landlord':
            from RentalManagementApplication.frontend.views.Landlord.LandlordMenu import LandlordMenu
            id_landlord = LandlordService.get_landlord_id_by_user_id(user_id)
            main_window.switch_to_page(LandlordMenu, id_landlord)

        elif role == 'tenant':
            from RentalManagementApplication.frontend.views.Tenant.TenantMenu import TenantMenu
            id_tenant = TenantService.get_tenant_id_by_user_id(user_id)
            main_window.switch_to_page(TenantMenu, id_tenant)

        elif role == 'admin':
            from RentalManagementApplication.frontend.views.Admin.AdminMenu import AdminMenu
            main_window.switch_to_page(AdminMenu, user_id)

        else:
            ErrorDialog.show_error("Vai trò không hợp lệ. Vui lòng liên hệ quản trị.", main_window)

    @staticmethod
    def go_to_change_password_view():
        from RentalManagementApplication.frontend.views.Login_Register.ForgotPassword.ChangePassword import ChangePasswordView
        change_password_window = ChangePasswordView()
        change_password_window.show()

    @staticmethod
    def go_to_forgot_password_view():
        from RentalManagementApplication.frontend.views.Login_Register.ForgotPassword.OTPVerificationView import \
            PasswordRecoveryFlow
        flow = PasswordRecoveryFlow()
        flow.start_flow()  # KHÔNG gọi flow.run()

    @staticmethod
    def go_to_home_login(main_window):
        from RentalManagementApplication.frontend.views.Login_Register.Login.HomeLogin import \
            LoginWindow as LoginWidget

        # 1) Tạo instance của login-widget, với main_window làm parent
        login_widget = LoginWidget(main_window)

        # 2) Cập nhật lại central widget của QMainWindow
        main_window.setCentralWidget(login_widget)

        # 3) (Nếu cần) điều chỉnh lại kích thước hoặc gọi lại show()
        main_window.show()
