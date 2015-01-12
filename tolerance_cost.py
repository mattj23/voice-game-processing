"""
    This program computes the tolerance cost of a distribution of tests.


"""

import os
import json
import manifold_library
import numpy
import time

def main():
    # Load the distribution of tests
    testFolder = "Data/tolcost"
    testFolder = "Data/test"
    testFiles = [os.path.join(testFolder, item) for item in os.listdir(testFolder) if item.endswith(".json")]
    testSet = testFiles

    # Begin by verifying that all of the specified tests actually have the same
    # setting parameters and so lie on the same solution manifold.  This is
    # critical for the results of this test to make any sense.  If any of the
    # tests have a different manifold than the others, we raise an error here
    # instead of proceeding with the analysis.
    if not manifold_library.validate_same_manifold(testSet):
        raise Exception("Not all of the specified tests have the same manifold.")

    # Now that we've verified that all of the tests have the same manifold,
    # let's load that manifold into memory.
    temporaryData = manifold_library.load_test_file(testSet[0])
    manifold      = manifold_library.get_solution_manifold(temporaryData)

    # Convert the closest point of approach to the absolute value
    solution = manifold_library.SolutionManifold(manifold)

    x = time.time()

    for item in testSet:
        data = manifold_library.load_test_file(item)
        releaseAngle = manifold_library.get_angle(data['release_pitch'], data)
        releaseStretch = manifold_library.get_stretch(data['release_volume'], data)

        gameValue = data['closest_approach']
        solutionValue = solution.interpolate(releaseAngle, releaseStretch)
        
        difference = abs(gameValue - solutionValue)
        print difference
    print time.time() - x, "seconds"
if __name__ == '__main__':
    main()