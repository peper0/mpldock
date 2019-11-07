import matplotlib.pyplot as plt

from mpldock import window

plt.switch_backend('module://mpldock.backend')

window("matplotlib backend example", '1e2682b5-4408-42a6-ae97-3c11332a96fa')

plt.figure("some plot")
plt.plot([1, 5, 3])
plt.figure("another plot")
plt.plot([5, 0, 1])

plt.figure("subplots")
a = plt.subplot('220')
a.plot([3, 2, 4])

plt.close()

plt.show()
