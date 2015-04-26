"""
    costs.py

    This module exists to compute the three cost measures (tolerance cost, noise cost, and covariation cost) of groups
    of tests.
"""

import manifold
import tests
import vector

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

def __load_tests(test_group):
    """
    Load the test data from a TestGroup object or a list of test filenames and return them as a list of test
    dictionaries.  Raise an exception if the data is not at TestGroup or list of test file names.
    :param test_group: Either a TestGroup object or a list of filenames
    :return:
    """
    if isinstance(test_group, tests.TestGroup) or isinstance(test_group, tests.TestLibrary):
        test_group = test_group.files

    if type(test_group) is not list:
        raise Exception("Expecting a TestGroup or list of test file names")

    test_data = []
    failed = []
    for item in test_group:
        data = tests.load_test_file(item)
        if data is None:
            failed.append(item)
        else:
            test_data.append(data)

    if failed:
        raise Exception("Loading tests failed on: " + ", ".join(failed) )
    return test_data


def compute_noise_cost(test_group):
    """
    Compute the noise cost for a TestGroup object or a list of filepaths using the algorithm described by Sternad and
    Cohen 2009. Return a dictionary with the results of the analysis.
    :param test_group: a TestGroup object or a list of paths of test .json files
    :return: a results dictionary
    """
    test_data = __load_tests(test_group)
    if not manifold.validate_same_manifold(test_data):
        raise Exception("The test group provided has tests which do not all lie on the same solution manifold")



    # Now that we've got the test data loaded and validated, we can create a simulator object based off of the settings
    # of the first test in the list (we have just validated that they are all the same, so this is acceptable)
    simulator = manifold.SolutionManifold(test_data[0]['settings'])

    # Find the mean point in the test group
    release_points = []
    for data in test_data:
        release_points.append(vector.Vector(data['release_angle'], data['release_stretch'], 0))
    n = len(release_points)
    mean_point = vector.get_average_point(release_points)

    # Get the initial score
    results = [abs(simulator.get_closest_approach(v.x, v.y)) for v in release_points]
    initial_score = sum(results) / n

    # Create a list where each point is represented by a vector from the mean point
    mean_vectors = [point - mean_point for point in release_points]

    # Go through 100 steps and transform each point by that percentage from the mean
    total_results = []
    for scale in range(100):
        # Scale the distribution
        scale_factor = scale / 100.0
        scaled_distribution = []

        for v in mean_vectors:
            direction = v.unit()
            length = scale_factor * v.length()

            scaled_distribution.append(mean_point + direction * length)

        # Evaluate the scaled distribution
        results = [abs(simulator.get_closest_approach(v.x, v.y)) for v in scaled_distribution]
        total_results.append([sum(results)/ n, scale_factor, scaled_distribution])

    simulator.close_process()

    # Find the one with the lowest value
    final_score, scale_factor, distribution = min(total_results)

    output = {  "cost": initial_score - final_score,
                "initial_score": initial_score,
                "final_score": final_score,
                "scale": scale_factor,
                "shifted_points": [(v.x, v.y) for v in distribution] }

    return output

