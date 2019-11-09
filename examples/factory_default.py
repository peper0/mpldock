import os.path as opath

import matplotlib

from mpldock import persist_layout

matplotlib.use('module://mpldock.backend')

import matplotlib.pyplot as plt

persist_layout('1e2682b5-4408-42a6-ae97-3290153294', opath.join(opath.dirname(opath.realpath(__file__)), 'fd_layout.json'))

plt.figure("some plot")
plt.plot([1, 5, 3])
plt.figure("another plot")
plt.plot([5, 0, 1])

plt.show()
