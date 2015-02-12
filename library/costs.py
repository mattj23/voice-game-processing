"""
    costs.py

    This module exists to compute the three cost measures (tolerance cost, noise cost, and covariation cost) of groups
    of tests.
"""

import manifold
import tests
import vector
import hashlib

import scipy.optimize
import numpy

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

def compute_tolerance_cost_sternad2009(test_group):
    """
    Using the method described in Sternad and Cohen 2009, compute the tolerance cost.  This involves the creation of
    a 500 x 500 grid and shifting the centroid of the manifold to each point on the grid, then checking the mean
    value of the distribution at that point and returning the lowest mean score.
    :param test_group: a TestGroup object with the tests to compute
    :return:
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

    # Now create a list of centroids to check
    settings = test_group.get_data_list()[0]['settings']

    angle_span = settings['AngleMaximum'] - settings['AngleMinimum']
    stretch_span = settings['StretchMaximum'] - settings['StretchMinimum']

    # TODO: Should this be bounded by the area in which the distribution will actually fit?
    angle_step = angle_span / 500.0
    stretch_step = stretch_span / 500.0

    angles = numpy.array(range(500)) * angle_step + settings['AngleMinimum']
    stretches = numpy.array(range(500)) * stretch_step + settings["StretchMinimum"]

    best_result = 0
    best_position = []
    best_distribution = []

    debug_output = []

    for a in angles:
        for s in stretches:
            local_value = abs(simulator.get_closest_approach(a, s))

            mean = vector.Vector(a, s, 0)
            distribution = [mean + v for v in mean_vectors]
            results = [abs(simulator.get_closest_approach(v.x, v.y)) for v in distribution]
            avg_result = sum(results) / n

            if avg_result < best_result or not best_position:
                best_position = [a, s]
                best_result = avg_result
                best_distribution = [(v.x, v.y) for v in distribution]

            debug_output.append("{}, {}, {}, {}".format(a, s, local_value, avg_result))
    final_score = best_result

    with open("debug.csv", "w") as handle:
        handle.write("\n".join(debug_output))

    # Print the results
    description = []
    description.append("Initial score: {:.2f} px".format(initial_score))
    description.append("Final score:   {:.2f} px".format(final_score))
    description.append("Difference:    {:.2f} px".format(initial_score-final_score))
    description.append("Shift:         (angle = {:.3f}, stretch = {:.3f})".format(best_position[0], best_position[1]))
    description = "\n".join(description)

    # Close the simulator process that's running in the background
    simulator.close_process()

    output = {  "cost": initial_score - final_score,
                "description": description,
                "initial_score": initial_score,
                "final_score": final_score,
                "shift": (best_position[0], best_position[1]),
                "shifted_points": best_distribution }

    return output

def compute_tolerance_cost_sternad2009_mod(test_group):
    """
    Using the method described in Sternad and Cohen 2009, compute the tolerance cost.  This involves the creation of
    a 500 x 500 grid and shifting the centroid of the manifold to each point on the grid, then checking the mean
    value of the distribution at that point and returning the lowest mean score.
    :param test_group: a TestGroup object with the tests to compute
    :return:
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

    # Now create a list of centroids to check
    settings = test_group.get_data_list()[0]['settings']
    search_points = __compute_search_points(simulator, settings, 4)


    best_result = 0
    best_position = []
    best_distribution = []

    for a, s in search_points:
        local_value = abs(simulator.get_closest_approach(a, s))

        mean = vector.Vector(a, s, 0)
        distribution = [mean + v for v in mean_vectors]
        results = [abs(simulator.get_closest_approach(v.x, v.y)) for v in distribution]
        avg_result = sum(results) / n

        if avg_result < best_result or not best_position:
            best_position = [a, s]
            best_result = avg_result
            best_distribution = [(v.x, v.y) for v in distribution]

    final_score = best_result


    # Print the results
    description = []
    description.append("Initial score: {:.2f} px".format(initial_score))
    description.append("Final score:   {:.2f} px".format(final_score))
    description.append("Difference:    {:.2f} px".format(initial_score-final_score))
    description.append("Shift:         (angle = {:.3f}, stretch = {:.3f})".format(best_position[0], best_position[1]))
    description = "\n".join(description)

    # Close the simulator process that's running in the background
    simulator.close_process()

    output = {  "cost": initial_score - final_score,
                "description": description,
                "initial_score": initial_score,
                "final_score": final_score,
                "shift": (best_position[0], best_position[1]),
                "shifted_points": best_distribution }

    return output

