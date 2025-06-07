from RentalManagementApplication.Repository.UserRepository import UserRepository


class UserService:
    def __init__(self):
        pass
    @staticmethod
    def add_user(username, password, role):
        UserRepository.add_user(username, password, role)

    @staticmethod
    def cancel_registration(username: str) -> bool:
        """
        Xóa user, return True nếu xóa thành công, False nếu không tồn tại hoặc lỗi.
        """
        return UserRepository.delete_user_by_username(username)


