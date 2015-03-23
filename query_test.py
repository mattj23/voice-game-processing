
import library.tests
import library.costs
import plot_manifold

import datetime

def main():

    # Load a test group of just Jarrad's tests
    tests = library.tests.TestLibrary("data")
    tests = tests.filter({"subject": "Jarrad"})

    # Compute the tolerance cost and capture the results
    tolerance_results = library.costs.compute_tolerance_cost(tests)

    # Prepare the initial points for the plotting
    initial_points = tests.get_release_points()

    # Prepare the shifted points for the plotting
    final_points = tolerance_results['shifted_points']

    # Prepare a list of dictionaries with the point sets and the colors to plot
    point_sets = [
                    {'points': initial_points, 'color': 'b'},
                    {"points": final_points,   "color": "r"}
                ]

    # Plot the manifold and the two point sets
    plot_manifold.plot(tests, "Tolerance Cost Shift", point_sets)
    print(
        tolerance_results["description"]
    )

    # And other stuff

def main2():
    tests = library.tests.TestLibrary("data")

    covariation_results = library.costs.compute_covariation_cost(tests)
    initial_points = tests.get_release_points()
    final_points = covariation_results['shifted_points']

    point_sets = [  {"points": initial_points, "color": "b"},
                    {"points": final_points, "color": "r"}]

    plot_manifold.plot(tests, "Covariation Cost Shift", point_sets)
    print(
        covariation_results["initial_score"]
    )
    print(
        covariation_results["final_score"]
    )
    print(
        covariation_results["cost"]
    )

def main3():
    tests = library.tests.TestLibrary("data")

    noise_results = library.costs.compute_noise_cost(tests)
    initial_points = tests.get_release_points()
    final_points = noise_results['shifted_points']

    point_sets = [  {"points": initial_points, "color": "b"},
                    {"points": final_points, "color": "r"}]

    plot_manifold.plot(tests, "Noise Cost Shift", point_sets)
    print(
        noise_results["initial_score"]
    )
    print(
        noise_results["final_score"]
    )
    print(
        noise_results["cost"]
    )

if __name__ == "__main__":
    main()