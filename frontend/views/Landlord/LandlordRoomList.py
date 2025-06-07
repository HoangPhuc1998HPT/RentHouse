from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame
)

from RentalManagementApplication.frontend.Component.tableUI import TableUI
from RentalManagementApplication.frontend.Style.GlobalStyle import GlobalStyle


class RoomList(QWidget):
    def __init__(self, main_window, room_list, id_lanlord):
        super().__init__()
        self.setStyleSheet(GlobalStyle.global_stylesheet())
        self.main_window = main_window
        self.id_lanlord = id_lanlord
        self.id_room = None
        self.room_list = room_list

        # Layout chính
        main_layout = QVBoxLayout(self)

        # Tiêu đề
        title = QLabel("🏠 Danh sách phòng trọ")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Frame chứa table (để style bo tròn + shadow)
        frame = QFrame()
        frame.setObjectName("tableCard")
        frame_layout = QVBoxLayout(frame)

        # Khởi tạo TableUI với header
        headers = ["STT", "Tên phòng", "Người thuê", "Giá", "Số điện", "Số nước", "Tình trạng hóa đơn", "Xem chi tiết"]
        self.table = TableUI(headers)

        # Định nghĩa mapping key
        header_to_key = {
            "STT": "stt",
            "Tên phòng": "ten_phong",
            "Người thuê": "nguoi_thue",
            "Giá": "gia",
            "Số điện": "so_dien",
            "Số nước": "so_nuoc",
            "Tình trạng hóa đơn": "hoa_don"
        }

        # Populate data và gắn callback cho nút
        self.table.populate(
            self.room_list,
            has_button=True,
            button_callback=self.show_room_details,
            header_to_key=header_to_key
        )

        # Đưa table vào frame, rồi frame vào layout
        frame_layout.addWidget(self.table)
        main_layout.addWidget(frame)

        self.setLayout(main_layout)

    def show_room_details(self, row):
        room = self.room_list[row]
        self.id_room = room.get('id_room')
        if self.id_room:
            print(f"🔍 Mở chi tiết phòng: {room['ten_phong']} (ID: {self.id_room})")
            from RentalManagementApplication.controller.RoomController.RoomMenuController import RoomMenuController
            RoomMenuController.go_to_room_management(self.id_room)
        else:
            print("❌ Không tìm thấy ID phòng trong dữ liệu.")
