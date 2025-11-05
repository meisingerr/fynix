from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QStatusBar,
    QMenuBar,
    QTabWidget,
)
from PyQt6.QtGui import QAction
from core.data_manager import DataManager
from .charts.mechanics.chart_widget import ChartWidget

class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Fynix")
        self.setGeometry(200, 100, 1200, 800)

        # --- Menu bar ---
        self._create_menu_bar()

        # --- Main widget ---
        self._create_tabs()

        # --- Status bar ---
        status = QStatusBar()
        status.showMessage("Ready")
        self.setStatusBar(status)

    def _create_menu_bar(self):

        menu_bar = QMenuBar()
        self.setMenuBar(menu_bar)

        # File menu
        file_menu = menu_bar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menu_bar.addMenu("View")

        # Help menu
        help_menu = menu_bar.addMenu("Help")
        about_action = QAction("About Fynix", self)
        about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(about_action)

    def _create_tabs(self):

        self.tabs = QTabWidget()

        # --- Price Action Tab ---
        price_tab = ChartWidget()
        self.tabs.addTab(price_tab, "Price Action")

        try:
            interval = "1d"
            data_manager = DataManager()
            data_manager.update_historical_data("BTCUSDT", interval=interval)
            df = data_manager.get_crypto_data("BTCUSDT", period="5y", interval=interval)
            if not df.empty:
                price_tab.update_chart(df)
        except Exception as e:
            print(f"[ERROR] Failed to load chart data: {e}")

        # --- Strategies Tab ---
        strategies_tab = QWidget()
        strategies_layout = QVBoxLayout()
        strategies_tab.setLayout(strategies_layout)
        strategies_layout.addWidget(QLabel("Strategies — empty"))
        self.tabs.addTab(strategies_tab, "Strategies")

        self.setCentralWidget(self.tabs)

    # --- About dialog ---
    def _show_about_dialog(self):

        from PyQt6.QtWidgets import QMessageBox

        QMessageBox.information(
            self,
            "About Fynix",
            "Fynix\n\nBuilt with Python + PyQt6.\n",
        )