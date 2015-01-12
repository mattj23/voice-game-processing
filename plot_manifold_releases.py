"""
    Plots the solution manifold for a test file or set of test files with the
    release points plotted. It uses the solution manifold from the first plot,
    and if the solution manifold doesn't match for all of the subsequent plots
    it will crash without producing an image.

    You can drag and drop the test files onto plot_manifold_trace.py

"""

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
    TEST_FILES = []

    if len(sys.argv) > 1:
        TEST_FILES = sys.argv[1:]
    else:
        folder = "Solution Manifold 20141007/Hard Problem"
        TEST_FILES = [os.path.join(folder, item) for item in os.listdir(folder)[:15]]
        # raise Exception("Need specified files!")
    
    # Load files and ensure that they all have the same manifold token
    tokens = []
    testData = []
    for test in TEST_FILES:
        if not os.path.exists(test):
            raise Exception("Cannot find test file '{}'".format(test))
        data = manifold_library.load_test_file(test)
        testData.append(data)
        tokens.append(manifold_library.generate_manifold_token(data))
    if len(list(set(tokens))) > 1:
        raise Exception("Not all files have the same solution manifold!")

    # Order the tests by time
    testData.sort(key = lambda element: element['timestamp'])

    # Create the plot of the solution manifold
    manifold = manifold_library.get_solution_manifold(testData[0])

    angles, stretches, output = manifold_library.get_manifold_draw_matrix(manifold)
    x = numpy.array(angles)
    y = numpy.array(stretches)
    z = numpy.array(output)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(z, aspect='auto', origin ='lower', cmap = plt.cm.hot, extent=(x.min(), x.max(), y.min(), y.max()))

    # Create the release data
    a = []
    s = []
    t = []
    for i, data in enumerate(testData):
        # Get an x, y trace of angle and stretch during the voicing
        a.append(manifold_library.get_angle(data['release_pitch'], data))
        s.append(manifold_library.get_stretch(data['release_volume'], data))
        t.append(i)
    a = numpy.array(a)
    t = numpy.array(t)
    s = numpy.array(s)

    colorMap = plt.cm.autumn
    ax.scatter(a, s, c=t, cmap=colorMap, s=40)

    # Finalize the plot
    ax.axis([x.min(), x.max(), y.min(), y.max()])
    plt.ylabel("Stretch")
    plt.xlabel("Angle (degrees)")
    plt.title("Test Output - Release Data")
    plt.show()


if __name__ == '__main__':
    main()