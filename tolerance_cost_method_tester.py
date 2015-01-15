"""
    This program computes the tolerance cost of a distribution of tests.


"""

import os
import json
import manifold_library
import numpy
import time

import scipy.optimize 

def evaluate(x, distribution, simulator):
    """ This is the evaluation function, which produces a single numerical
    output which the scipy optimizer will attempt to minimize. In our case,
    imagine that this is a function F(u, v) which we are trying to minimize.
    The variables u and v are the x and y shift in the distribution,
    respectively.  The scipy optimizer will attempt to minimize F by making
    repeated calls to this function to test its gradient and value.  The
    optimizer will provide u and v to us in the form of the numpy array 'x'
    which will take the form of x = [u, v].  It's up to us to perform the
    evaluation here and return the result."""

    u, v = x 
    test = [(angle + u, stretch + v) for angle, stretch in distribution ]
    
    sumValue = 0
    for angle, stretch in test:
        sumValue += abs(simulator.get_closest_approach(angle, stretch))
    return sumValue

def main():
    # Load the distribution of tests
    testFolder = "Data/tolerance_test"
    testSet = [os.path.join(testFolder, item) for item in os.listdir(testFolder) if item.endswith(".json")]
    
    # Begin by verifying that all of the specified tests actually have the same
    # setting parameters and so lie on the same solution manifold.  This is
    # critical for the results of this test to make any sense.  If any of the
    # tests have a different manifold than the others, we raise an error here
    # instead of proceeding with the analysis.
    if not manifold_library.validate_same_manifold(testSet):
        raise Exception("Not all of the specified tests have the same manifold.")

    # Now that we've verified that all of the tests have the same manifold,
    # let's load a simulator object into memory
    temporaryData = manifold_library.load_test_file(testSet[0])
    simulator = manifold_library.SolutionManifold(temporaryData['settings'])

    # Now let's assemble the test distribution, which ends up as a nested list
    # of release angle and stretch pairs.
    distribution = []
    for item in testSet:
        data           = manifold_library.load_test_file(item)
        releaseAngle   = data['release_angle']
        releaseStretch = data['release_stretch']
        distribution.append([releaseAngle, releaseStretch])

    # Create the initial guess
    x0 = [0, 0]

    # Check the initial score
    initialScore = evaluate(x0, distribution, simulator)

    # Perform the optimization
    methods = ['Powell'] # ['Nelder-Mead', 'COBYLA', ]
    for method in methods:
        result = scipy.optimize.minimize(evaluate, x0, method=method, args=(distribution, simulator) )
        # print result

        print "Method: {}".format(method)
        print "============================="
        print "Local optimization:"
        print "    Initial score: {:.1f} px".format(initialScore)
        print "    Final score:   {:.1f} px".format(evaluate(result.x, distribution, simulator))
        print "    Success:    {}".format(result.success)

        # Basin hopping
        result = scipy.optimize.basinhopping(evaluate, x0, minimizer_kwargs={"method":method, "args":(distribution, simulator)}, niter=10)
        # print result
        print "Global (basin hopping):"
        print "    Initial score: {:.1f} px".format(initialScore)
        print "    Final score:   {:.1f} px".format(evaluate(result.x, distribution, simulator))
        
        print ""
    simulator.close_process()


if __name__ == '__main__':
    main()