"""Main application window."""
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .chart_widget import ChartWidget


class MainWindow(QMainWindow):
    """Window combining chart area and a control panel."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Fynix")

        central = QWidget()
        layout = QHBoxLayout(central)
        self.setCentralWidget(central)

        self.chart = ChartWidget(self)
        layout.addWidget(self.chart, 1)

        self.control_panel = QWidget()
        control_layout = QVBoxLayout(self.control_panel)
        control_layout.addWidget(QLabel("Controls"))
        control_layout.addStretch()
        control_layout.addWidget(QPushButton("Load Data"))
        layout.addWidget(self.control_panel)
