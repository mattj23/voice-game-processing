"""
    Plots the solution manifold for a test file.  You can drag and drop the test
    file onto plot_manifold.py or you can specify the test file here at the top
    of the file.

"""

TEST_FILE = r"D:\Workbench\PERSONAL\Voice\Processing\Solution Manifold 20141007\Hard Problem\Test 2014-09-13_15-04-44.json"


import os       
import json     
import datetime 
import math 
import sys 

import matplotlib
import matplotlib.pyplot as plt 
import numpy
import matplotlib.cm as cm 
import matplotlib.mlab as mlab 

import manifold_library

from matplotlib.collections import LineCollection


def main():
    global TEST_FILE

    if len(sys.argv) > 1:
        TEST_FILE = sys.argv[1]

    if not os.path.exists(TEST_FILE):
        raise Exception("Can't find '{}'".format(TEST_FILE))

    data = manifold_library.load_test_file(TEST_FILE)
    manifold = manifold_library.get_solution_manifold(data)

    angles, stretches, output = manifold_library.get_manifold_draw_matrix(manifold)
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