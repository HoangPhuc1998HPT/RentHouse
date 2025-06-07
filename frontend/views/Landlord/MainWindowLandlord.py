from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from pydot import id_re_alpha_nums

from QLNHATRO.RentalManagementApplication.Repository.LandlordRepository import LanlordRepository
from QLNHATRO.RentalManagementApplication.frontend.Style.GlobalStyle import GlobalStyle
from QLNHATRO.RentalManagementApplication.frontend.views.Landlord.LandlordMenu import LandlordMenu


class MainWindowLandlord(QMainWindow):
    print("mở MainWindowLandLord")

    def __init__(self, main_window, user_id):
        super().__init__()
        self.setStyleSheet(GlobalStyle.global_stylesheet())


        self.main_window = main_window
        self.user_id = user_id
        self.id_lanlord = LanlordRepository.get_id_landlord_from_user_id(user_id)

        # Setup UI
        self.setWindowTitle("Dashboard Chủ trọ")
        self.setGeometry(300, 100, 1000, 600)
        #self.setStyleSheet("""
            #background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #FF6B6B, stop:1 #FFA07A);
            #border-radius: 15px;
        #""")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        self.landlord_menu = LandlordMenu(main_window=self,id_lanlord=self.id_lanlord)
        layout.addWidget(self.landlord_menu)

    def close_window_menu(self):
        self.main_window.close()