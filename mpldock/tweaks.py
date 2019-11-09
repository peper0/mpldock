import matplotlib

def image():
    matplotlib.rcParams['image.interpolation'] = 'nearest'
    matplotlib.rcParams['image.aspect'] = 'equal'
    matplotlib.rcParams.update({'font.size': 6})

def tweak_axes(axes):
    axes.set_adjustable('datalim')  # use whole area when keeping aspect ratio of images
