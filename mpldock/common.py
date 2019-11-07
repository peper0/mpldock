from PyQt5.QtWidgets import QWidget


def named(widget: QWidget, name, title=None) -> QWidget:
    if title is None:
        title = name
    widget.setObjectName(name)
    widget.setWindowTitle(title)
    return widget