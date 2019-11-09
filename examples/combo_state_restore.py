from typing import Dict

from PyQt5.QtWidgets import QComboBox, QApplication

from mpldock import window, add_dock, named, run


def save_state_combo(o: QComboBox) -> Dict:
    return dict(
        current_text=o.currentText()
    )


def load_state_combo(o: QComboBox, state: Dict):
    if 'current_text' in state:
        o.setCurrentText(state['current_text'])


window("combo state restore", '7ec682b5-4408-42a6-ae97-3c11332a96f6')


combo = QComboBox()
combo.addItems(['oranges', 'apples'])


add_dock(named(combo, name='fruits', title='fruits selector'), dump_state=save_state_combo, restore_state=load_state_combo)

combo2 = QComboBox()
combo2.addItems(['a', 'b', 'c'])
combo2.setObjectName('letters')
add_dock(combo2, dump_state=save_state_combo, restore_state=load_state_combo)

run()