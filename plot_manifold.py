"""
    Plots the solution manifold for a test file or set of test files with the
    release points plotted. It uses the solution manifold from the first plot,
    and if the solution manifold doesn't match for all of the subsequent plots
    it will crash without producing an image.

    You can drag and drop the test files onto plot_manifold_trace.py

"""



import matplotlib
import matplotlib.pyplot as plt 
import numpy
import matplotlib.cm as cm 
import matplotlib.mlab as mlab 

import library.manifold
import library.tests


def plot(test_group, plot_title, points=[]):

    # Validate that the test group all has the same manifold
    if not library.manifold.validate_same_manifold(test_group):
        raise Exception("specified test group does not all lie on the same manifold")

    # Create the plot of the solution manifold
    test_data = test_group.get_data_list()
    manifold = library.manifold.get_solution_manifold(test_data[0])

    angles, stretches, output = library.manifold.get_manifold_draw_matrix(manifold)
    x = numpy.array(angles)
    y = numpy.array(stretches)
    z = numpy.array(output)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(z, aspect='auto', origin='lower', cmap=plt.cm.hot, extent=(x.min(), x.max(), y.min(), y.max()))


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

