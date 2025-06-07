from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QWidget, QVBoxLayout, QPushButton, QLabel

from RentalManagementApplication.controller.LandlordController.LandlordController import LandlordController
from RentalManagementApplication.controller.MaintenanceController.MaintenanceController import \
    MaintenanceController

from RentalManagementApplication.frontend.Component.ButtonUI import ButtonUI
from RentalManagementApplication.frontend.Style.GlobalStyle import GlobalStyle





class LandlordMenu(QWidget):
    def __init__(self, main_window=None,id_lanlord=None):
        super().__init__()
        self.setStyleSheet(GlobalStyle.global_stylesheet())
        print("[DEBUG] LandlordMenu khởi tạo","với id_lanlord:", id_lanlord)

        self.main_window = main_window
        self.current_page = None
        self.id_lanlord = id_lanlord

        self.main_window.setWindowTitle("Dashboard Chủ trọ")
        #self.main_window.setGeometry(300, 100, 1000, 600)
        self.main_window.resize(GlobalStyle.WINDOW_WIDTH, GlobalStyle.WINDOW_HEIGHT)
        self.main_window.setMinimumSize(GlobalStyle.WINDOW_WIDTH, GlobalStyle.WINDOW_HEIGHT)
        self.main_window.setMaximumSize(GlobalStyle.WINDOW_WIDTH, GlobalStyle.WINDOW_HEIGHT)

        self.main_layout = QHBoxLayout()

        # ------------ LEFT MENU FRAME ------------
        self.left_frame = QWidget()
        self.left_frame.setFixedWidth(250)
        self.left_frame.setStyleSheet("""
            background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #FF6B6B, stop:1 #FFA07A);
            border-radius: 15px;
        """)

        left_layout = QVBoxLayout(self.left_frame)
        left_layout.setAlignment(Qt.AlignTop)

        # Label chào mừng
        self.label_landlord = QLabel("👋 Chào mừng đến với DASHBOARD Chủ trọ: Nguyễn Văn A")
        self.label_landlord.setObjectName("Title")

        # Tạo nút và áp dụng style
        button_ui = ButtonUI.landlord_dashboard_button()

        self.home_btn = QPushButton("🏠 Trang chính")
        button_ui.apply_style(self.home_btn)
        self.home_btn.clicked.connect(lambda : LandlordController.go_to_home_page(self, self.id_lanlord))

        self.info_btn = QPushButton("👤 Thông tin chủ trọ") # OK
        button_ui.apply_style(self.info_btn)
        self.info_btn.clicked.connect(lambda : LandlordController.go_to_info_page(self, self.id_lanlord))

        self.infor_list_room_btn = QPushButton("📂 Danh sách phòng trọ") # OK
        button_ui.apply_style(self.infor_list_room_btn)
        self.infor_list_room_btn.clicked.connect(lambda : LandlordController.go_to_room_list(self, self.id_lanlord))

        self.create_new_room_btn = QPushButton("➕ Tạo phòng trọ mới") #OK
        button_ui.apply_style(self.create_new_room_btn)
        self.create_new_room_btn.clicked.connect(lambda : LandlordController.go_to_create_new_room(self, self.id_lanlord))

        self.add_list_maintenance_btn = QPushButton("🛠️ Danh sách bảo trì") # Tạm OK
        button_ui.apply_style(self.add_list_maintenance_btn)
        self.add_list_maintenance_btn.clicked.connect( lambda: MaintenanceController.go_to_maintenance_list(self, self.id_lanlord))

        self.infor_list_invoice_btn = QPushButton("🧾 Danh sách hóa đơn")
        button_ui.apply_style(self.infor_list_invoice_btn)
        self.infor_list_invoice_btn.clicked.connect(lambda : LandlordController.go_to_invoice_list(self,self.id_lanlord))

        self.add_adv_find_tenant_btn = QPushButton("🔍 Tìm người thuê mới")
        button_ui.apply_style(self.add_adv_find_tenant_btn)
        self.add_adv_find_tenant_btn.clicked.connect(lambda: LandlordController.go_to_LanlordFindNewTenant(self,self.id_lanlord))



        self.logout_btn = QPushButton("🚪 Đăng xuất")
        button_ui.apply_style(self.logout_btn)
        self.logout_btn.clicked.connect(lambda: LandlordController.handle_logout(self))

        self.exist_btn = QPushButton("❌ Thoát")
        button_ui.apply_style(self.exist_btn)
        self.exist_btn.clicked.connect(lambda: self.close_window_menu())

        # Thêm tất cả các button vào layout
        left_layout.addWidget(self.home_btn)
        left_layout.addWidget(self.info_btn)
        left_layout.addWidget(self.infor_list_room_btn)
        left_layout.addWidget(self.create_new_room_btn)
        left_layout.addWidget(self.add_list_maintenance_btn)
        left_layout.addWidget(self.infor_list_invoice_btn)
        left_layout.addWidget(self.add_adv_find_tenant_btn)
        left_layout.addWidget(self.logout_btn)
        left_layout.addWidget(self.exist_btn)

        # ----------- RIGHT FRAME (QStackedWidget) -----------
        self.right_frame = QWidget()
        self.right_layout = QVBoxLayout(self.right_frame)
        self.right_layout.setContentsMargins(0, 0, 0, 0)

        # Trang mặc định hiển thị Home page
        #self.home_page = LandlordHome(self.main_window)
        #self.set_right_frame(LandlordHome)
        #self.right_layout.addWidget(self.set_right_frame(LandlordHome))  # page

        # Thêm vào layout chính
        self.main_layout.addWidget(self.left_frame)
        self.main_layout.addWidget(self.right_frame)

        # Initialize with home page
        # self.set_right_frame(LandlordHome)
        # Sửa dòng này:
        # self.set_right_frame(lambda : LandlordController.go_to_home_page(...))

        # Thành:
        LandlordController.go_to_home_page(self, self.id_lanlord)

        self.setLayout(self.main_layout)

    def set_right_frame(self, PageClass):
        if self.current_page:
            self.right_layout.removeWidget(self.current_page)
            self.current_page.setParent(None)

        try:
            if callable(PageClass):  # lambda trả về instance
                self.current_page = PageClass()
            else:
                self.current_page = PageClass(self.main_window, self.id_lanlord)
        except TypeError as e:
            print(f"[⚠️ Cảnh báo] {PageClass.__name__} không nhận 2 tham số: {e}")
            self.current_page = PageClass(self.main_window)

        self.right_layout.addWidget(self.current_page)
        return self.current_page



    def close_window_menu(self):
        self.main_window.close()