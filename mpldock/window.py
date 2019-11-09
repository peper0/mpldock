import json
import logging
import signal
from dataclasses import dataclass
from os import path
from typing import Callable, Dict, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QApplication, QDockWidget, QMainWindow, QMenu, QWidget

from mpldock.common import DumpStateFunction, RestoreStateFunction
from .common import DumpedState
from .common import named
from .statemanager import StateManager

logging.basicConfig(level=logging.INFO)


@dataclass
class WidgetInfo:
    widget: QWidget
    name: str  # used to programatically identify widget instance (in configs, in function calls)
    title: str
    dock_widget: QDockWidget
    dump_state: DumpStateFunction = lambda: dict()
    restore_state: RestoreStateFunction = lambda s: None
    remove_action = None


class Window(QMainWindow):
    def __init__(self, parent, title, name, state_manager: StateManager):
        """
        :param parent:
        :param title: any descriptive string
        :param name: a string that identifies this window (unique)
        :param state_manager:
        """
        super().__init__(parent)
        # self.setCentralWidget(QTextEdit())
        # noinspection PyTypeChecker
        self.name = name
        self.state_manager = state_manager
        self.setCentralWidget(None)
        self.setDockNestingEnabled(True)
        self.setWindowTitle(title)

        self.widgets = {}  # type: Dict[str, WidgetInfo]

        self.file_menu = QMenu('&File', self)
        self.menuBar().addMenu(self.file_menu)

        self.layout_menu = QMenu('&Layout', self)
        self.menuBar().addMenu(self.layout_menu)
        self.save_layout_action = self.layout_menu.addAction('&Save', state_manager.save_as_last, Qt.CTRL + Qt.Key_S)
        self.save_layout_action.setEnabled(state_manager.has_last())
        self.save_layout_def_action = self.layout_menu.addAction('Save as &default',
                                                               state_manager.save_as_default)
        self.save_layout_def_action.setEnabled(state_manager.has_factory_default())


        # self.add_menu = QMenu('&Add widget', self)
        # self.menuBar().addSeparator()
        # self.menuBar().addMenu(self.add_menu)

        self.remove_menu = QMenu('&Remove widget', self)
        self.menuBar().addMenu(self.remove_menu)

        self.close_callback = None

        self.resize(400, 400)  # workaround some bugs

        self.loaded_widgets_state = dict()

        self.state_manager.add_client(self.name, self.dump_state, self.restore_state)
        loaded_state = self.state_manager.get_client_state(self.name)
        if loaded_state is not None:
            self.restore_state(loaded_state)

    def remove_widget(self, widget_name):
        wi = self.widgets[widget_name]
        self.remove_menu.removeAction(wi.remove_action)
        self.removeDockWidget(wi.dock_widget)
        wi.widget.destroy()
        wi.dock_widget.destroy()
        del self.widgets[widget_name]

    def closeEvent(self, a0: QCloseEvent):
        self.state_manager.save_as_last()
        if self.close_callback:
            self.close_callback()

    def dump_state(self):
        widgets_state = {}
        for i in self.widgets.values():
            try:
                widgets_state[i.name] = i.title, i.dump_state()
            except Exception:
                logging.exception("ignoring exception during serialization of {}".format(i.dock_widget.windowTitle()))

        return dict(
            geometry=bytes(self.saveGeometry()).hex(),
            state=bytes(self.saveState()).hex(),
            widgets=widgets_state
        )

    def restore_state(self, window_state: DumpedState):
        try:
            self.loaded_state = window_state
            self.loaded_widgets_state = window_state['widgets']

            for widget_name, (widget_title, widget_state) in self.loaded_widgets_state.items():
                if widget_name not in self.widgets:
                    print(f"adding {widget_name} {widget_title}")
                    # widget.show()
                    self.add(named(QWidget(), widget_name, widget_title))
                else:
                    self.widgets[widget_name].restore_state(widget_state)

            self.restoreGeometry(bytes.fromhex(window_state['geometry']))
            self.restoreState(bytes.fromhex(window_state['state']))
        except Exception:
            logging.exception("exception during reading state file; ignoring")

    # FIXME: refactor: add, remove, replace
    def add(self, widget: QWidget, dump_state: DumpStateFunction = lambda: dict(),
            restore_state: RestoreStateFunction = lambda b: None):
        name = widget.objectName()
        assert name
        title = widget.windowTitle() or name
        widget_instance = self.widgets.get(name)

        if widget_instance is None:
            dock_widget = QDockWidget(title)
            dock_widget.setObjectName(f"{name}__docked")
            dock_widget.setWidget(widget)
            self.addDockWidget(Qt.RightDockWidgetArea, dock_widget)
        else:
            dock_widget = widget_instance.dock_widget
            dock_widget.setWindowTitle(title)
            dock_widget.setWidget(widget)
            dock_widget.show()
            if widget_instance.widget:
                widget_instance.widget.close()
            self.remove_menu.removeAction(widget_instance.remove_action)

        widget.setParent(dock_widget)
        wi = WidgetInfo(widget=widget, name=name, title=title, dock_widget=dock_widget,
                        dump_state=dump_state, restore_state=restore_state)
        self.widgets[name] = wi

        def remove_widget():
            self.remove_widget(name)

        wi.remove_action = self.remove_menu.addAction(title, remove_widget)

        def title_changed(new_title):
            print(f"title changed to {new_title}")
            dock_widget.setWindowTitle(new_title)
            wi.title = new_title
            wi.remove_action.setText(new_title)

        widget.windowTitleChanged.connect(title_changed)

        def forbid_name_change(new_name):
            raise Exception("Name changing after adding to docks is forbidden!")

        widget.objectNameChanged.connect(forbid_name_change)

        self.restore(widget)

    def restore(self, widget: QWidget):
        name = widget.objectName()
        state = self.loaded_widgets_state.get(name)
        widget_instance = self.widgets[name]
        if state is not None:
            widget_instance.restore_state(state)

    def run(self):
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        return QApplication.exec()
