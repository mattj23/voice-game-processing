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

    # The "angles" and "stretches" objects are one dimensonal arrays that
    # contain the values of the rows and columns in the "output" matrix.  Rows
    # correspond with different values of stretch, and columns correspond with
    # different values of angle. That is, position i of the stretches array
    # corresponds with the stretch value of row i in the output matrix, and
    # position j of the angles list corresponds with the angular values of the
    # elements in column j of the output matrix.
    angles, stretches, output = manifold_library.get_manifold_matrix(manifold)

    # Write out at comma delimited text file of the output matrix.
    with open("manifold.txt", "w") as handle:
        handle.write("\n".join([",".join(["{}".format(c) for c in row]) for row in output]))


if __name__ == '__main__':
    main()