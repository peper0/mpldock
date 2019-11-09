import os
from typing import Union

from PyQt5.QtWidgets import QApplication, QWidget

from mpldock.common import DumpStateFunction, RestoreStateFunction
from .statemanager import StateManager
from .window import Window

WindowSpec = Union[str, Window, None]
WidgetSpec = Union[str, QWidget, None]

current_main_window = None  # type: Window
windows_by_title = dict()

qapplication = None
state_manager = None


def _create_window(title, name, close_callback):
    global qapplication
    qapplication = qapplication or QApplication.instance() or QApplication([])  # just ensure application exist
    window = Window(parent=None, title=title, name=name, state_manager=obtain_state_manager())
    window.show()
    window.close_callback = close_callback
    return window


def _obtain_window(window_spec: WindowSpec = None) -> Window:
    """
    Returns window with given name. Create it if doesn't exist. If `name` is `None`, return last window used.
    :param title:
    :return:
    """
    global current_main_window
    if isinstance(window_spec, Window):
        current_main_window = window_spec
        return window_spec
    if window_spec is None:
        if current_main_window is not None:
            return current_main_window
        for i in range(1, 1000000):
            title = "window {}".format(i)
            if title not in windows_by_title:
                break
    else:
        title = window_spec

    if title in windows_by_title:
        window = windows_by_title[title]
    else:
        def window_closed():
            del windows_by_title[title]
            global current_main_window
            if current_main_window == window:
                current_main_window = None

        window = _create_window(title=title, name=title, close_callback=window_closed)
        windows_by_title[title] = window

    current_main_window = window
    return window


def add_dock(widget: QWidget, dump_state: DumpStateFunction, restore_state: RestoreStateFunction,
             window: WindowSpec = None):
    """
    Adds a widget to a current window (if given) or to a current one (if None).
    :param widget: Any qt widget.
    :param dump_state: Function used to save an internal state of the widget.
    :param restore_state: Function used to restore an internal state of the widget.
    :param window:
    """
    window = _obtain_window(window)
    window.add(widget, dump_state, restore_state)


def window(title: str = None) -> Window:
    """
    Returns a window with given title. Creates if not existing. Sets it as a current window.
    :param title: A window title.
    :param global_id: An id used to store layout (user settings scope).
    :return:
    """
    return _obtain_window(title)


def run():
    # FIXME: there should be one common window manager with "run" (it should also be owner of _create_window method)
    return window().run()


def obtain_state_manager():
    global state_manager
    if state_manager is None:
        # if it's not initialized until first use, we assume the user does not want persistance
        state_manager = StateManager(None, None)
    return state_manager


def persist_layout(id: str, factory_default_path=None, load_now=True):
    """
    Call this function before creating any other window to restore the layout on each run.
    :param id: Any string that is unique to the application.
    :param factory_default_path: A path to a file that stores factory default settings. Usually, it is a file that you
     want to ship along with your application. It is used if there is no locally saved layout.
    :param load_now: Load state immediately.
    :return:
    """
    global state_manager
    assert state_manager is None, "'persist_state' must be called before creating any window"
    state_manager = StateManager(id, factory_default_path)
    if id and load_now:
        success = state_manager.restore_from_system(id)
        if not success and factory_default_path and os.path.exists(factory_default_path):
            state_manager.restore_default()
