from typing import Callable, Union

from PyQt5.QtWidgets import QApplication, QWidget

from .window import Window

WindowSpec = Union[str, Window, None]
WidgetSpec = Union[str, QWidget, None]

current_main_window = None  # type: Window
windows_by_title = dict()

qapplication = None


def _create_window(title, global_id, close_callback):
    global qapplication
    qapplication = qapplication or QApplication.instance() or QApplication([])  # just ensure application exist
    window = Window(widget_title=title, global_id=global_id)
    window.show()
    window.close_callback = close_callback
    return window


def _obtain_window(window_spec: WindowSpec = None, global_id=None) -> Window:
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

        window = _create_window(title=title, global_id=global_id, close_callback=window_closed)
        windows_by_title[title] = window

    current_main_window = window
    return window


def add_dock(widget: QWidget, save_state: Callable, load_state: Callable, window: WindowSpec = None):
    """
    Adds a widget to a current window (if given) or to a current one (if None).
    :param widget: Any qt widget.
    :param save_state: Function used to save an internal state of the widget.
    :param load_state: Function used to restore an internal state of the widget.
    :param window:
    """
    window = _obtain_window(window)
    window.add(widget, save_state, load_state)


def window(title: str = None, global_id: str = None) -> Window:
    """
    Returns a window with given title. Creates if not existing. Sets it as a current window.
    :param title: A window title.
    :param global_id: An id used to store layout (user settings scope).
    :return:
    """
    return _obtain_window(title, global_id)

def run():
    return window().run()