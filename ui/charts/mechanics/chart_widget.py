"""
chart_widget.py
---------------
Handles chart rendering inside a PyQt6 widget using PyQtGraph.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg
from pyqtgraph import PlotWidget

from .candlestick_chart import CandlestickChart

class ChartWidget(QWidget):
    
    """Widget that renders all chart layers using PyQtGraph."""

    def __init__(self):
        
        super().__init__()

        # --- Layout ---
        layout = QVBoxLayout(self)
        self.plot_widget = PlotWidget()
        layout.addWidget(self.plot_widget)

        # --- Chart setup ---
        self.plot_item = self.plot_widget.getPlotItem()
        self.plot_item.showGrid(x=True, y=True, alpha=0.3)
        self.plot_item.setLabel('bottom', 'Date')
        self.plot_item.setLabel('left', 'Price')
        self.plot_widget.setBackground('k')

        # --- State ---
        self.current_chart_type = "candlestick"
        self.additional_layers = []  # indicators, overlays, etc.

    def set_chart_type(self, chart_type: str):
        
        self.current_chart_type = chart_type.lower()

    def clear_chart(self):
        
        self.plot_item.clear()

    def update_chart(self, data):
        
        if data.empty:
            return

        self.clear_chart()

        # Add the main price layer
        if self.current_chart_type == "candlestick":
            CandlestickChart(data).add_trace(self.plot_item)
        elif self.current_chart_type == "line":
            LineChart(data).add_trace(self.plot_item)

        # Add overlays (indicators, signals)
        for overlay in self.additional_layers:
            overlay.add_trace(self.plot_item)

        # Optional: auto-range view
        self.plot_item.enableAutoRange()