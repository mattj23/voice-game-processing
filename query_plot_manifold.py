"""
    Plots the solution manifold for a test file.  You can drag and drop the test
    file onto plot_manifold.py or you can specify the test file here at the top
    of the file.

"""

import os
import sys 

import matplotlib
import matplotlib.pyplot as plt 
import numpy
import matplotlib.cm as cm 
import matplotlib.mlab as mlab 

import library.manifold

from matplotlib.collections import LineCollection


def main():

    # Get a test file from data
    test_files = [item for item in os.listdir('data') if item.endswith(".json")]
    data = library.manifold.load_test_file(test_files[0])

    manifold = library.manifold.get_solution_manifold(data)

    angles, stretches, output = library.manifold.get_manifold_draw_matrix(manifold)
    x = numpy.array(angles)
    y = numpy.array(stretches)
    z = numpy.array(output)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(z, aspect='auto', origin ='lower', cmap = plt.cm.hot, extent=(x.min(), x.max(), y.min(), y.max()))

    ax.axis([x.min(), x.max(), y.min(), y.max()])
    plt.ylabel("Stretch")
    plt.xlabel("Angle (degrees)")
    plt.title(os.path.basename(TEST_FILE))
    plt.show()


if __name__ == '__main__':
    main()