from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QWidget, QVBoxLayout, QPushButton, QLabel

from QLNHATRO.RentalManagementApplication.controller.AdminController.AdminController import AdminController
from QLNHATRO.RentalManagementApplication.frontend.Component.ButtonUI import ButtonUI
from QLNHATRO.RentalManagementApplication.frontend.Style.GlobalStyle import GlobalStyle

#TODO: cần hiệu chỉnh màu nền

class AdminMenu(QWidget):
    def __init__(self, main_window=None, user_id=None):
        super().__init__()
        print("[DEBUG] AdminMenu khởi tạo")

        self.main_window = main_window
        self.current_page = None
        self.user_id = user_id

        self.main_window.setWindowTitle("Dashboard Admin")
        self.main_window.setGeometry(300, 100, 1000, 600)

        self.main_window.setStyleSheet(GlobalStyle.global_stylesheet() + """
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #8E2DE2, stop:1 #4A00E0);
                border-radius: 15px;
            }
        """)

        self.main_layout = QHBoxLayout()

        # ------------ LEFT MENU FRAME ------------
        self.left_frame = QWidget()
        self.left_frame.setFixedWidth(250)
        self.left_frame.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #8E2DE2, stop:1 #4A00E0);
                border-radius: 15px;
            }
        """)

        left_layout = QVBoxLayout(self.left_frame)
        left_layout.setAlignment(Qt.AlignTop)

        # Tạo các nút với style
        button_ui = ButtonUI.tenant_dashboard_button()

        self.home_btn = QPushButton("🏠 Home")
        button_ui.apply_style(self.home_btn)
        self.home_btn.clicked.connect(lambda: AdminController.go_to_home(self))

        self.user_btn = QPushButton("👥 Quản lý User")
        button_ui.apply_style(self.user_btn)
        self.user_btn.clicked.connect(lambda: AdminController.go_to_user_management(self))

        self.landlord_btn = QPushButton("📋 Danh Sách chủ trọ")
        button_ui.apply_style(self.landlord_btn)
        self.landlord_btn.clicked.connect(lambda: AdminController.go_to_landlord_list(self))

        self.tenant_btn = QPushButton("📋 Danh sách người thuê trọ")
        button_ui.apply_style(self.tenant_btn)
        self.tenant_btn.clicked.connect(lambda: AdminController.go_to_tenant_list(self))

        self.room_btn = QPushButton("🚪 Danh sách phòng trọ")
        button_ui.apply_style(self.room_btn)
        self.room_btn.clicked.connect(lambda: AdminController.go_to_room_list(self))

        self.invoice_btn = QPushButton("🧾 Danh sách hóa đơn")
        button_ui.apply_style(self.invoice_btn)
        self.invoice_btn.clicked.connect(lambda: AdminController.go_to_invoice_list(self))

        self.logout_btn = QPushButton("🚪 Đăng xuất")
        button_ui.apply_style(self.logout_btn)
        self.logout_btn.clicked.connect(lambda: AdminController.handle_logout(self))

        self.exit_btn = QPushButton("❌ Thoát")
        button_ui.apply_style(self.exit_btn)
        self.exit_btn.clicked.connect(lambda: AdminController.handle_exit(self))

        # Thêm nút vào layout
        left_layout.addWidget(self.home_btn)
        left_layout.addWidget(self.user_btn)
        left_layout.addWidget(self.landlord_btn)
        left_layout.addWidget(self.tenant_btn)
        left_layout.addWidget(self.room_btn)
        left_layout.addWidget(self.invoice_btn)
        left_layout.addWidget(self.logout_btn)
        left_layout.addWidget(self.exit_btn)

        # ----------- RIGHT FRAME -----------
        self.right_frame = QWidget()
        self.right_layout = QVBoxLayout(self.right_frame)
        self.right_layout.setContentsMargins(0, 0, 0, 0)

        # Giao diện mặc định là Home
        #AdminController.go_to_home(self)

        from QLNHATRO.RentalManagementApplication.frontend.views.Admin.AdminHomePage import AdminHome
        from QLNHATRO.RentalManagementApplication.services.AdminService import AdminService

        summary_data = AdminService.get_summary_dashboard_data()
        self.set_right_frame(lambda: AdminHome(self.main_window, summary_data))

        self.main_layout.addWidget(self.left_frame)
        self.main_layout.addWidget(self.right_frame)
        self.setLayout(self.main_layout)

    def set_right_frame(self, PageClass):
        if self.current_page:
            self.right_layout.removeWidget(self.current_page)
            self.current_page.setParent(None)

        try:
            if callable(PageClass):
                self.current_page = PageClass()
            else:
                self.current_page = PageClass(self.main_window)
        except TypeError as e:
            print(f"[⚠️ Cảnh báo] {PageClass.__name__} không nhận 1 tham số: {e}")
            self.current_page = PageClass()

        self.right_layout.addWidget(self.current_page)
        return self.current_page
