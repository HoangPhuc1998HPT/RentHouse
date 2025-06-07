# QLNHATRO/services/OTPService.py
import random


class OTPService:
    # Lưu tạm OTP theo username (giả lập, mỗi lần restart app sẽ mất)
    otp_store: dict[str, str] = {}

    @staticmethod
    def generate_otp(username: str) -> str:
        """
        Sinh ngẫu nhiên một mã OTP 4 chữ số, lưu vào otp_store theo username,
        rồi trả về mã này để controller có thể hiển thị cho user.
        """
        # Tạo một chuỗi gồm 4 chữ số ngẫu nhiên
        otp = ''.join(str(random.randint(0, 9)) for _ in range(4))
        # Lưu vào dict tạm
        OTPService.otp_store[username] = otp
        return otp

    @staticmethod
    def verify_otp(username: str, otp: str) -> bool:
        """
        Kiểm tra mã otp nhập vào có bằng mã đã generate cho username hay không.
        Nếu đúng thì xoá otp đó khỏi store và trả về True.
        Ngược lại trả về False.
        """
        stored = OTPService.otp_store.get(username)
        if stored is not None and stored == otp:
            # Xoá mã đã dùng để tránh reuse
            del OTPService.otp_store[username]
            return True
        return False

    @staticmethod
    def check_change_password(username: str, current_password: str) -> bool:
        """
        (Giữ nguyên hoặc tuỳ bạn implement)
        Kiểm tra user+password truyền vào có đúng không.
        """
        # TODO: Thực tế sẽ query DB, ở đây tạm luôn True
        return True