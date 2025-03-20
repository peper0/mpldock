import os.path

import matplotlib

from mpldock import persist_layout
import matplotlib.pyplot as plt

matplotlib.use('module://mpldock')

persist_layout('1e2682b5-4408-42a6-ae97-3290153294', os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fd_layout.json'))

plt.figure("some plot")
plt.plot([1, 5, 3])
plt.figure("another plot")
plt.plot([5, 0, 1])

plt.show()
