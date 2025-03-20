import matplotlib.pyplot as plt
import numpy as np
import os.path


from mpldock import persist_layout, window

USE_MPLDOCK = True

script_dir = os.path.dirname(os.path.realpath(__file__))

if USE_MPLDOCK:
    plt.switch_backend('module://mpldock')
    persist_layout('1e2682b5-4408-42a6-ae97-23416178192', os.path.join(script_dir, 'me_layout.json'))
    window("Gradient analysis")

lenna_path = os.path.join(script_dir, 'lenna.png')
#lenna_path = 'examples/lenna.png'

img = plt.imread(lenna_path)

plt.figure("original image")
plt.imshow(img)

img_gray = np.mean(img, axis=-1)
plt.figure("grayscale")
plt.imshow(img_gray, cmap='gray')

img_dx = img_gray - np.roll(img_gray, 1, axis=1)
plt.figure("gradient x")
plt.imshow(img_dx, cmap='seismic')

img_dy = img_gray - np.roll(img_gray, 1, axis=0)
plt.figure("gradient y")
plt.imshow(img_dy, cmap='seismic')

img_angle = np.rad2deg(np.arctan2(img_dy, img_dx))
plt.figure("gradient dir")
plt.imshow(img_angle, cmap='hsv', vmin=-180, vmax=180)
plt.colorbar()

plt.figure("image histogram")
plt.hist(img_gray.flat, bins=64)

plt.figure("gradient dir histogram")
plt.hist(img_angle.flat, bins=100)

plt.figure("gradient x histogram")
plt.hist(img_dx.flat, bins=100)

plt.figure("gradient y histogram")
plt.hist(img_dy.flat, bins=100)


plt.show()
