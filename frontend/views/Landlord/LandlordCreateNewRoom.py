from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QComboBox, QPushButton, QGroupBox,
    QVBoxLayout, QHBoxLayout, QMessageBox,
    QCheckBox, QGridLayout, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator

from RentalManagementApplication.controller.RoomController.RoomMenuController import RoomMenuController
from RentalManagementApplication.frontend.Style.GlobalStyle import GlobalStyle
from RentalManagementApplication.utils.Validators import Validators

''' Đã kiểm tra đã đồng bộ và chuẩn hóa '''
class CreateNewRoom(QWidget):
    def __init__(self, main_window=None, id_landlord=None):
        super().__init__()
        self.setStyleSheet(GlobalStyle.global_stylesheet())
        self.create_data_for_update = {}
        self.id_landlord = id_landlord
        self.main_window = main_window

        # Thiết lập khu vực cuộn cho trường hợp form dài
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(20, 20, 20, 20)
        scroll_layout.setSpacing(15)

        # NỀN TRẮNG CHỨA NỘI DUNG
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # TIÊU ĐỀ
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("🏠 Tạo phòng trọ mới")
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("Title")
        title.setFixedHeight(60)
        header_layout.addWidget(title)

        # Thông tin hướng dẫn
        desc_box = QGroupBox("Hướng dẫn")
        desc_box.setProperty("theme", "blue")
        desc_layout = QVBoxLayout(desc_box)

        desc = QLabel("• Vui lòng điền đầy đủ thông tin để thêm phòng mới vào hệ thống.")
        desc.setObjectName("sectionLabel")
        desc.setAlignment(Qt.AlignLeft)

        desc_1 = QLabel("• Các trường đánh dấu (*) là bắt buộc phải nhập.")
        desc_1.setObjectName("infoLabel")
        desc_1.setAlignment(Qt.AlignLeft)

        desc_2 = QLabel("• Đảm bảo nhập đúng định dạng số cho các trường giá tiền và diện tích.")
        desc_2.setObjectName("infoLabel")
        desc_2.setAlignment(Qt.AlignLeft)

        desc_layout.addWidget(desc)
        desc_layout.addWidget(desc_1)
        desc_layout.addWidget(desc_2)

        scroll_layout.addWidget(header_widget)
        scroll_layout.addWidget(desc_box)

        # THÔNG TIN CƠ BẢN VỀ PHÒNG
        basic_info_box = QGroupBox("Thông tin cơ bản")
        basic_info_box.setProperty("theme", "blue")
        basic_info_layout = QGridLayout(basic_info_box)

        # Đặt style cho combo & input đồng bộ
        def style_input(widget):
            widget.setFixedHeight(36)
            widget.setStyleSheet("padding-left: 5px;")
            return widget

        def create_input_with_unit(unit_text=None, placeholder="", validator=None):
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)

            input = QLineEdit()
            input.setPlaceholderText(placeholder)
            style_input(input)

            if validator:
                input.setValidator(validator)

            layout.addWidget(input)

            if unit_text:
                unit = QLabel(unit_text)
                unit.setObjectName("keyLabel")
                unit.setFixedWidth(80)
                unit.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                layout.addWidget(unit)

            return input, container

        # Validators
        number_validator = QRegExpValidator(QRegExp(r"[0-9]+"))
        decimal_validator = QRegExpValidator(QRegExp(r"[0-9]+(\.[0-9]+)?"))

        # Input Widgets
        room_name_label = QLabel("Tên phòng: *")
        room_name_label.setObjectName("keyLabel")
        self.input_name_room = style_input(QLineEdit())
        self.input_name_room.setPlaceholderText("Nhập tên phòng (vd: Phòng 101)")

        people_label = QLabel("Số người tối đa: *")
        people_label.setObjectName("keyLabel")
        self.input_number_people_room = style_input(QLineEdit())
        self.input_number_people_room.setPlaceholderText("Nhập số người tối đa")
        self.input_number_people_room.setValidator(number_validator)

        address_label = QLabel("Địa chỉ: *")
        address_label.setObjectName("keyLabel")
        self.input_address_room = style_input(QLineEdit())
        self.input_address_room.setPlaceholderText("Nhập địa chỉ chi tiết")

        type_label = QLabel("Loại phòng: *")
        type_label.setObjectName("keyLabel")
        self.input_type_room = QComboBox()
        self.input_type_room.addItems(
            ["Phòng trọ", "Chung cư mini", "Nhà nguyên căn", "Chung cư", "Nhà mặt phố", "Khác"])
        style_input(self.input_type_room)

        status_label = QLabel("Trạng thái:")
        status_label.setObjectName("keyLabel")
        self.input_status_room = QComboBox()
        self.input_status_room.addItems(["Trống", "Đã thuê", "Đang sửa chữa", "Đặt cọc"])
        style_input(self.input_status_room)

        # Thêm vào layout
        basic_info_layout.addWidget(room_name_label, 0, 0)
        basic_info_layout.addWidget(self.input_name_room, 0, 1)
        basic_info_layout.addWidget(type_label, 0, 2)
        basic_info_layout.addWidget(self.input_type_room, 0, 3)

        basic_info_layout.addWidget(people_label, 1, 0)
        basic_info_layout.addWidget(self.input_number_people_room, 1, 1)
        basic_info_layout.addWidget(status_label, 1, 2)
        basic_info_layout.addWidget(self.input_status_room, 1, 3)

        basic_info_layout.addWidget(address_label, 2, 0)
        self.input_address_room.setMinimumWidth(300)
        basic_info_layout.addWidget(self.input_address_room, 2, 1, 1, 3)

        scroll_layout.addWidget(basic_info_box)

        # THÔNG TIN GIÁ PHÒNG VÀ DIỆN TÍCH
        price_info_box = QGroupBox("Thông tin giá và diện tích")
        price_info_box.setProperty("theme", "blue")
        price_info_layout = QGridLayout(price_info_box)

        area_label = QLabel("Diện tích: *")
        area_label.setObjectName("keyLabel")
        self.input_area, area_container = create_input_with_unit("m²", "Nhập diện tích", decimal_validator)

        price_room_label = QLabel("Giá thuê: *")
        price_room_label.setObjectName("keyLabel")
        self.input_price_room, price_room_container = create_input_with_unit("VNĐ/tháng", "Nhập giá thuê",
                                                                             number_validator)

        price_electric_label = QLabel("Giá điện:")
        price_electric_label.setObjectName("keyLabel")
        self.input_price_electric, price_electric_container = create_input_with_unit("VNĐ/kWh", "Nhập giá điện",
                                                                                     number_validator)

        price_water_label = QLabel("Giá nước:")
        price_water_label.setObjectName("keyLabel")
        self.input_price_water, price_water_container = create_input_with_unit("VNĐ/m³", "Nhập giá nước",
                                                                               number_validator)
        # Giả sử giá Internet là tùy chọn, không bắt buộc
        price_internet_label = QLabel("Giá Internet:")
        price_internet_label.setObjectName("keyLabel")
        self.input_price_internet, price_internet_container = create_input_with_unit("VNĐ/tháng", "Nhập giá Internet", number_validator)

        # Giá rác
        price_garbage_label = QLabel("Giá rác:")
        price_garbage_label.setObjectName("keyLabel")
        self.input_price_garbage, price_garbage_container = create_input_with_unit("VNĐ/tháng", "Nhập giá rác", number_validator)

        # Thêm vào layout
        price_info_layout.addWidget(area_label, 0, 0)
        price_info_layout.addWidget(area_container, 0, 1)
        price_info_layout.addWidget(price_room_label, 0, 2)
        price_info_layout.addWidget(price_room_container, 0, 3)

        price_info_layout.addWidget(price_electric_label, 1, 0)
        price_info_layout.addWidget(price_electric_container, 1, 1)
        price_info_layout.addWidget(price_water_label, 1, 2)
        price_info_layout.addWidget(price_water_container, 1, 3)

        # Thêm dòng mới vào layout hiển thị giá Internet và giá rác
        price_info_layout.addWidget(price_internet_label, 2, 0)
        price_info_layout.addWidget(price_internet_container, 2, 1)
        price_info_layout.addWidget(price_garbage_label, 2, 2)
        price_info_layout.addWidget(price_garbage_container, 2, 3)

        scroll_layout.addWidget(price_info_box)

        # CHỈ SỐ ĐỒNG HỒ
        meter_info_box = QGroupBox("Chỉ số đồng hồ ban đầu")
        meter_info_box.setProperty("theme", "blue")
        meter_info_layout = QGridLayout(meter_info_box)

        number_electric_label = QLabel("Số điện ban đầu:")
        number_electric_label.setObjectName("keyLabel")
        self.input_number_electric, number_electric_container = create_input_with_unit("kWh",
                                                                                       "Nhập chỉ số đồng hồ điện",
                                                                                       number_validator)

        number_water_label = QLabel("Số nước ban đầu:")
        number_water_label.setObjectName("keyLabel")
        self.input_number_water, number_water_container = create_input_with_unit("m³", "Nhập chỉ số đồng hồ nước",
                                                                                 number_validator)

        # Thêm vào layout
        meter_info_layout.addWidget(number_electric_label, 0, 0)
        meter_info_layout.addWidget(number_electric_container, 0, 1)
        meter_info_layout.addWidget(number_water_label, 0, 2)
        meter_info_layout.addWidget(number_water_container, 0, 3)

        scroll_layout.addWidget(meter_info_box)

        # THÔNG TIN TIỆN ÍCH
        amenities_box = QGroupBox("Tiện ích phòng")
        amenities_box.setProperty("theme", "blue")
        amenities_layout = QGridLayout(amenities_box)

        self.cb_wifi = QCheckBox("Wifi miễn phí")
        self.cb_parking = QCheckBox("Chỗ để xe")
        self.cb_aircon = QCheckBox("Máy lạnh/Điều hòa")
        self.cb_fridge = QCheckBox("Tủ lạnh")

        self.cb_wm = QCheckBox("Máy giặt")
        self.cb_security = QCheckBox("Bảo vệ 24/7")
        self.cb_tv = QCheckBox("TV")
        self.cb_kitchen = QCheckBox("Bếp")
        # ---
        self.cb_floor = QCheckBox("Tầng lầu")
        self.cb_hasLoft = QCheckBox("Gác lửng")
        self.cb_bathroom = QCheckBox("Phòng tắm")
        self.cb_balcony = QCheckBox("Ban công")

        self.cb_funiture = QCheckBox("Nội thất cơ bản")
        self.cb_pet = QCheckBox("Thú cưng")

        # Thêm vào layout
        amenities_layout.addWidget(self.cb_wifi, 0, 0)
        amenities_layout.addWidget(self.cb_parking, 0, 1)
        amenities_layout.addWidget(self.cb_aircon, 0, 2)
        amenities_layout.addWidget(self.cb_fridge, 0, 3)

        amenities_layout.addWidget(self.cb_wm, 1, 0)
        amenities_layout.addWidget(self.cb_security, 1, 1)
        amenities_layout.addWidget(self.cb_tv, 1, 2)
        amenities_layout.addWidget(self.cb_kitchen, 1, 3)

        amenities_layout.addWidget(self.cb_floor, 2, 0)
        amenities_layout.addWidget(self.cb_hasLoft, 2, 1)
        amenities_layout.addWidget(self.cb_bathroom, 2, 2)
        amenities_layout.addWidget(self.cb_balcony, 2, 3)

        amenities_layout.addWidget(self.cb_funiture, 3, 0)


        scroll_layout.addWidget(amenities_box)

        # THÔNG TIN KHÁC
        other_info_box = QGroupBox("Thông tin bổ sung")
        other_info_box.setProperty("theme", "blue")
        other_info_layout = QVBoxLayout(other_info_box)

        other_label = QLabel("Mô tả thêm:")
        other_label.setObjectName("keyLabel")
        self.input_infor_more = QLineEdit()
        self.input_infor_more.setPlaceholderText("Nhập các thông tin bổ sung khác về phòng")
        self.input_infor_more.setMinimumHeight(60)

        other_info_layout.addWidget(other_label)
        other_info_layout.addWidget(self.input_infor_more)

        scroll_layout.addWidget(other_info_box)

        # BUTTON ACTIONS
        button_layout = QHBoxLayout()

        self.btn_clear = QPushButton("Xóa dữ liệu")
        self.btn_clear.setObjectName("CancelBtn")
        self.btn_clear.setFixedWidth(150)
        self.btn_clear.setFixedHeight(40)
        self.btn_clear.clicked.connect(self.clear_form)

        self.btn_create = QPushButton("Tạo phòng")
        self.btn_create.setFixedWidth(150)
        self.btn_create.setFixedHeight(40)
        self.btn_create.clicked.connect(self.handle_create_room)

        button_layout.addWidget(self.btn_clear)
        button_layout.addSpacing(20)
        button_layout.addWidget(self.btn_create)

        scroll_layout.addLayout(button_layout)
        scroll_layout.addStretch()

        # Thêm separator trước khu vực button để chia tách nội dung
        separator = QFrame()
        separator.setObjectName("separator")
        separator.setFrameShape(QFrame.HLine)
        scroll_layout.addWidget(separator)

        # Thiết lập cuộn
        scroll_area.setWidget(scroll_content)

        # Thêm nội dung vào main
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)

    def clear_form(self):
        # Xóa tất cả dữ liệu trong form
        self.input_name_room.clear()
        self.input_number_people_room.clear()
        self.input_address_room.clear()
        self.input_type_room.setCurrentIndex(0)
        self.input_status_room.setCurrentIndex(0)
        self.input_infor_more.clear()
        self.input_area.clear()
        self.input_price_room.clear()
        self.input_price_electric.clear()
        self.input_price_water.clear()
        self.input_number_electric.clear()
        self.input_number_water.clear()

        # Xóa checkboxes
        for cb in (
                self.cb_wifi, self.cb_parking, self.cb_aircon, self.cb_fridge,
                self.cb_wm, self.cb_security, self.cb_tv, self.cb_kitchen,
                self.cb_floor, self.cb_hasLoft, self.cb_bathroom,
                self.cb_balcony, self.cb_funiture, self.cb_pet
        ):
            cb.setChecked(False)

    def validate_form(self) -> bool:
        # 1. Thu thập dữ liệu từ form vào dict
        data = {
            "room_name":         self.input_name_room.text().strip(),
            "max_tenants":        self.input_number_people_room.text().strip(),
            "address":           self.input_address_room.text().strip(),
            "area":              self.input_area.text().strip(),
            "room_price":        self.input_price_room.text().strip(),
            "electricity_price": self.input_price_electric.text().strip() or "0",
            "water_price":       self.input_price_water.text().strip()   or "0",
            "internet_price":    self.input_price_internet.text().strip() or "0",
            "garbage_price":     self.input_price_garbage.text().strip()  or "0",
            "initial_electric":  self.input_number_electric.text().strip() or "0",
            "initial_water":     self.input_number_water.text().strip()   or "0",
        }

        # 2. Gọi validator tập trung
        is_valid, errors = Validators.validate_room_data(data)  # bạn đã thêm hàm này vào Validators.py

        if not is_valid:
            # Lấy lỗi đầu tiên để hiển thị
            first_field, first_msg = next(iter(errors.items()))

            # Map từ key của data → widget tương ứng
            field_map = {
                "room_name":         self.input_name_room,
                "max_tenants":       self.input_number_people_room,
                "address":           self.input_address_room,
                "area":              self.input_area,
                "rent_price":        self.input_price_room,
                "electricity_price": self.input_price_electric,
                "water_price":       self.input_price_water,
                "internet_price":    self.input_price_internet,
                "garbage_price":     self.input_price_garbage,
                "initial_electric":  self.input_number_electric,
                "initial_water":     self.input_number_water,
            }

            # Hiển thị cảnh báo và focus vào ô có lỗi
            QMessageBox.warning(self, "Lỗi nhập liệu", first_msg)
            field_map[first_field].setFocus()
            return False

        return True

    def collect_amenities(self) -> dict:
        return {
            "free_wifi": int(self.cb_wifi.isChecked()),
            "parking": int(self.cb_parking.isChecked()),
            "air_conditioner": int(self.cb_aircon.isChecked()),
            "fridge": int(self.cb_fridge.isChecked()),
            "washing_machine": int(self.cb_wm.isChecked()),
            "security": int(self.cb_security.isChecked()),
            "television": int(self.cb_tv.isChecked()),
            "kitchen": int(self.cb_kitchen.isChecked()),
            "floor": int(self.cb_floor.isChecked()),
            "has_loft": int(self.cb_hasLoft.isChecked()),
            "bathroom": int(self.cb_bathroom.isChecked()),
            "balcony": int(self.cb_balcony.isChecked()),
            "furniture": int(self.cb_funiture.isChecked()),
            "pet_allowed": int(self.cb_pet.isChecked()),
        }

    def handle_create_room(self):
        # 1. Validate form
        if not self.validate_form():
            return

        # 2. Thu thập flags tiện ích
        amenities = self.collect_amenities()


        # 3. Phần mô tả thuần (Description)
        description = self.input_infor_more.text().strip()

        # 4. Gom payload tương ứng schema Rooms
        create_data = {
            "room_name": self.input_name_room.text().strip(),
            "address": self.input_address_room.text().strip(),
            "type_room": self.input_type_room.currentText(),
            "status": self.input_status_room.currentText(),
            "area": self.input_area.text().strip(),
            "floor": int(self.cb_floor.isChecked()),
            "has_loft": int(self.cb_hasLoft.isChecked()),
            "bathroom": int(self.cb_bathroom.isChecked()),
            "kitchen": int(self.cb_kitchen.isChecked()),
            "furniture": int(self.cb_funiture.isChecked()),
            "balcony": int(self.cb_balcony.isChecked()),
            "free_wifi": int(self.cb_wifi.isChecked()),
            "parking": int(self.cb_parking.isChecked()),
            "air_conditioner": int(self.cb_aircon.isChecked()),
            "fridge": int(self.cb_fridge.isChecked()),
            "washing_machine": int(self.cb_wm.isChecked()),
            "security": int(self.cb_security.isChecked()),
            "television": int(self.cb_tv.isChecked()),
            "pet_allowed": int(self.cb_pet.isChecked()),
            "room_price": self.input_price_room.text().strip(),
            "electricity_price": self.input_price_electric.text().strip() or "0",
            "water_price": self.input_price_water.text().strip() or "0",
            "internet_price": self.input_price_internet.text().strip() or "0",
            "other_fees": 0,  # hoặc từ một input nếu có
            "garbage_service_price": self.input_price_garbage.text().strip() or "0",
            "deposit": "0",  # hoặc từ input
            "current_electricity_num": self.input_number_electric.text().strip() or "0",
            "current_water_num": self.input_number_water.text().strip() or "0",
            "max_tenants": self.input_number_people_room.text().strip(),
            "description": self.input_infor_more.text().strip(),
            "tenant_id": None,
            "id_landlord": self.id_landlord
        }

        print("[DEBUG] Payload tạo phòng:", create_data)

        # 5. Xác nhận
        ans = QMessageBox.question(
            self, "Xác nhận tạo phòng",
            f"Bạn có chắc chắn muốn tạo phòng “{create_data['room_name']}” không?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if ans != QMessageBox.Yes:
            return

        # 6. Gọi Controller → Service → Repository
        ok = RoomMenuController.go_to_handel_data_for_create_room(
            self.id_landlord, create_data
        )

        # 7. Phản hồi kết quả
        if ok:
            QMessageBox.information(
                self, "Thành công",
                "Phòng trọ đã được thêm vào hệ thống!",
                QMessageBox.Ok
            )
            self.clear_form()
        else:
            QMessageBox.critical(
                self, "Lỗi",
                "Không thể tạo phòng mới. Vui lòng thử lại sau.",
                QMessageBox.Ok
            )
