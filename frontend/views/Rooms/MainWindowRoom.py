from PyQt5.QtWidgets import QMainWindow

from RentalManagementApplication.frontend.Style.GlobalStyle import GlobalStyle
from RentalManagementApplication.frontend.views.Rooms.RoomMenu import RoomMenu


class MainWindowRoom(QMainWindow):
    def __init__(self, room_id):
        super().__init__()
        self.setStyleSheet(GlobalStyle.global_stylesheet())
        self.setWindowTitle("Dashboard Chủ trọ")
        self.setGeometry(300, 100, 860, 600)

        # Giao diện chính được xử lý hoàn toàn bên trong RoomMenu
        self.setCentralWidget(RoomMenu(self, room_id))

    def close_window_menu(self):
        self.main_window.close()

