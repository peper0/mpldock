import matplotlib

def image():
    matplotlib.rcParams['image.interpolation'] = 'nearest'
    matplotlib.rcParams['image.aspect'] = 'equal'
    matplotlib.rcParams.update({'font.size': 6})
