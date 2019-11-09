import logging
from math import exp, log

from PyQt5 import QtGui
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from matplotlib.axis import Axis
from matplotlib.backend_bases import MouseEvent, key_press_handler
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar

FigureCanvas = FigureCanvasQTAgg

MODIFIER_KEYS = set(['shift', 'control', 'alt'])


class MplFigure(QWidget):
    def __init__(self, canvas: FigureCanvasQTAgg):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.canvas = canvas
        self.canvas.setParent(self)
        self.canvas.setFocusPolicy(Qt.StrongFocus)
        self.canvas.setFocus()
        self.layout.addWidget(self.canvas)

        self.figure = canvas.figure

        self.mpl_toolbar = NavigationToolbar(self.canvas, self)
        self.layout.addWidget(self.mpl_toolbar)

        def sizeHint():
            size = super(NavigationToolbar, self.mpl_toolbar).sizeHint()
            return size

        self.mpl_toolbar.sizeHint = sizeHint
        self.mpl_toolbar.layout().setContentsMargins(0, 0, 0, 0)
        self.mpl_toolbar.setIconSize(QSize(16, 16))
        self.mpl_toolbar.layout().setSpacing(2)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # self.mpl_toolbar.setHeight(20)
        self.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.canvas.mpl_connect('key_release_event', self.on_key_release)
        self.mpl_toolbar.pan()  # we usually want to pan with mouse, since zooming is on the scroll

        self.current_modifiers = set()

        self.axes = self.figure.add_subplot(111)
        self.axes.set_adjustable('datalim')  # use whole area when keeping aspect ratio of images
        self.resizeEvent(None)

        self.setMinimumSize(200, 200)

    @property
    def visibilityChanged(self):
        return self.parentWidget().visibilityChanged

    def on_key_press(self, event):
        if event.key in MODIFIER_KEYS:
            self.current_modifiers.add(event.key)

        # implement the default mpl key press events described at
        # http://matplotlib.org/users/navigation_toolbar.html#navigation-keyboard-shortcuts
        key_press_handler(event, self.canvas, self.mpl_toolbar)

    def on_key_release(self, event):
        if event.key in MODIFIER_KEYS and event.key in self.current_modifiers:
            self.current_modifiers.remove(event.key)

    @staticmethod
    def get_scaled_lim(lim, focus, scale_factor, mode: str):
        # Todo: use some generic method to support any scale
        if mode == 'linear':
            return [(l - focus) * scale_factor + focus for l in lim]
        elif mode == 'log':
            return [exp((log(l) - log(focus)) * scale_factor + log(focus)) for l in lim]
        else:
            logging.error("cannot zoom on '{}' scale".format(mode))

    def on_scroll(self, event: MouseEvent):
        ax = self.axes

        SCALE_PER_TICK = 1.3
        if event.button == 'up':
            scale_factor = 1 / SCALE_PER_TICK
        elif event.button == 'down':
            scale_factor = SCALE_PER_TICK
        else:
            # deal with something that should never happen
            scale_factor = 1

        if 'control' not in self.current_modifiers:
            ax.set_xlim(self.get_scaled_lim(ax.get_xlim(), event.xdata, scale_factor, ax.get_xscale()))

        if 'shift' not in self.current_modifiers:
            ax.set_ylim(self.get_scaled_lim(ax.get_ylim(), event.ydata, scale_factor, ax.get_yscale()))

        self.draw()

    def draw(self):
        self.canvas.draw_idle()

    def resizeEvent(self, a0: QtGui.QResizeEvent):
        self.figure.tight_layout(pad=0.5)

    @staticmethod
    def dump_axis_state(axis: Axis):
        state = dict()
        if axis.minorTicks and axis.minorTicks:
            major = axis.majorTicks[0].gridOn
            minor = axis.minorTicks[0].gridOn
            if major or minor:
                state['grid'] = dict(
                    which='both' if major and minor else 'major' if major else 'minor'
                )
            else:
                state['grid'] = None
        return state

    @staticmethod
    def load_axis_state(axis: Axis, state: dict):
        if state['grid']:
            axis.grid(True, **state['grid'])
        else:
            axis.grid(False)

    def dump_state(self):
        return dict(
            xlim=self.axes.get_xlim(),
            ylim=self.axes.get_ylim(),
            xscale=self.axes.get_xscale(),
            yscale=self.axes.get_yscale(),
            x_axis=self.dump_axis_state(self.axes.get_xaxis()),
            y_axis=self.dump_axis_state(self.axes.get_yaxis()),
        )

    def restore_state(self, state: dict):
        if 'xlim' in state:
            self.axes.set_xlim(state['xlim'])
        if 'ylim' in state:
            self.axes.set_ylim(state['ylim'])
        if 'xscale' in state:
            self.axes.set_xscale(state['xscale'])
        if 'yscale' in state:
            self.axes.set_yscale(state['yscale'])
        if 'x_axis' in state:
            self.load_axis_state(self.axes.get_xaxis(), state['x_axis'])
        if 'y_axis' in state:
            self.load_axis_state(self.axes.get_yaxis(), state['y_axis'])
