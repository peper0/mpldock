import matplotlib.pyplot as plt

from mpldock import persist_layout

plt.switch_backend('module://mpldock.backend')
persist_layout('1e2682b5-4408-42a6-ae97-3c11332a96fa')
# window("matplotlib backend example")

plt.figure("some plot")
plt.plot([1, 5, 3])
plt.figure("another plot")
plt.plot([5, 0, 1])

plt.figure("subplots")
plt.subplot('220').plot([0, 0, 4])
plt.subplot('221').plot([0, 1, 4])
plt.subplot('222').plot([0, 2, 4])
plt.subplot('223').plot([0, 3, 4])

plt.show()
