"""
    Demonstrates the temporal calculations
"""
import math

__author__ = 'matt'

import library.tests
import library.temporal


def main():

    # Load the data from the test library, filter out everything but Jarrad's tests,
    # and then break it into test blocks separated by 10 minutes or more of inactivity
    tests = library.tests.TestLibrary("data")
    tests = tests.filter({"subject": "NM002"})
    test_blocks = tests.break_into_blocks()

    # Isolate the very first of Jarrad's blocks
    first_block = test_blocks['NM002'][0]

    # Print the block summary
    first_block.print_summary()

    # Perform the lag-1 autocorrelation for the closest approach
    coeff = library.temporal.lag_1_autocorrelation(first_block, "closest_approach")
    print "Lag 1 autocorrelation coefficient for closest approach: {}".format(coeff)

    # Perform the DFA and print out the slope for the closest approach
    results = library.temporal.detrended_fluctuation_analysis(first_block, "closest_approach")
    print "Detrended Fluctuation Scaling Factor for closest approach: {}".format(results["linear_regression"]["slope"])

    print ""
    print "angle, lag1, dfa"
    for angle, heading in generate_headings():
        lag1 = library.temporal.lag_1_autocorrelation(first_block, heading)
        dfa = library.temporal.detrended_fluctuation_analysis(first_block, heading)
        print "{}, {}, {}".format(angle, lag1, dfa)

def generate_headings():
    for i in range(180):
        yield i, "x" + str(i * math.pi / 180.0)


if __name__ == '__main__':
    main()

