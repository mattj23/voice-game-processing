"""
    Plots the solution manifold for a test file or set of test files with the
    release points plotted. It uses the solution manifold from the first plot,
    and if the solution manifold doesn't match for all of the subsequent plots
    it will crash without producing an image.

"""
import matplotlib.pyplot as plt
import numpy
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap

import library.manifold
import library.tests

c_dict = {'red': ((0,1,1), (1,0,0)),
        'green': ((0,1,1), (1,0,0)),
        'blue': ((0,1,1), (0.1,0,0), (1,0,0))}
c_map = LinearSegmentedColormap("yellow", c_dict)

def __validate_and_get_dictionaries(test_group):
    """
    Validate that the test_group argument is a TestGroup or TestLibrary object and return a list of the raw data
    dictionaries.
    :param test_group: a TestGroup or TestLibrary object
    :return: a list of test data dictionaries
    """
    # Validate that the test_group is a TestGroup object
    if not (isinstance(test_group, library.tests.TestGroup) or isinstance(test_group, library.tests.TestLibrary)):
        raise Exception("test_group must be a TestGroup or TestLibrary object")

    # Validate that the test group all has the same manifold
    if not library.manifold.validate_same_manifold(test_group):
        raise Exception("specified test group does not all lie on the same manifold")

    # Create the plot of the solution manifold
    return test_group.get_data_list()



def plot(test_group, plot_title, points=[]):
    """
    Create a matplotlib plot of the manifold of test_group, and plot series of points on it.  An optional argument
    "points" is a list of dictionaries which specify sets of angle, velocity pairs and colors to plot on the manifold.
    In the case that points is empty, the release angle and release stretch pairs of test_group are plotted on the
    manifold in blue.
    :param test_group: a TestGroup
    :param plot_title: a string with the title of the plot
    :param points:  an optional list of dictionaries [{"points": [], "color":"c"}, ...] to draw instead of test_group
    :return:
    """
    test_data = __validate_and_get_dictionaries(test_group)
    manifold = library.manifold.get_solution_manifold(test_data[0])
    cpa_max = max([abs(p['cpa']) for k, p in manifold.items()])

    angles, stretches, output = library.manifold.get_manifold_draw_matrix(manifold)
    x = numpy.array(angles)
    y = numpy.array(stretches)
    z = numpy.array(output)

    fig, ax = plt.subplots(figsize=(8, 8))
    cax = ax.imshow(z, aspect='auto', origin='lower', cmap=c_map, vmin=0, vmax=cpa_max, extent=(x.min(), x.max(), y.min(), y.max()))
    plt.colorbar(cax)

    # Create the release data point series
    if not points:
        # Create the release data
        release_points = test_group.get_release_points()
        a, s = zip(*release_points)
        ax.scatter(a, s, color="b")
    else:
        # We are expecting a list of points
        for point_set in points:
            # Point set should be a dictionary of the following form:
            # {'points': [(a1,v1), (a2, v2) ... ], 'color': 'c'}
            a, s = zip(*point_set['points'])
            ax.scatter(a, s, color=point_set['color'])

    # Finalize the plot
    ax.axis([x.min(), x.max(), y.min(), y.max()])
    plt.ylabel("Stretch")
    plt.xlabel("Angle (degrees)")
    plt.title(plot_title)
    plt.show()

def plot_traces(test_group, plot_title):
    """
    Plot the traces for a test distribution on a manifold.
    :param test_group:
    :param plot_title:
    :return:
    """
    test_data = __validate_and_get_dictionaries(test_group)
    manifold = library.manifold.get_solution_manifold(test_data[0])
    cpa_max = max([abs(p['cpa']) for k, p in manifold.items()])

    angles, stretches, output = library.manifold.get_manifold_draw_matrix(manifold)
    x = numpy.array(angles)
    y = numpy.array(stretches)
    z = numpy.array(output)

    fig, ax = plt.subplots(figsize=(8, 8))
    cax = ax.imshow(z, aspect='auto', origin='lower', cmap=c_map, vmin=0, vmax=cpa_max, extent=(x.min(), x.max(), y.min(), y.max()))
    plt.colorbar(cax)

    for data in test_data:
        # Get an x, y trace of angle and stretch during the voicing
        a = []
        t = []
        s = []
        for time, pitch, volume in data['trace']:
            if time > data['release_time']:
                break
            t.append(time)
            a.append(library.manifold.get_angle(pitch, data))
            s.append(library.manifold.get_stretch(volume, data))
        a = numpy.array(a)
        # t = numpy.array(t)
        s = numpy.array(s)

        colorMap = None # plt.cm.autumn

        points = numpy.array([a, s]).T.reshape(-1, 1, 2)
        segments = numpy.concatenate([points[:-1], points[1:]], axis=1)
        lc = LineCollection(segments, colors='r')
        #lc.set_array(t)
        lc.set_linewidth(3)

        #ax.plot(a, s)
        plt.gca().add_collection(lc)
        ax.scatter(a, s, s=40, color='r')

    # Finalize the plot
    ax.axis([x.min(), x.max(), y.min(), y.max()])
    plt.ylabel("Stretch")
    plt.xlabel("Angle (degrees)")
    plt.title(plot_title)
    plt.show()