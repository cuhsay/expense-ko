from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from PyQt6.QtWidgets import QVBoxLayout, QWidget


class ChartCanvas(FigureCanvasQTAgg):
    def __init__(self, figsize=(6, 4), dpi=100):
        self.fig = Figure(figsize=figsize, dpi=dpi)
        super().__init__(self.fig)
        self.setStyleSheet("background: transparent;")


class ChartWidget(QWidget):
    def __init__(self, figsize=(6, 4), dpi=100, toolbar=False):
        super().__init__()
        self.canvas = ChartCanvas(figsize, dpi)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        if toolbar:
            layout.addWidget(NavigationToolbar2QT(self.canvas, self))
        self.ax = None

    def clear(self):
        self.canvas.fig.clear()
        self.ax = None
        self.canvas.draw_idle()

    def subplot(self, *args, **kwargs):
        self.ax = self.canvas.fig.add_subplot(*args, **kwargs)
        return self.ax

    def refresh(self):
        self.canvas.fig.tight_layout(pad=2)
        self.canvas.draw_idle()