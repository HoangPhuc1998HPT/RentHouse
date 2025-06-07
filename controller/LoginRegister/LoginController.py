


class LoginController:

    def __init__(self):
        self.main_window = None
        self.window = None

    ''' Đã check - đã chuẩn hóa'''
    @staticmethod
    def on_click_btn_login(main_window, username, password):
        from QLNHATRO.RentalManagementApplication.services.LoginService import LoginService
        from QLNHATRO.RentalManagementApplication.frontend.Component.ErrorDialog import ErrorDialog

        success, user, error_msg = LoginService.authenticate(username, password)
        if not success:
            ErrorDialog.show_error(error_msg or "Sai tài khoản hoặc mật khẩu", main_window)
            return

        role = user.role
        user_id = user.user_id

        if role == 'landlord':
            from QLNHATRO.RentalManagementApplication.frontend.views.Landlord.LandlordMenu import LandlordMenu
            main_window.switch_to_page(LandlordMenu, user_id)

        elif role == 'tenant':
            from QLNHATRO.RentalManagementApplication.frontend.views.Tenant.TenantMenu import TenantMenu
            main_window.switch_to_page(TenantMenu, user_id)

        elif role == 'admin':
            from QLNHATRO.RentalManagementApplication.frontend.views.Admin.AdminMenu import AdminMenu
            main_window.switch_to_page(AdminMenu, user_id)

        else:
            ErrorDialog.show_error("Vai trò không hợp lệ. Vui lòng liên hệ quản trị.", main_window)

    @staticmethod
    def go_to_change_password_view():
        from QLNHATRO.RentalManagementApplication.frontend.views.Login_Register.ForgotPassword.ChangePassword import ChangePasswordView
        change_password_window = ChangePasswordView()
        change_password_window.show()

    @staticmethod
    def go_to_forgot_password_view():
        from QLNHATRO.RentalManagementApplication.frontend.views.Login_Register.ForgotPassword.OTPVerificationView import \
            PasswordRecoveryFlow
        flow = PasswordRecoveryFlow()
        flow.start_flow()  # KHÔNG gọi flow.run()

    @staticmethod
    def go_to_home_login(main_window):
        from QLNHATRO.RentalManagementApplication.frontend.views.Login_Register.Login.HomeLogin import \
            LoginWindow as LoginWidget

        # 1) Tạo instance của login-widget, với main_window làm parent
        login_widget = LoginWidget(main_window)

        # 2) Cập nhật lại central widget của QMainWindow
        main_window.setCentralWidget(login_widget)

        # 3) (Nếu cần) điều chỉnh lại kích thước hoặc gọi lại show()
        main_window.show()

    '''
    def go_to_main_windown_lanlord(self,main_window ,user_id):
        print(f"[LoginController] sắp MainWindowLandlord với ID: {user_id}")
        id_lanlord = LanlordRepository.get_id_landlord_from_user_id(user_id)
        print(f"ID landlord lấy được: {id_lanlord}")

        try:
            print(">> đang khởi tạo MainWindowLandlord")
            #self.window = MainWindowLandlord(main_window, id_lanlord)
            print(">> đã khởi tạo xong MainWindowLandlord")
        except Exception as e:
            print(f"[ERROR] Lỗi khi khởi tạo MainWindowLandlord với ID: {id_lanlord}")
            print(e)
            traceback.print_exc()

        print(f"[LoginController] Đã tạo MainWindowLandlord với ID: {id_lanlord}")
        self.main_window.setCentralWidget(self.window)
        print(f"[LoginController] Đã setCentralWidget với ID: {id_lanlord}")
        return self.main_window
    '''