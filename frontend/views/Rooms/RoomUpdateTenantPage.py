from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit,
    QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt


from RentalManagementApplication.frontend.Component.ErrorDialog import ErrorDialog
from RentalManagementApplication.frontend.Component.SuccessDialog import SuccessDialog
from RentalManagementApplication.frontend.Style.GlobalStyle import GlobalStyle
from RentalManagementApplication.services.RoomService import RoomService


class RoomUpdateTenantPage(QWidget):
    def __init__(self, main_window, room_data_list, tenant_finder_callback, update_tenant_callback, room_id):
        super().__init__()
        self.setStyleSheet(GlobalStyle.global_stylesheet())
        self.room_id = room_id
        self.main_window = main_window
        self.room_data_list = room_data_list  # List of room dicts
        self.tenant_finder_callback = tenant_finder_callback
        self.update_tenant_callback = update_tenant_callback
        self.selected_room = None
        self.found_tenant = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        #self.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #FFDEE9, stop:1 #B5FFFC);")

        # ===== Title =====
        title = QLabel("Cập nhật Người thuê cho Phòng trọ")
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("Title")
        title.setFixedHeight(60)
        layout.addWidget(title)

        # ===== Chọn phòng =====
        room_layout = QHBoxLayout()
        room_label = QLabel("Chọn phòng:")
        #room_label.setStyleSheet("font-weight: bold;color: black ; padding: 5px; background-color: #0192F4; border-radius: 8px;")
        room_label.setFixedWidth(100)


        self.room_combo = QComboBox()
        self.room_combo.setMinimumWidth(300)
        #self.room_combo.setStyleSheet("padding: 5px; font-weight: bold; background-color: white; border-radius: 8px;")

        for room in self.room_data_list:
            label = room['ten_phong']
            uid = room['id_room']
            self.room_combo.addItem(f"{label} – ID: {uid}", userData=room)
        self.room_combo.setFixedWidth(300)
        self.room_combo.currentIndexChanged.connect(self.display_room_info)

        room_layout.addWidget(room_label)
        room_layout.setAlignment(Qt.AlignLeft)
        room_layout.addWidget(self.room_combo)
        layout.addLayout(room_layout)

        # ===== Thông tin phòng =====
        self.room_info_label = QLabel("Thông tin phòng sẽ hiển thị ở đây")
        layout.addWidget(self.room_info_label)

        # ===== Nhập CCCD =====
        cccd_layout = QHBoxLayout()

        cccd_label = QLabel("Nhập CCCD người thuê:")
        cccd_label.setFixedWidth(160)

        self.cccd_input = QLineEdit()
        self.cccd_input.setFixedWidth(250)
        self.cccd_input.setPlaceholderText("VD: 082098013220")
        #self.cccd_input.setStyleSheet("padding: 5px; border-radius: 5px; background-color: white;")

        self.find_tenant_btn = QPushButton("Tìm người thuê")
        self.find_tenant_btn.setFixedWidth(200)
        self.find_tenant_btn.clicked.connect(self.find_tenant)

        cccd_layout.addWidget(cccd_label)
        cccd_layout.addWidget(self.cccd_input)
        cccd_layout.addWidget(self.find_tenant_btn)

        # Căn trái toàn bộ dòng CCCD
        cccd_layout.setAlignment(Qt.AlignLeft)

        layout.addLayout(cccd_layout)

        # ===== Thông tin người thuê =====
        self.tenant_info_label = QLabel("Thông tin người thuê sẽ hiển thị ở đây")
        layout.addWidget(self.tenant_info_label)

        # ===== Nút cập nhật =====
        self.update_btn = QPushButton("Cập nhật người thuê vào phòng")
        self.update_btn.setFixedWidth(300)
        self.update_btn.clicked.connect(self.update_tenant_to_room)
        layout.addWidget(self.update_btn, alignment=Qt.AlignCenter)

        self.display_room_info()
    # xử lý nạp dữ liệu room
    def display_room_info(self):
        room = self.room_combo.currentData()
        if room:
            self.selected_room = room
            info = (
                    f"Tên phòng: {room['ten_phong']}\n"
                    f"Giá phòng: {room['gia']} VNĐ\n"
                    f"Chỉ số điện: {room['so_dien']}\n"
                    f"Chỉ số nước: {room['so_nuoc']}\n"
                     # nếu bạn muốn hiển thị diện tích, service phải bổ sung thêm 'dien_tich'
                    )
            self.room_info_label.setText(info)
        else:
            self.room_info_label.setText("Không có thông tin phòng")

    def find_tenant(self):
        cccd = self.cccd_input.text().strip()
        if not cccd:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập CCCD.")
            return
        tenant = self.tenant_finder_callback(cccd)
        if tenant:
            self.found_tenant = tenant
            self.tenant_info_label.setText(
                f"Họ tên: {tenant['name_tenant']}\n"
                f"SĐT: {tenant['phone']}\n"
                f"CCCD: {tenant['cccd']}\n"
                f"Email: {tenant['email']}"
            )
        else:
            self.tenant_info_label.setText("Không tìm thấy người thuê với CCCD này.")
            self.found_tenant = None

    def update_tenant_to_room(self):
        if not self.selected_room or not self.found_tenant:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn phòng và tìm người thuê.")
            return
        # gọi cái hàm lấy data từ UI gửi đi update
        call_update = RoomService.get_data_send_to_update_tenant_rent_room(self.selected_room['id'], self.found_tenant['id'])
        confirm = QMessageBox.question(self, "Xác nhận", "Bạn chắc chắn muốn cập nhật người thuê vào phòng?")
        if confirm == QMessageBox.Yes & call_update==True:
            self.update_tenant_callback(self.selected_room['id'], self.found_tenant['id'])
            SuccessDialog.show_success("Đã cập nhật người thuê vào phòng thành công!", self)
            #QMessageBox.information(self, "Thành công", "Đã cập nhật người thuê vào phòng thành công.")
        else:
            ErrorDialog.show_error("Cập nhật người thuê vào phòng thất bại!", self)
