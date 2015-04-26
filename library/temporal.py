"""
    Code for the temporal analyses

"""
__author__ = 'matt'

import tests
import numpy
import subprocess
import os

def __auto_correlation(x, lag=1):
    """
    Perform an autocorrelation with a specified lag and return the correlation coefficient
    :param x: the array-like variable to perform the auto correlation on
    :param lag: the lag for the auto correlation, defaults to 1
    :return: the correlation coefficient
    """
    return numpy.corrcoef(numpy.array([x[0:len(x)-lag], x[lag:len(x)]]))

def lag_1_autocorrelation(test_group, property):
    """
    The lag-1 autocorrelation is performed on a sequential series of test results using the closest approach value.

    :rtype : dict
    :type property: str
    :type test_group: tests.TestGroup
    :param test_group: TestGroup to perform the autocorrelation on
    :param property: property to evaluate autocorrelation for
    :return: correlation coefficient
    """

    # Validate that this is a TestGroup object
    if not isinstance(test_group, tests.TestGroup):
        raise ValueError("The test_group argument passed to the lag_1_autocorrelation function must be a tests.TestGroup object")

    # Extract the closest approach value
    property_values, filenames = test_group.get_list_of_key(property)

    coefficient = __auto_correlation(property_values, 1)

    return coefficient[0, 1]


def detrended_fluctuation_analysis(test_group, property):
    """
    Use the dfa.exe located in the other_binaries folder of the library to perform
    a detrended fluctuation analysis.
    :param test_group:
    :param property:
    :return:
    """

    # See instructions on usage and input/output formats at
    # http://www.physionet.org/physiotools/dfa/dfa-1.htm

    # Find the executable
    this_path = os.path.dirname(__file__)
    executable = os.path.join(this_path, "other_binaries", "dfa.exe")
    if not os.path.exists(executable):
        raise Exception("Couldn't find the dfa.exe executable")

    print "all is well"