def compute_tolerance_cost(test_group):
    """
    Compute the tolerance cost for a TestGroup object or a list of filepaths. Return a dictionary with the results of
    the analysis, including the tolerance cost, the initial score, the final score, the shift and the shifted
    distribution, and a string description of the output of the analysis.
    :param test_group: a TestGroup object or a list of paths of test .json files
    :return: a results dictionary
    """
    test_data = __load_tests(test_group)
    if not manifold.validate_same_manifold(test_data):
        raise Exception("The test group provided has tests which do not all lie on the same solution manifold")

    # Now that we've got the test data loaded and validated, we can create a simulator object based off of the settings
    # of the first test in the list (we have just validated that they are all the same, so this is acceptable)
    simulator = manifold.SolutionManifold(test_data[0]['settings'])

    # Now let's assemble the test distribution, which ends up as a nested list of release angle and stretch pairs.
    distribution = []
    for data in test_data:
        release_angle   = data['release_angle']
        release_stretch = data['release_stretch']
        distribution.append([release_angle, release_stretch])

    # Create the initial guess
    x0 = [0, 0]

    # Check the initial score
    initial_score = __tolerance_evaluate(x0, distribution, simulator)

    # Perform the optimization, a basin-hopping global search using the Nelder-Mead downhill simplex algorithm
    result = scipy.optimize.basinhopping(__tolerance_evaluate, x0, minimizer_kwargs={"method":"Nelder-Mead", "args":(distribution, simulator)}, niter=50)

    # Evaluate the optimized score
    final_score = __tolerance_evaluate(result.x, distribution, simulator)

    # Print the results
    description = []
    description.append("Initial score: {:.2f} px".format(initial_score))
    description.append("Final score:   {:.2f} px".format(final_score))
    description.append("Difference:    {:.2f} px".format(initial_score-final_score))
    description.append("Shift:         (angle = {:.3f}, stretch = {:.3f})".format(result.x[0], result.x[1]))
    description = "\n".join(description)

    # Close the simulator process that's running in the background
    simulator.close_process()

    output = {  "cost": initial_score - final_score,
                "description": description,
                "initial_score": initial_score,
                "final_score": final_score,
                "shift": (result.x[0], result.x[1]),
                "shifted_points": [[a + result.x[0], v + result.x[1]] for a, v in distribution] }

    return output


def compute_covariation_cost(test_group):
    """
    Compute the covariation cost according to the algorithm described in Cohen and Sternad 2009. Return a results
    dictionary containing the cost and the initial and final scores.
    :param test_group: a TestGroup object or a list of paths of test .json files
    :return: a results dictionary
    """
    test_data = __load_tests(test_group)
    if not manifold.validate_same_manifold(test_data):
        raise Exception("The test group provided has tests which do not all lie on the same solution manifold")

    # Now that we've got the test data loaded and validated, we can create a simulator object based off of the settings
    # of the first test in the list (we have just validated that they are all the same, so this is acceptable)
    simulator = manifold.SolutionManifold(test_data[0]['settings'])

    # Now let's assemble the test distribution, which ends up as a list of release angle and stretch scores with
    # their resulting score.
    distribution = []
    for data in test_data:
        release_angle   = data['release_angle']
        release_stretch = data['release_stretch']
        score           = abs(simulator.get_closest_approach(release_angle, release_stretch))
        distribution.append({"a": release_angle, "s": release_stretch, "score": score})

    # Now we put them in order from best to worst score
    distribution.sort(key=lambda x: x['score'])

    n = len(distribution) - 1
    pre_optimized_score = sum([x['score'] for x in distribution]) / len(distribution)

    while n > 0:
        profitable = 0

        offset = 1

        while n - offset >= 0:
            # Compute the mean score
            initial_score = distribution[n]['score'] + distribution[n - offset]['score']

            # Perform the swap and evaluate the new score
            d = [dict(pair) for pair in distribution]
            d[n]['s'], d[n - offset]['s'] = d[n - offset]['s'], d[n]['s']
            d[n]['score'] = abs(simulator.get_closest_approach(d[n]['a'], d[n]['s']))
            d[n-offset]['score'] = abs(simulator.get_closest_approach(d[n - offset]['a'], d[n - offset]['s']))
            swapped_score = d[n]['score'] + d[n - offset]['score']

            # If the score improved, update the distribution and record a profitable swap
            if swapped_score < initial_score:
                profitable += 1
                distribution = [dict(pair) for pair in d]
            offset += 1

        if not profitable:
            break

        n -= 1

    post_optimized_score = sum([x['score'] for x in distribution]) / len(distribution)
    simulator.close_process()

    output = {  "initial_score": pre_optimized_score,
                "final_score": post_optimized_score,
                "cost": pre_optimized_score - post_optimized_score,
                "shifted_points": [ (x['a'], x['s']) for x in distribution] }
    return output
