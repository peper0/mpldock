import logging

from matplotlib.backend_bases import FigureManagerBase
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from mpldock import add_dock, window
from mpldock.figure import MplFigure


class FigureManagerQTDock(FigureManagerBase):
    def __init__(self, canvas: FigureCanvasQTAgg, num):
        self.widget = MplFigure(canvas)
        self.name = f"MplFigure__{num}"
        self.widget.setObjectName(self.name)
        self.window = window()
        super().__init__(canvas=canvas, num=num)
        add_dock(self.widget, dump_state=self.widget.dump_state, restore_state=self.widget.restore_state)

    def destroy(self, *args):
        # Not sure what should we do here
        pass

    def get_window_title(self):
        return self.widget.windowTitle()

    def set_window_title(self, title):
        self.widget.setWindowTitle(title)

    def resize(self, width, height):
        logging.warning("cannot resize qtdock")

    def show(self):
        self.window.show()
        self.window.activateWindow()
        self.window.raise_()


# This class is an entry point to the backend. It's methods are called by matplotlib if the current module is used as a backend.
class FigureCanvas(FigureCanvasQTAgg):
    required_interactive_framework = "qt5"
    FigureCanvas = FigureCanvasQTAgg
    FigureManager = FigureManagerQTDock

    def __init__(self, figure: Figure):
        super().__init__(figure)
        self.figure = figure

    @classmethod
    def new_manager(cls, figure, num):
        canvas = FigureCanvas(figure)
        manager = FigureManagerQTDock(canvas, num)
        canvas.manager = manager
        figure.canvas = canvas
        return manager
