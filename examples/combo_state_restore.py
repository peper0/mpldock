import os
from functools import partial
from typing import Dict

from PyQt5.QtWidgets import QApplication, QComboBox

from mpldock import add_dock, named, persist_layout, run

persist_layout('7ec682b5-4408-42a6-ae97-3c11332a96f6', os.path.realpath(__file__))


def save_state_combo(o: QComboBox) -> Dict:
    return dict(
        current_text=o.currentText()
    )


def load_state_combo(o: QComboBox, state: Dict):
    if 'current_text' in state:
        o.setCurrentText(state['current_text'])


qapp = QApplication([])

combo = QComboBox()
combo.addItems(['oranges', 'apples'])

add_dock(named(combo, name='fruits', title='fruits selector'),
         dump_state=partial(save_state_combo, combo),
         restore_state=partial(load_state_combo, combo))

combo2 = QComboBox()
combo2.addItems(['a', 'b', 'c'])
add_dock(named(combo2, name='letters'),
         dump_state=partial(save_state_combo, combo2),
         restore_state=partial(load_state_combo, combo2))

run()
