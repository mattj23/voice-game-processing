"""
    Demonstrates the temporal calculations
"""

__author__ = 'matt'

import library.tests
import library.temporal


def main():

    # Load the data from the test library, filter out everything but Jarrad's tests,
    # and then break it into test blocks separated by 10 minutes or more of inactivity
    tests = library.tests.TestLibrary("data")
    tests = tests.filter({"subject": "Jarrad"})
    test_blocks = tests.break_into_blocks()

    # Isolate the very first of Jarrad's blocks
    first_block = test_blocks['Jarrad'][0]

    # Print the block summary
    first_block.print_summary()

    # Perform the lag-1 autocorrelation for the closest approach
    coeff = library.temporal.lag_1_autocorrelation(first_block, "closest_approach")
    print "Lag 1 autocorrelation coefficient for closest approach: {}".format(coeff)

    # Perform the lag-1 autocorrelation for the release angle
    coeff = library.temporal.lag_1_autocorrelation(first_block, "release_angle")
    print "Lag 1 autocorrelation coefficient for release angle: {}".format(coeff)

    # Perform the lag-1 autocorrelation for the release stretch
    coeff = library.temporal.lag_1_autocorrelation(first_block, "release_stretch")
    print "Lag 1 autocorrelation coefficient for release stretch: {}".format(coeff)

    # Perform the DFA and print out the slope for the closest approach
    results = library.temporal.detrended_fluctuation_analysis(first_block, "closest_approach")
    print "Detrended Fluctuation Scaling Factor for closest approach: {}".format(results["linear_regression"]["slope"])

    # Perform the DFA and print out the slope for the release angle
    results = library.temporal.detrended_fluctuation_analysis(first_block, "release_angle")
    print "Detrended Fluctuation Scaling Factor for release angle: {}".format(results["linear_regression"]["slope"])

    # Perform the DFA and print out the slope for the release stretch
    results = library.temporal.detrended_fluctuation_analysis(first_block, "release_stretch")
    print "Detrended Fluctuation Scaling Factor for release stretch: {}".format(results["linear_regression"]["slope"])

if __name__ == '__main__':
    main()