def false_manifold(test_group):
    """
    Make a much lower resolution manifold
    :param test_group:
    :return:
    """
    test_data = __load_tests(test_group)
    if not manifold.validate_same_manifold(test_data):
        raise Exception("The test group provided has tests which do not all lie on the same solution manifold")

    # Now that we've got the test data loaded and validated, we can create a simulator object based off of the settings
    # of the first test in the list (we have just validated that they are all the same, so this is acceptable)
    simulator = manifold.SolutionManifold(test_data[0]['settings'])
    grid_steps = 100

    # Now create a starting point grid
    settings = test_group.get_data_list()[0]['settings']
    angle_span = settings['AngleMaximum'] - settings['AngleMinimum']
    stretch_span = settings['StretchMaximum'] - settings['StretchMinimum']


    angle_step = angle_span / grid_steps
    stretch_step = stretch_span / grid_steps

    angles = numpy.array(range(grid_steps)) * angle_step + settings['AngleMinimum']
    stretches = numpy.array(range(grid_steps)) * stretch_step + settings["StretchMinimum"]

    table = []

    for a in angles:
        row = []
        for s in stretches:
            value = simulator.get_closest_approach(a, s)
            row.append(abs(value))
        table.append(row)

    rendered = []
    for row in table:
        threshold = 50
        new_row = []
        for cell in row:
            if cell > threshold:
                new_row.append("-")
            else:
                new_row.append("0")
        rendered.append("".join(new_row))


    simulator.close_process()

    return "\n".join(rendered)

def __hash_point(x, y):
    engine = hashlib.sha1()
    engine.update("{:.4f}{:.4f}".format(x,y))
    return engine.hexdigest()

def __compute_search_points(simulator, settings, iterations=4):
    """
    Compute the search points for a manifold
    :param simulator:
    :param settings:
    :return:
    """
    threshold = 30

    grid_steps = 50
    angle_span = settings['AngleMaximum'] - settings['AngleMinimum']
    stretch_span = settings['StretchMaximum'] - settings['StretchMinimum']
    angle_step = angle_span / grid_steps
    stretch_step = stretch_span / grid_steps

    angles = numpy.array(range(grid_steps)) * angle_step + settings['AngleMinimum']
    stretches = numpy.array(range(grid_steps)) * stretch_step + settings["StretchMinimum"]

    search_points = {}

    for a in angles:
        for s in stretches:
            value = simulator.get_closest_approach(a, s)
            if abs(value) < threshold:
                search_points[__hash_point(a, s)] = (a,s)

    for i in range(iterations):
        angle_step *= 0.5
        stretch_step *= 0.5

        for k, v in search_points.items():
            a, s = v

            px, py = a + angle_step, s
            search_points[__hash_point(px, py)] = (px, py)

            px, py = a, s + stretch_step
            search_points[__hash_point(px, py)] = (px, py)

            px, py = a + angle_step, s + stretch_step
            search_points[__hash_point(px, py)] = (px, py)

            px, py = a - angle_step, s
            search_points[__hash_point(px, py)] = (px, py)

            px, py = a, s - stretch_step
            search_points[__hash_point(px, py)] = (px, py)

            px, py = a - angle_step, s - stretch_step
            search_points[__hash_point(px, py)] = (px, py)

    all_points = [v for k, v in search_points.items()]

    final = []
    for a, s in all_points:
        value = abs(simulator.get_closest_approach(a, s))
        if value <= threshold:
            final.append((a,s))

    return final

def __compute_search_points_brute(simulator, settings):
    """
    Compute the search points for a manifold
    :param simulator:
    :param settings:
    :return:
    """
    threshold = 30

    grid_steps = 1000
    angle_span = settings['AngleMaximum'] - settings['AngleMinimum']
    stretch_span = settings['StretchMaximum'] - settings['StretchMinimum']
    angle_step = angle_span / grid_steps
    stretch_step = stretch_span / grid_steps

    angles = numpy.array(range(grid_steps)) * angle_step + settings['AngleMinimum']
    stretches = numpy.array(range(grid_steps)) * stretch_step + settings["StretchMinimum"]

    search_points = []

    for a in angles:
        for s in stretches:
            value = simulator.get_closest_approach(a, s)
            if abs(value) < threshold:
                search_points.append([a, s])

    return search_points

def compute_tolerance_cost_test(test_group):
    """
    Intelligent search for global minima based on what we know about the shape of the solution manifolds.  Uses a low
    resolution rendering of the solution manifold to determine a small number of intelligent starting points for a local
    minimization search.
    :param test_group:
    :return:
    """
    test_data = __load_tests(test_group)
    if not manifold.validate_same_manifold(test_data):
        raise Exception("The test group provided has tests which do not all lie on the same solution manifold")

    # Now that we've got the test data loaded and validated, we can create a simulator object based off of the settings
    # of the first test in the list (we have just validated that they are all the same, so this is acceptable)
    simulator = manifold.SolutionManifold(test_data[0]['settings'])


    x = __compute_search_points(simulator, test_data[0]['settings'])
    print len(x)
    print x[0]


    # Close the simulator process that's running in the background
    simulator.close_process()


