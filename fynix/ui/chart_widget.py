"""Chart widget displaying OHLC candles."""
from typing import Iterable, Tuple

from PyQt5.QtChart import QChart, QChartView, QCandlestickSeries, QCandlestickSet
from PyQt5.QtGui import QPainter

OHLC = Tuple[float, float, float, float, float]  # (timestamp, open, high, low, close)


class ChartWidget(QChartView):
    """Widget that renders OHLC candles using QtCharts."""

    def __init__(self, parent=None) -> None:
        chart = QChart()
        super().__init__(chart, parent)
        self.setRenderHint(QPainter.Antialiasing)

        self._series = QCandlestickSeries()
        chart.addSeries(self._series)
        chart.createDefaultAxes()
        chart.legend().hide()

    def load_data(self, data: Iterable[OHLC]) -> None:
        """Load OHLC tuples into the chart.

        Each tuple should contain: (timestamp, open, high, low, close).
        """
        self._series.clear()
        for timestamp, opn, high, low, close in data:
            candle = QCandlestickSet(opn, high, low, close, timestamp)
            self._series.append(candle)
