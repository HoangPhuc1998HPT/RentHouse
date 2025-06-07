from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QHBoxLayout,
    QPushButton, QGroupBox, QMessageBox
)

from QLNHATRO.RentalManagementApplication.backend.model.Landlord import Landlord
from QLNHATRO.RentalManagementApplication.frontend.Component.LabelUI import LabelUI
from QLNHATRO.RentalManagementApplication.frontend.Style.GlobalStyle import GlobalStyle
from QLNHATRO.RentalManagementApplication.frontend.Component.InforUpdater import InfoUpdater

''' Đã kiểm tra đồng bộ dữ liệu và chuẩn hóa '''
class LandlordInfo(QWidget):
    def __init__(self, main_window, landlord):
        super().__init__()
        self.setStyleSheet(GlobalStyle.global_stylesheet())
        if isinstance(landlord, dict):
            self.landlord = Landlord(landlord)
        else:
            self.landlord = landlord
        self.id_lanlord = self.landlord.landlord_id

        self.main_window = main_window
        self.information = {
            'name': landlord.fullname,
            'birth': landlord.birth,
            'cccd': landlord.cccd,
            'gender': landlord.gender,
            'job_title': landlord.job_title,
            'email': landlord.email,
            'phone_number': landlord.phone_number,
            'marital_status': landlord.marital_status,
            # Thêm các thông tin phục vụ mục đích nâng cấp ứng dụng sau này
            'username': landlord.username,
            'so_phong': landlord.so_phong,
            'created_at': landlord.created_at,
        }

        main_layout = QVBoxLayout()

        title = QLabel("👤 THÔNG TIN CHỦ TRỌ")
        #title.setStyleSheet("font-size: 24px; font-weight: bold;")
        title.setObjectName("Title")  # ✅ sẽ dùng style của QLabel#Title
        title.setFixedHeight(60)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        content_widget = QWidget()
        content_layout = QVBoxLayout()

        field_names = [
            "Họ và Tên", "Ngày Sinh", "CCCD", "Giới tính",
            "Nghề nghiệp", "Email", "Số điện thoại", "Tình trạng hôn nhân"
        ]
        field_keys = [
            'name', 'birth', 'cccd', 'gender',
            'job_title', 'email', 'phone_number', 'marital_status'
        ]

        self.label_fields = []

        for i, field in enumerate(field_names):
            group = QGroupBox()
            hbox = QHBoxLayout()

            label = QLabel(f"{field}:")
            label.setStyleSheet("font-size: 16px; min-width: 140px;")

            try:
                value = self.information.get(field_keys[i], "Chưa có dữ liệu")
                label_ui = LabelUI(str(value))
            except Exception as e:
                print(f"Lỗi khi tạo LabelUI ở chỉ mục {i}: {e}")
                continue
            else:
                self.label_fields.append(label_ui)

                update_btn = QPushButton("Cập nhật")
                update_btn.setFixedHeight(40)
                update_btn.setFixedWidth(200)
                update_btn.clicked.connect(lambda _, index=i: self.update_field(index))

                hbox.addWidget(label)
                hbox.addWidget(label_ui, stretch=1)
                hbox.addWidget(update_btn)
                group.setLayout(hbox)
                content_layout.addWidget(group)

        # ➕ Thêm phần mật khẩu riêng
        #password_group = QGroupBox()
        #password_layout = QHBoxLayout()

        #password_label = QLabel("Mật khẩu:")
        #password_label.setStyleSheet("font-size: 16px; min-width: 140px;")
        #password_ui = LabelUI("**********")

        #change_pass_btn = QPushButton("Đổi mật khẩu")
        #change_pass_btn.clicked.connect(self.open_change_password_dialog)

        #password_layout.addWidget(password_label)
        #password_layout.addWidget(password_ui, stretch=1)
        #password_layout.addWidget(change_pass_btn)
        #password_group.setLayout(password_layout)

        #content_layout.addWidget(password_group)

        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        self.setLayout(main_layout)

    def update_field(self, index):
        label = self.label_fields[index]
        field_name = [
            "Họ và Tên", "Ngày Sinh", "CCCD", "Giới tính",
            "Nghề nghiệp", "Số điện thoại", "Tình trạng hôn nhân"
        ][index]

        dialog = InfoUpdater(
            title=field_name,
            current_value=label.text(),
            on_update_callback=lambda new_val: self.apply_update(index, new_val)
        )
        dialog.exec_()

    def apply_update(self, index, new_value):
        field_keys = ['name', 'birth', 'cccd', 'sex', 'job', 'phone', 'marriage']
        key = field_keys[index]

        self.label_fields[index].setText(new_value)
        self.information[key] = new_value
        print(f"✅ Đã cập nhật {key}: {new_value}")

        from QLNHATRO.RentalManagementApplication.controller.LandlordController.LandlordController import LandlordController
        controller = LandlordController()
        controller.update_landlord_field(self.id_lanlord, key, new_value)

    def open_change_password_dialog(self):
        QMessageBox.information(self, "Đổi mật khẩu", "Mở cửa sổ đổi mật khẩu tại đây.")
        # TODO: sau này sẽ mở form nhập mật khẩu cũ + mới để xác nhận
