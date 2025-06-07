
from PyQt5.QtWidgets import QMessageBox
from RentalManagementApplication.frontend.Component.ErrorDialog import ErrorDialog
from RentalManagementApplication.services.OTPService import OTPService

class OTPController:
    @staticmethod
    def request_initial_otp(username: str, email: str, parent_view=None):
        """
        Yêu cầu backend (ở đây giả lập) tạo và gửi OTP lần đầu.
        - username: tên người dùng
        - email: email nhận OTP
        - parent_view: QWidget để show dialog, nếu có
        Trả về (success: bool, message: str).
        """
        if not username or not email:
            return False, "Thiếu thông tin username hoặc email."

        # 1. Sinh OTP và lưu tạm
        otp = OTPService.generate_otp(username)
        # 2. Giả lập gửi email: show ra QMessageBox (hoặc custom SuggestDialog)
        msg = QMessageBox(parent_view)
        msg.setWindowTitle("Mã OTP đã được gửi")
        msg.setText(f"Mã OTP của bạn là:\n\n<b>{otp}</b>")
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

        return True, f"OTP đã được gửi đến {email}."

    @staticmethod
    def verify_otp(otp_text: str, username: str, view_instance):
        """
        Xác thực mã OTP do user nhập:
        - otp_text: chuỗi 4 chữ số user nhập
        - username: để so sánh với mã đã lưu
        - view_instance: instance của OTPVerificationView, để gọi reset hoặc chuyển view
        """
        # 1. Kiểm tra format: phải đủ 4 ký tự số
        if len(otp_text) != 4 or not otp_text.isdigit():
            ErrorDialog.show_error("⚠️ Vui lòng nhập đủ 4 chữ số mã OTP.", view_instance)
            return

        # 2. Gọi service để verify
        is_correct = OTPService.verify_otp(username, otp_text)
        if is_correct:
            # Dừng timer trong view
            try:
                view_instance.timer.stop()
            except Exception:
                pass

            # Chuyển sang ResetPasswordView (giống logic cũ của bạn)
            from RentalManagementApplication.frontend.views.Login_Register.ForgotPassword.ResetPasswordView import ResetPasswordView

            view_instance.reset_password_view = ResetPasswordView(username=username)
            view_instance.hide()
            view_instance.reset_password_view.show()
        else:
            # Mã sai, show error và clear lại ô
            ErrorDialog.show_error("❌ Mã OTP không chính xác hoặc đã hết hạn.", view_instance)
            view_instance.reset_otp_fields()

    @staticmethod
    def resend_otp(username: str, email: str, view_instance):
        """
        Gửi lại OTP (generate mới).
        - username, email: thông tin để generate lại mã
        - view_instance: instance OTPVerificationView, để reset timer/fields
        """
        if not username or not email:
            ErrorDialog.show_error("Thiếu thông tin username hoặc email.", view_instance)
            return

        # 1. Sinh OTP mới
        otp = OTPService.generate_otp(username)
        # 2. Hiển thị lại
        msg = QMessageBox(view_instance)
        msg.setWindowTitle("Gửi lại OTP")
        msg.setText(f"Mã OTP mới của bạn là:\n\n<b>{otp}</b>")
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

        # 3. Reset các ô nhập và timer
        view_instance.reset_otp_fields()
        try:
            view_instance.remaining_seconds = 120
            view_instance.timer.start(1000)
        except Exception:
            pass

    @staticmethod
    def go_to_reset_password(view_instance, username: str):
        """
        Chuyển thẳng sang màn hình ResetPassword (nếu cần từ view khác).
        """
        from RentalManagementApplication.frontend.views.Login_Register.ForgotPassword.ResetPasswordView import ResetPasswordView

        view_instance.hide()
        view_instance.reset_password_view = ResetPasswordView(username=username)
        view_instance.reset_password_view.show()

    @staticmethod
    def go_to_opt_view(email_sdt, username):
        from RentalManagementApplication.frontend.views.Login_Register.ForgotPassword.OTPVerificationView import \
            OTPVerificationView
        otp_window = OTPVerificationView(email_sdt = email_sdt, username= username)
        otp_window.show()


