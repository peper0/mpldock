from numbers import Number
from typing import Callable, Dict, Any, Union, Tuple, List

from PyQt5.QtWidgets import QWidget


def named(widget: QWidget, name, title=None) -> QWidget:
    if title is None:
        title = name
    widget.setObjectName(name)
    widget.setWindowTitle(title)
    return widget


DumpedState = Union[str, Number, Dict[Union[str, Number], 'DumpedState'], List['DumpedState'], Tuple['DumpedState']]
DumpStateFunction = Callable[[], DumpedState]
RestoreStateFunction = Callable[[DumpedState], None]