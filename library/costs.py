"""
    costs.py

    This module exists to compute the three cost measures (tolerance cost, noise cost, and covariation cost) of groups
    of tests.
"""

import manifold
import scipy.optimize


def __tolerance_evaluate(x, distribution, simulator):
    """ This is the tolerance evaluation function, which produces a single numerical
    output which the scipy optimizer will attempt to minimize.

    In our case, imagine that this is a function F(u, v) which we are trying to
    minimize. The variables u and v are the x and y shift in the distribution,
    and the value of the function F is the mean of the closest approaches of a
    distribution shifted by u and v.

    The scipy optimizer will attempt to minimize F by making repeated calls to
    this function to test its gradient and value.  The optimizer will provide u
    and v to us in the form of the numpy array 'x' (the first argument in this
    function) which we will interpret as taking the form of x = [u, v].  It's up
    to us to perform the evaluation here and return the result."""

    # Extract u and v from the x array given to us by scipy
    u, v = x

    # Create a temporary test distribution that is shifted by u and v
    test = [(angle + u, stretch + v) for angle, stretch in distribution ]

    # Calculate the sum of the distributions
    sum_value = 0
    for angle, stretch in test:
        sum_value += abs(simulator.get_closest_approach(angle, stretch))

    # Return the mean value
    return sum_value / len(test)

def compute_tolerance_cost():
    pass