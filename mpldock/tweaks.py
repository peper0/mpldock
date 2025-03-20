def image():
    import matplotlib  # we don't want to import at the toplevel to avoid activating repl when importing this module (e.g. in pycharm)

    matplotlib.rcParams["image.interpolation"] = "nearest"
    matplotlib.rcParams["image.aspect"] = "equal"
    matplotlib.rcParams.update({"font.size": 6})


def tweak_axes(axes):
    axes.set_adjustable("datalim")  # use whole area when keeping aspect ratio of images
