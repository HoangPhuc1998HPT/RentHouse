from PyQt5.QtWidgets import QMessageBox

from RentalManagementApplication.Repository.LoginRepository import LoginRepository
from RentalManagementApplication.Repository.UserRepository import UserRepository
from RentalManagementApplication.controller.UpdateInfor.UpdateInfoController import UpdateInfoController
from RentalManagementApplication.frontend.Component.ErrorDialog import ErrorDialog


class LoginService:
    def __init__(self):
        pass

    landlord_window = None  # thuộc tính class-level
    '''Đã check - đã chuẩn hóa    '''
    @staticmethod
    def authenticate(username, password):
        """
        Trả về tuple (success, user object hoặc None, thông báo lỗi nếu có)
        """
        user = UserRepository.get_user_by_username(username)
        if not user:
            return False, None, "Tài khoản không tồn tại."

        # So sánh mật khẩu đã hash
        hashed_input = UserRepository.hash_password(password)
        if user.password != hashed_input:
            return False, None, "Mật khẩu không đúng."

        if user.is_active == 0:
            return False, None, "Tài khoản chưa được kích hoạt hoặc bị khóa."

        return True, user, None

    @staticmethod
    def get_user_id_from_username(username):
        """
        Lấy user_id từ username.
        :param username: Tên đăng nhập của người dùng.
        :return: user_id nếu tìm thấy, None nếu không tìm thấy.
        """
        UserRepository.get_user_id_from_username(username)
    # xử lý 1 vấn đề là check user tồn tại và password đúng
    @staticmethod
    #"admin" "admin"
    def check_login(username, password):
        # giả lập truy vấn cho ra kết quả
        print("login được gọi")
        user = LoginRepository.get_user(username)
        print(user)
        if username == user['username'] and password == user['password']:
            print("user và passowrd đúng rồi")
            #LoginService.open_dashboard_window_and_close_login(login_window, user['role'], int(user['user_id']))
            return True
        else:
            QMessageBox.information(None, 'Thông báo', 'Sai tên tài khoản hoặc mật khẩu!')
            return False


    @staticmethod
    def close_main_window(main_window):
        main_window.close()

    @staticmethod
    def check_confim_password(password, confim_password):
        if password == confim_password:
            return True
        else:
            print("Không khớp mật khẩu")
            return False

    @staticmethod
    def handle_data_user_to_create_new_user(user, main_window):
        """
        user = [username, password, role]
        - Bước 1: Kiểm tra trùng username (nếu trùng -> báo lỗi / return).
        - Bước 2: Hash mật khẩu.
        - Bước 3: Gọi LoginRepository.create_new_user_name để chèn vào Users.
        - Bước 4: Nếu chèn thành công (trả về user_id), khởi UpdateInfoController.
        """
        username, password, role = user

        # 1. Kiểm tra trùng username
        if UserRepository.check_duplicate_user(username):
            ErrorDialog.show_error("Tên tài khoản đã tồn tại, vui lòng chọn tên khác.")
            return

        # 2. Hash mật khẩu
        hashed_password = UserRepository.hash_password(password)

        # 3. Chèn vào bảng Users (Repository chỉ làm INSERT)
        new_user_id = LoginRepository.create_new_user_name(username, hashed_password, role)
        if new_user_id is None:
            ErrorDialog.show_error("Không thể tạo tài khoản mới. Vui lòng thử lại.")
            return
        # 4. Chuyển sang bước cập nhật thông tin (UpdateInfoController)
        controller = UpdateInfoController(main_window, role, username, hashed_password, new_user_id)
        controller.show()


