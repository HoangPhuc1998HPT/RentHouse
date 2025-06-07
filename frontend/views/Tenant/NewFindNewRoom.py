from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QPushButton, QHBoxLayout,
    QFrame, QGridLayout, QMessageBox, QLineEdit, QComboBox, QCheckBox
)
from PyQt5.QtCore import Qt

from RentalManagementApplication.frontend.Style.GlobalStyle import GlobalStyle


class TenantFindNewRoom(QWidget):
    def __init__(self, main_window, advertised_rooms=None):
        super().__init__()
        self.setStyleSheet(GlobalStyle.global_stylesheet())
        self.main_window = main_window
        self.advertised_rooms = advertised_rooms or []
        self.filtered_rooms = self.advertised_rooms.copy()

        # Khởi tạo giao diện
        self.init_ui()

        # Populate dữ liệu ban đầu
        self.populate_rooms()

    def init_ui(self):
        """Khởi tạo giao diện người dùng"""
        # Layout chính
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header với tiêu đề và bộ lọc
        header_widget = self.create_header()
        main_layout.addWidget(header_widget)

        # Scroll area cho danh sách phòng
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #F8FAFC;
            }
            QScrollBar:vertical {
                background-color: #E2E8F0;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #CBD5E1;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #94A3B8;
            }
        """)

        # Container cho danh sách phòng
        self.container = QWidget()
        self.container.setStyleSheet("background-color: #F8FAFC; padding: 20px;")
        scroll.setWidget(self.container)

        # Layout cho container
        self.room_list_layout = QVBoxLayout(self.container)
        self.room_list_layout.setSpacing(20)
        self.room_list_layout.setContentsMargins(20, 20, 20, 20)

        main_layout.addWidget(scroll)

    def create_header(self):
        """Tạo header với tiêu đề và bộ lọc"""
        header_frame = QFrame()
        header_frame.setFixedHeight(200)
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #667EEA, stop:1 #764BA2);
                border-radius: 0px;
                margin-bottom: 10px;
            }
        """)

        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(30, 20, 30, 20)
        header_layout.setSpacing(15)

        # Tiêu đề
        title = QLabel("🏠 Tìm Phòng Trọ Ưng Ý")
        title.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: white;
                background: transparent;
            }
        """)
        title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Khám phá các phòng trọ chất lượng với giá cả hợp lý")
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: rgba(255, 255, 255, 0.9);
                background: transparent;
            }
        """)
        subtitle.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(subtitle)

        # Bộ lọc
        filter_layout = self.create_filter_section()
        header_layout.addLayout(filter_layout)

        return header_frame

    def create_filter_section(self):
        """Tạo section bộ lọc"""
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(15)

        # Search box
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Tìm kiếm theo địa chỉ, mô tả...")
        self.search_input.setFixedHeight(40)
        self.search_input.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
                padding: 10px 15px;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 20px;
                background-color: rgba(255, 255, 255, 0.9);
                color: #2D3748;
            }
            QLineEdit:focus {
                border-color: #4299E1;
                background-color: white;
            }
        """)
        self.search_input.textChanged.connect(self.filter_rooms)

        # Price filter
        self.price_filter = QComboBox()
        self.price_filter.addItems([
            "💰 Tất cả mức giá",
            "Dưới 2 triệu",
            "2-3 triệu",
            "3-5 triệu",
            "Trên 5 triệu"
        ])
        self.price_filter.setFixedHeight(40)
        self.price_filter.setStyleSheet("""
            QComboBox {
                font-size: 14px;
                padding: 8px 15px;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 20px;
                background-color: rgba(255, 255, 255, 0.9);
                color: #2D3748;
                min-width: 150px;
            }
            QComboBox:hover {
                border-color: #4299E1;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                selection-background-color: #EBF8FF;
            }
        """)
        self.price_filter.currentTextChanged.connect(self.filter_rooms)

        # Preference filters
        self.student_filter = QCheckBox("🎓 Ưu tiên sinh viên")
        self.female_filter = QCheckBox("👩 Ưu tiên nữ")
        self.shared_filter = QCheckBox("👥 Cho phép ở ghép")

        for checkbox in [self.student_filter, self.female_filter, self.shared_filter]:
            checkbox.setStyleSheet("""
                QCheckBox {
                    font-size: 13px;
                    color: rgba(255, 255, 255, 0.95);
                    background: transparent;
                    padding: 5px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    border: 2px solid rgba(255, 255, 255, 0.6);
                    border-radius: 4px;
                    background-color: rgba(255, 255, 255, 0.1);
                }
                QCheckBox::indicator:checked {
                    background-color: #4299E1;
                    border-color: #4299E1;
                }
            """)
            checkbox.stateChanged.connect(self.filter_rooms)

        # Layout arrangement
        filter_layout.addWidget(self.search_input, 2)
        filter_layout.addWidget(self.price_filter, 1)
        filter_layout.addWidget(self.student_filter)
        filter_layout.addWidget(self.female_filter)
        filter_layout.addWidget(self.shared_filter)

        return filter_layout

    def populate_rooms(self):
        """Hiển thị danh sách phòng"""
        # Clear existing widgets
        self.clear_room_list()

        if not self.filtered_rooms:
            self.show_no_rooms_message()
            return

        # Statistics
        stats_widget = self.create_statistics_widget()
        self.room_list_layout.addWidget(stats_widget)

        # Room cards in grid
        self.create_room_grid()

    def clear_room_list(self):
        """Xóa tất cả widget trong danh sách phòng"""
        while self.room_list_layout.count():
            item = self.room_list_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def create_statistics_widget(self):
        """Tạo widget thống kê"""
        stats_frame = QFrame()
        stats_frame.setFixedHeight(80)
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #E2E8F0;
                margin-bottom: 10px;
            }
        """)

        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(25, 15, 25, 15)

        # Total rooms
        total_label = QLabel(f"📊 Tổng cộng: {len(self.filtered_rooms)} phòng")
        total_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2D3748;
            }
        """)

        # Available rooms (assuming all are available)
        available_label = QLabel(f"✅ Có sẵn: {len(self.filtered_rooms)} phòng")
        available_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #38A169;
            }
        """)

        # Average price (mock calculation)
        avg_price_label = QLabel("💰 Giá TB: 3.2 triệu/tháng")
        avg_price_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #4299E1;
            }
        """)

        stats_layout.addWidget(total_label)
        stats_layout.addStretch()
        stats_layout.addWidget(available_label)
        stats_layout.addStretch()
        stats_layout.addWidget(avg_price_label)

        return stats_frame

    def create_room_grid(self):
        """Tạo lưới hiển thị các phòng"""
        # Create grid container
        grid_container = QWidget()
        grid_layout = QGridLayout(grid_container)
        grid_layout.setSpacing(20)
        grid_layout.setContentsMargins(0, 0, 0, 0)

        # Add room cards to grid (2 columns)
        for i, room in enumerate(self.filtered_rooms):
            row = i // 2
            col = i % 2

            room_card = self.create_enhanced_room_card(room, i + 1)
            grid_layout.addWidget(room_card, row, col)

        self.room_list_layout.addWidget(grid_container)

    def create_enhanced_room_card(self, room, stt):
        """Tạo card phòng với thiết kế nâng cao"""
        card = QFrame()
        card.setFixedHeight(320)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 20px;
                border: 1px solid #E2E8F0;
                padding: 0px;
            }
            QFrame:hover {
                border: 2px solid #4299E1;
                box-shadow: 0px 8px 25px rgba(66, 153, 225, 0.15);
            }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        # Image section
        image_section = self.create_image_section(room)
        card_layout.addWidget(image_section)

        # Content section
        content_section = self.create_content_section(room, stt)
        card_layout.addWidget(content_section)

        return card

    def create_image_section(self, room):
        """Tạo section hình ảnh"""
        image_frame = QFrame()
        image_frame.setFixedHeight(140)
        image_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #FF8A80, stop:1 #FFB74D);
                border-top-left-radius: 20px;
                border-top-right-radius: 20px;
                border-bottom: none;
            }
        """)

        image_layout = QVBoxLayout(image_frame)
        image_layout.setAlignment(Qt.AlignCenter)

        # Placeholder for actual image
        image_label = QLabel("🏠")
        image_label.setStyleSheet("""
            QLabel {
                font-size: 48px;
                color: white;
                background: transparent;
            }
        """)
        image_label.setAlignment(Qt.AlignCenter)

        # Room number badge
        room_number = QLabel(f"#{room.get('room_name', 'N/A')}")
        room_number.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 0.9);
                color: #2D3748;
                font-size: 12px;
                font-weight: bold;
                padding: 4px 8px;
                border-radius: 12px;
            }
        """)

        image_layout.addWidget(image_label)
        image_layout.addWidget(room_number, alignment=Qt.AlignCenter)

        return image_frame

    def create_content_section(self, room, stt):
        """Tạo section nội dung"""
        content_frame = QFrame()
        content_frame.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 15, 20, 20)
        content_layout.setSpacing(12)

        # Title and price row
        title_row = QHBoxLayout()

        room_title = QLabel(f"{room.get('room_name', 'Phòng không tên')}")
        room_title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2D3748;
            }
        """)

        price_label = QLabel(f"{room.get('price', 'Liên hệ')}")
        price_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #E53E3E;
                background-color: #FED7D7;
                padding: 4px 8px;
                border-radius: 8px;
            }
        """)

        title_row.addWidget(room_title)
        title_row.addStretch()
        title_row.addWidget(price_label)
        content_layout.addLayout(title_row)

        # Address
        address = QLabel(f"📍 {room.get('address', 'Chưa cập nhật')[:50]}...")
        address.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #718096;
            }
        """)
        content_layout.addWidget(address)

        # Description
        description = room.get('description', 'Chưa có mô tả')
        if len(description) > 80:
            description = description[:80] + "..."

        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #4A5568;
                line-height: 1.4;
            }
        """)
        desc_label.setWordWrap(True)
        content_layout.addWidget(desc_label)

        # Tags (preferences)
        tags_layout = self.create_tags_layout(room.get('preferences', []))
        content_layout.addLayout(tags_layout)

        # Action buttons
        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)

        contact_btn = QPushButton("📞 Liên hệ")
        contact_btn.setFixedHeight(35)
        contact_btn.setStyleSheet("""
            QPushButton {
                background-color: #48BB78;
                color: white;
                font-size: 12px;
                font-weight: bold;
                border-radius: 17px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #38A169;
            }
        """)

        detail_btn = QPushButton("📋 Chi tiết")
        detail_btn.setFixedHeight(35)
        detail_btn.setStyleSheet("""
            QPushButton {
                background-color: #4299E1;
                color: white;
                font-size: 12px;
                font-weight: bold;
                border-radius: 17px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #3182CE;
            }
        """)
        detail_btn.clicked.connect(lambda: self.view_room_details(room))

        action_layout.addWidget(contact_btn)
        action_layout.addWidget(detail_btn)
        content_layout.addLayout(action_layout)

        return content_frame

    def create_tags_layout(self, preferences):
        """Tạo layout cho các tag preferences"""
        tags_layout = QHBoxLayout()
        tags_layout.setSpacing(5)

        # Limit to 3 tags
        display_prefs = preferences[:3] if len(preferences) > 3 else preferences

        for pref in display_prefs:
            tag = QLabel(pref)
            tag.setStyleSheet("""
                QLabel {
                    background-color: #EDF2F7;
                    color: #4A5568;
                    font-size: 10px;
                    padding: 3px 8px;
                    border-radius: 10px;
                    font-weight: 500;
                }
            """)
            tags_layout.addWidget(tag)

        if len(preferences) > 3:
            more_tag = QLabel(f"+{len(preferences) - 3}")
            more_tag.setStyleSheet("""
                QLabel {
                    background-color: #CBD5E0;
                    color: #2D3748;
                    font-size: 10px;
                    padding: 3px 8px;
                    border-radius: 10px;
                    font-weight: bold;
                }
            """)
            tags_layout.addWidget(more_tag)

        tags_layout.addStretch()
        return tags_layout

    def show_no_rooms_message(self):
        """Hiển thị thông báo khi không có phòng"""
        no_rooms_frame = QFrame()
        no_rooms_frame.setFixedHeight(300)
        no_rooms_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 20px;
                border: 2px dashed #CBD5E0;
            }
        """)

        layout = QVBoxLayout(no_rooms_frame)
        layout.setAlignment(Qt.AlignCenter)

        icon_label = QLabel("🏠")
        icon_label.setStyleSheet("""
            QLabel {
                font-size: 64px;
                color: #CBD5E0;
            }
        """)
        icon_label.setAlignment(Qt.AlignCenter)

        message_label = QLabel("Không tìm thấy phòng phù hợp")
        message_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #718096;
                font-weight: bold;
            }
        """)
        message_label.setAlignment(Qt.AlignCenter)

        subtitle_label = QLabel("Hãy thử điều chỉnh bộ lọc tìm kiếm")
        subtitle_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #A0AEC0;
            }
        """)
        subtitle_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(icon_label)
        layout.addWidget(message_label)
        layout.addWidget(subtitle_label)

        self.room_list_layout.addWidget(no_rooms_frame)

    def filter_rooms(self):
        """Lọc danh sách phòng theo các tiêu chí"""
        search_text = self.search_input.text().lower()
        price_filter = self.price_filter.currentText()

        self.filtered_rooms = []

        for room in self.advertised_rooms:
            # Search filter
            if search_text:
                searchable_text = f"{room.get('address', '')} {room.get('description', '')}".lower()
                if search_text not in searchable_text:
                    continue

            # Convert price string to int (mock parsing)
            price_str = room.get("price", "0").replace(".", "").replace(" VNĐ", "")
            try:
                price_value = int(price_str)
            except:
                price_value = 0

            # Kiểm tra khoảng giá
            if price_filter == "Dưới 2 triệu" and price_value >= 2000000:
                continue
            elif price_filter == "2-3 triệu" and not (2000000 <= price_value <= 3000000):
                continue
            elif price_filter == "3-5 triệu" and not (3000000 < price_value <= 5000000):
                continue
            elif price_filter == "Trên 5 triệu" and price_value <= 5000000:
                continue
            # Preference filters
            preferences = room.get('preferences', [])
            if self.student_filter.isChecked() and "Sinh viên" not in preferences:
                continue
            if self.female_filter.isChecked() and "Nữ" not in preferences:
                continue
            if self.shared_filter.isChecked() and "Ở ghép" not in preferences:
                continue

            self.filtered_rooms.append(room)

        # Refresh display
        self.populate_rooms()

    def view_room_details(self, room):
        """Xem chi tiết phòng"""
        room_id = room.get('id')
        if room_id:
            try:
                print(f"[DEBUG] Đang mở chi tiết phòng với ID: {room_id}")
                from RentalManagementApplication.controller.RoomController.RoomMenuController import \
                    RoomMenuController
                controller = RoomMenuController()
                controller.open_room_detail_popup_for_tenant(room_id)
            except Exception as e:
                import traceback
                traceback.print_exc()
                QMessageBox.critical(self, "Lỗi", f"Không thể hiển thị thông tin phòng: {str(e)}")
        else:
            QMessageBox.warning(self, "Thông báo", "Không tìm thấy thông tin phòng!")

    def refresh_data(self, new_rooms_data):
        """Làm mới dữ liệu phòng"""
        self.advertised_rooms = new_rooms_data or []
        self.filtered_rooms = self.advertised_rooms.copy()
        self.populate_rooms()

if __name__ == '__main__':
    # Write a simple test to run the widget
    import sys
    from PyQt5.QtWidgets import QApplication, QMainWindow
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    main_window.setWindowTitle("Tìm Phòng Trọ")
    main_window.setGeometry(100, 100, 800, 600)
    tenant_find_new_room = TenantFindNewRoom(main_window, advertised_rooms=[
        {'id': 1, 'room_name': 'Phòng A1', 'price': '2 triệu', 'address': '123 Đường ABC',
         'description': 'Phòng rộng rãi, thoáng mát, gần trường học.',
         'preferences': ['Sinh viên', 'Nữ']},
        {'id': 2, 'room_name': 'Phòng B2', 'price': '3 triệu', 'address': '456 Đường DEF',
         'description': 'Phòng sạch sẽ, đầy đủ tiện nghi.',
         'preferences': ['Ở ghép']},
        # Add more mock rooms as needed
    ])
    main_window.setCentralWidget(tenant_find_new_room)
    main_window.show()
    sys.exit(app.exec_())
