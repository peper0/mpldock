import logging

from PyQt5 import QtWidgets
from matplotlib.backend_bases import FigureManagerBase, _Backend
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

from mpldock import add_dock, window, run
from mpldock.figure import FigureCanvas, MplFigure


class FigureManagerQTDock(FigureManagerBase):
    def __init__(self, canvas: FigureCanvas, num):
        super().__init__(canvas=canvas, num=num)
        widget = MplFigure(canvas)
        self.name = f"MplFigure__{num}"
        widget.setObjectName(self.name)
        self.window = window()
        add_dock(widget, save_state=MplFigure.dump_state, load_state=MplFigure.load_state)
        self.widget = widget

    def destroy(self, *args):
        # Not sure what should we do here
        self.window.remove_widget(self.name)

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


@_Backend.export
class _BackendQTDock(_Backend):
    required_interactive_framework = "qt5"
    FigureCanvas = FigureCanvasQTAgg
    FigureManager = FigureManagerQTDock

    @staticmethod
    def trigger_manager_draw(manager):
        manager.canvas.draw_idle()

    @staticmethod
    def mainloop():
        run()

