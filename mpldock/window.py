import json
import logging
import signal
from dataclasses import dataclass
from os import path
from typing import Callable, Dict

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QComboBox, QDockWidget, QMainWindow, QMenu, QWidget, QApplication

from .common import named

logging.basicConfig(level=logging.INFO)


@dataclass
class WidgetInfo:
    widget: QWidget
    name: str  # used to programatically identify widget instance (in configs, in function calls)
    title: str
    dock_widget: QDockWidget
    save_state: Callable = lambda o: dict()
    load_state: Callable = lambda o, s: None
    remove_action = None


class Window(QMainWindow):
    def __init__(self, parent=None, widget_title=None, global_id=None):
        super().__init__(parent)
        # self.setCentralWidget(QTextEdit())
        # noinspection PyTypeChecker
        self.global_id = global_id
        self.setCentralWidget(None)
        self.setDockNestingEnabled(True)
        self.setWindowTitle(widget_title)

        self.widgets = {}  # type: Dict[str, WidgetInfo]

        self.file_menu = QMenu('&File', self)
        self.save_layout_action = self.file_menu.addAction('&Save layout', self.save_state_to_file, Qt.CTRL + Qt.Key_S)
        self.save_layout_action.setEnabled(bool(self.global_id))
        self.menuBar().addMenu(self.file_menu)

        # self.add_menu = QMenu('&Add widget', self)
        # self.menuBar().addSeparator()
        # self.menuBar().addMenu(self.add_menu)

        self.remove_menu = QMenu('&Remove widget', self)
        self.menuBar().addMenu(self.remove_menu)

        self.close_callback = None

        self.resize(400, 400)  # workaround some bugs

        self.widgets_state = dict()

        file_name = "{}.state.json".format(self.global_id)
        if path.exists(file_name):
            try:
                with open(file_name) as f:
                    loaded_state = json.load(f)
                    self.loaded_state = loaded_state
                    self.widgets_state = loaded_state['widgets']

                    for widget_name, (widget_title, state) in self.widgets_state.items():
                        print(f"adding {widget_name} {widget_title}")
                        # widget.show()
                        self.add(named(QWidget(), widget_name, widget_title))

                    self.restoreGeometry(bytes.fromhex(loaded_state['geometry']))
                    self.restoreState(bytes.fromhex(loaded_state['state']))
            except Exception:
                logging.exception("exception during reading state file; ignoring")

    def remove_widget(self, widget_name):
        wi = self.widgets[widget_name]
        self.remove_menu.removeAction(wi.remove_action)
        self.removeDockWidget(wi.dock_widget)
        wi.widget.destroy()
        wi.dock_widget.destroy()
        del self.widgets[widget_name]

    def closeEvent(self, a0: QCloseEvent):
        self.save_state_to_file()
        if self.close_callback:
            self.close_callback()

    def save_state_to_file(self):
        if self.global_id:
            state_as_json = json.dumps(
                self.dump_state())  # we do it before overwritting a file since there may be error
            with open("{}.state.json".format(self.global_id), 'w') as f:
                f.write(state_as_json)

    def dump_state(self):
        widgets_state = {}
        for i in self.widgets.values():
            try:
                widgets_state[i.name] = i.title, i.save_state(i.widget)
            except Exception:
                logging.exception("ignoring exception during serialization of {}".format(i.dock_widget.windowTitle()))

        return dict(
            geometry=bytes(self.saveGeometry()).hex(),
            state=bytes(self.saveState()).hex(),
            widgets=widgets_state
        )

    def load_state(self, state: dict):
        pass


    # FIXME: refactor: add, remove, replace
    def add(self, widget: QWidget, save_state: Callable = lambda a: dict(), load_state: Callable = lambda a, b: None):
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
                        save_state=save_state, load_state=load_state)
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
        state = self.widgets_state.get(name)
        widget_instance = self.widgets[name]
        if state is not None:
            widget_instance.load_state(widget, state)

    def run(self):
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        return QApplication.exec()