def compute_tolerance_cost_intelligent(test_group):
    """
    Intelligent search for global minima based on what we know about the shape of the solution manifolds.  Uses a low
    resolution rendering of the solution manifold to determine a small number of intelligent starting points for a local
    minimization search.
    :param test_group:
    :return:
    """
    test_data = __load_tests(test_group)
    if not manifold.validate_same_manifold(test_data):
        raise Exception("The test group provided has tests which do not all lie on the same solution manifold")

    # Now that we've got the test data loaded and validated, we can create a simulator object based off of the settings
    # of the first test in the list (we have just validated that they are all the same, so this is acceptable)
    simulator = manifold.SolutionManifold(test_data[0]['settings'])

    # Now create a starting point grid
    settings = test_group.get_data_list()[0]['settings']
    search_points = __compute_search_points(simulator, settings, 0)

    # Now perform local searches at each of the search points
    # Find the mean point in the test group
    release_points = []
    for data in test_data:
        release_points.append(vector.Vector(data['release_angle'], data['release_stretch'], 0))
    n = len(release_points)
    mean_point = vector.get_average_point(release_points)

    distribution = [[v.x, v.y] for v in release_points]

    # Get the initial score
    results = [abs(simulator.get_closest_approach(a, s)) for a, s in distribution]
    initial_score = sum(results) / n

    best_result = 0
    best_position = []
    best_distribution = []

    for a, s in search_points:

        ra = a - mean_point.x
        rs = s - mean_point.y

        result = scipy.optimize.minimize(__tolerance_evaluate, [ra, rs], method="Nelder-Mead", args=(distribution, simulator))
        avg_result = __tolerance_evaluate(result.x, distribution, simulator)

        if avg_result < best_result or not best_position:
            best_position = [ra, rs]
            best_result = avg_result
            best_distribution = [[x + result.x[0], y + result.x[1]] for x, y in distribution]

    final_score = best_result

    # Print the results
    description = []
    description.append("Initial score: {:.2f} px".format(initial_score))
    description.append("Final score:   {:.2f} px".format(final_score))
    description.append("Difference:    {:.2f} px".format(initial_score-final_score))
    description.append("Shift:         (angle = {:.3f}, stretch = {:.3f})".format(best_position[0], best_position[1]))
    description = "\n".join(description)

    # Close the simulator process that's running in the background
    simulator.close_process()

    output = {  "cost": initial_score - final_score,
                "description": description,
                "initial_score": initial_score,
                "final_score": final_score,
                "shift": (best_position[0], best_position[1]),
                "shifted_points": best_distribution }

    return output

def compute_tolerance_cost_hybrid(test_group):
    """
    Using a local search that is repeated at a number of starting grid points, compute the tolerance cost
    :return:
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

    # Get the initial score
    n = len(distribution)
    results = [abs(simulator.get_closest_approach(a, s)) for a, s in distribution]
    initial_score = sum(results) / n


    # Now create a starting point grid
    settings = test_group.get_data_list()[0]['settings']
    angle_span = settings['AngleMaximum'] - settings['AngleMinimum']
    stretch_span = settings['StretchMaximum'] - settings['StretchMinimum']

    grid_steps = 50

    angle_step = angle_span / grid_steps
    stretch_step = stretch_span / grid_steps

    angles = numpy.array(range(grid_steps)) * angle_step + settings['AngleMinimum']
    stretches = numpy.array(range(grid_steps)) * stretch_step + settings["StretchMinimum"]

    best_result = 0
    best_position = []
    best_distribution = []

    for a in angles:
        for s in stretches:

            x0 = [a, s]
            result = scipy.optimize.minimize(__tolerance_evaluate, x0, method="Nelder-Mead", args=(distribution, simulator))
            avg_result = __tolerance_evaluate(result.x, distribution, simulator)

            if avg_result < best_result or not best_position:
                best_position = [a, s]
                best_result = avg_result
                best_distribution = [[x + result.x[0], y + result.x[1]] for x, y in distribution]

    final_score = best_result

    # Print the results
    description = []
    description.append("Initial score: {:.2f} px".format(initial_score))
    description.append("Final score:   {:.2f} px".format(final_score))
    description.append("Difference:    {:.2f} px".format(initial_score-final_score))
    description.append("Shift:         (angle = {:.3f}, stretch = {:.3f})".format(best_position[0], best_position[1]))
    description = "\n".join(description)

    # Close the simulator process that's running in the background
    simulator.close_process()

    output = {  "cost": initial_score - final_score,
                "description": description,
                "initial_score": initial_score,
                "final_score": final_score,
                "shift": (best_position[0], best_position[1]),
                "shifted_points": best_distribution }

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


def compute_tolerance_cost_local(test_group):
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
    result = scipy.optimize.minimize(__tolerance_evaluate, x0, method="Powell", args=(distribution, simulator))
    #result = scipy.optimize.basinhopping(__tolerance_evaluate, x0, minimizer_kwargs={"method":"Nelder-Mead", "args":(distribution, simulator)}, niter=50)

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
