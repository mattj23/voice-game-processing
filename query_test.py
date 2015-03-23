
import library.tests
import library.costs
import plot_manifold
import time
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
    # plot_manifold.plot(tests, "Tolerance Cost Shift", point_sets)
    print tolerance_results
    # And other stuff`

def main2():
    tests = library.tests.TestLibrary("data")

    covariation_results = library.costs.compute_covariation_cost(tests)
    initial_points = tests.get_release_points()
    final_points = covariation_results['shifted_points']

    point_sets = [  {"points": initial_points, "color": "b"},
                    {"points": final_points, "color": "r"}]

    plot_manifold.plot(tests, "Covariation Cost Shift", point_sets)


def main3():

    # Load a test group of just Jarrad's tests
    tests = library.tests.TestLibrary("data")
    tests = tests.filter({"subject": "Jarrad"})
    print "starting"
    for i in range(50):
        start = time.time()
        # Compute the tolerance cost and capture the results
        tolerance_results = library.costs.compute_tolerance_cost(tests)
        output =  "trial {}, {} seconds, initial = {}, final = {}, result = {}".format(i, time.time() - start, tolerance_results['initial_score'], tolerance_results['final_score'], tolerance_results['cost'])

        with open("sternad2009.txt", "a") as handle:
            handle.write(output)
            handle.write("\n")

        print output 
    print "done"

def main4():
	# Load a test group of just Jarrad's tests
    tests = library.tests.TestLibrary("data")
    tests = tests.filter({"subject": "Jarrad"})

    start = time.time()
    table = library.costs.compute_tolerance_cost(tests)

    print "{} s".format(time.time() - start)

if __name__ == "__main__":
    main3()