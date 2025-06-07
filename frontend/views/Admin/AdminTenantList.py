from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame

from RentalManagementApplication.frontend.Component.ErrorDialog import ErrorDialog
from RentalManagementApplication.frontend.Component.tableUI import TableUI
from RentalManagementApplication.frontend.Style.GlobalStyle import GlobalStyle



class AdminTenantList(QWidget):
    def __init__(self, main_window, tenant_list=None):
        super().__init__()
        self.setStyleSheet(GlobalStyle.global_stylesheet())
        self.main_window = main_window
        self.tenant_list = tenant_list

        '''[
            {
                "stt": idx,
                "name": t.fullname,
                "cccd": t.cccd,
                "phone": t.phone_number,
                "email": t.email,
                "ngay_thue": t.rent_start_date,  # hoặc chuyển format tại đây
                "username": t.username,
                "created_at": t.created_at,
                "id_tenant": t.tenant_id
                
            }
        ]'''

        main_layout = QVBoxLayout()

        title = QLabel("📋 Danh sách người thuê trọ")
        title.setObjectName("Title")
        #title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        title.setFixedHeight(60)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        frame = QFrame()
        '''
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #dcdcdc;
                padding: 10px;
                box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
            }
        """)
        '''
        headers = ["STT", "Họ tên", "CCCD", "Số điện thoại", "Email", "Ngày bắt đầu thuê", "Xem chi tiết"]
        header_to_key = {
            "STT": "stt",
            "Họ tên": "name",
            "CCCD": "cccd",
            "Số điện thoại": "phone",
            "Email": "email",
            "Ngày bắt đầu thuê": "ngay_thue"
        }

        self.table = TableUI(headers)
        self.table.populate(self.tenant_list, has_button=True, button_callback=self.show_detail,
                            header_to_key=header_to_key)

        main_layout.addWidget(self.table)
        main_layout.addWidget(frame)
        self.setLayout(main_layout)

    def show_detail(self, row):
        try:
            tenant = self.tenant_list[row]
            # Debug: in ra keys của dict xem có 'id_tenant' không
            print("DEBUG: tenant keys =", list(tenant.keys()))
            if 'id_tenant' not in tenant:
                ErrorDialog.show_error( "Không tìm thấy khóa 'id_tenant' trong dữ liệu tenant.", self)
                return

            id_tenant = tenant['id_tenant']
            # Tạo và hiển thị dashboard người thuê trong cửa sổ mới
            from RentalManagementApplication.frontend.views.Tenant.MainWindowTenant import MainWindowTenant
            dashboard = MainWindowTenant(id_tenant)
            dashboard.show()

            # Lưu lại tham chiếu để cửa sổ không bị thu hồi bộ nhớ
            if not hasattr(self, "_opened_windows"):
                self._opened_windows = []
            self._opened_windows.append(dashboard)

        except Exception as e:
            ErrorDialog.show_error(f"Không thể hiển thị chi tiết: {str(e)}", self)
