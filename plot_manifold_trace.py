"""
    Plots the solution manifold for a test file or set of test files with the
    trace on top of the plot. It uses the solution manifold from the first plot,
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
        # folder = "Solution Manifold 20141007/Hard Problem"
        # TEST_FILES = [os.path.join(folder, item) for item in os.listdir(folder)[:3]]
        raise Exception("Need specified files!")
    
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


    # Create the plot of the solution manifold
    manifold = manifold_library.get_solution_manifold(testData[0])

    angles, stretches, output = manifold_library.get_manifold_draw_matrix(manifold)
    x = numpy.array(angles)
    y = numpy.array(stretches)
    z = numpy.array(output)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(z, aspect='auto', origin ='lower', cmap = plt.cm.hot, extent=(x.min(), x.max(), y.min(), y.max()))

    # Create and add the plots of the individual traces
    for data in testData:
        # Get an x, y trace of angle and stretch during the voicing
        a = []
        t = []
        s = []
        for time, pitch, volume in data['trace']:
            if time > data['release_time']:
                break
            t.append(time)
            a.append(manifold_library.get_angle(pitch, data))
            s.append(manifold_library.get_stretch(volume, data))
        a = numpy.array(a)
        t = numpy.array(t)
        s = numpy.array(s)

        colorMap = plt.cm.autumn

        points = numpy.array([a, s]).T.reshape(-1, 1, 2)
        segments = numpy.concatenate([points[:-1], points[1:]], axis=1)
        lc = LineCollection(segments, cmap=colorMap)
        lc.set_array(t)
        lc.set_linewidth(3)

        #ax.plot(a, s)
        plt.gca().add_collection(lc)
        ax.scatter(a, s, c=t, cmap=colorMap, s=40)

    # Finalize the plot
    ax.axis([x.min(), x.max(), y.min(), y.max()])
    plt.ylabel("Stretch")
    plt.xlabel("Angle (degrees)")
    plt.title("Test Traces")
    plt.show()


if __name__ == '__main__':
    main()