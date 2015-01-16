
import library.tests
import library.costs
import plot_manifold


def main():

    # Load a test group of just Jarrad's tests
    tests = library.tests.TestLibrary("data")
    tests = tests.filter({"subject": "Jarrad"})

    # Compute the tolerance cost and capture the results
    tolerance_results = library.costs.compute_tolerance_cost(tests)

    # Prepare the initial points for the plotting
    initial_points = tests.get_release_points()

    # Prepare the shifted points for the plotting
    x, y = tolerance_results['shift']
    final_points = [(a + x, v + y) for a, v in initial_points]

    # Prepare a list of dictionaries with the point sets and the colors to plot
    point_sets = [
                    {'points': initial_points, 'color': 'b'},
                    {"points": final_points,   "color": "r"}
                ]

    # Plot the manifold and the two point sets
    plot_manifold.plot(tests, "Tolerance Cost Shift", point_sets)


if __name__ == "__main__":
    main()