"""
candlestick_chart.py
--------------------
Candlestick chart using Plotly inside a PyQt6 QWebEngineView.
"""

import tempfile
import plotly.graph_objects as go
from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView


class CandlestickChart(QWebEngineView):

    def __init__(self, data=None, parent=None):

        super().__init__(parent)
        self.data = data

    def add_trace(self, plot_item=None):

        if self.data is None or self.data.empty:
            return
        self._render_chart()

    def _render_chart(self):
        # Build Plotly candlestick figure
        fig = go.Figure(data=[go.Candlestick(
            x=self.data.index,
            open=self.data['open'],
            high=self.data['high'],
            low=self.data['low'],
            close=self.data['close'],
            increasing_line_color="#00ff99",
            decreasing_line_color="#ff3366"
        )])

        fig.update_layout(
            template="plotly_dark",
            xaxis_rangeslider_visible=False,
            dragmode="drawopenpath",
            margin=dict(l=10, r=10, t=25, b=25),
            height=700,
        )

        # Save to temporary HTML and load into QWebEngineView
        html_file = tempfile.NamedTemporaryFile(suffix=".html", delete=False)
        fig.write_html(html_file.name)
        self.load(QUrl.fromLocalFile(html_file.name))