
import library.tests
import library.costs
import plot_manifold

import datetime

def main():

    # Load a test group of just Jarrad's tests
    tests = library.tests.TestLibrary("data")
    tests = tests.filter({"subject": "NM003"})

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

    point_sets = [
                    {'points': initial_points, 'color': 'b'},
                    {"points": final_points,   "color": "orange"}
                ]

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

    noise_results = library.costs.compute_noise_cost(tests)
    initial_points = tests.get_release_points()
    final_points = noise_results['shifted_points']

    point_sets = [
                    {"points": initial_points,   "color": "b"},
                    {"points": final_points,   "color": "green"}
                ]

    plot_manifold.plot(tests, "Noise Cost Shift", point_sets)
    print(
        noise_results["initial_score"]
    )
    print(
        noise_results["cost"]
    )

def main4():
    tests = library.tests.TestLibrary("data")

    noise_results = library.costs.compute_noise_cost(tests)
    covariation_results = library.costs.compute_covariation_cost(tests)
    tolerance_results = library.costs.compute_tolerance_cost(tests)

    print "Initial Score: ", noise_results['initial_score']
    print "Tolerance Cost: ", tolerance_results['cost']
    print "Noise Cost: ", noise_results['cost']
    print "Covariation Cost: ", covariation_results['cost']



    initial_points = tests.get_release_points()

    point_sets = [  {"points": initial_points, "color": "blue"},
                    {"points": noise_results['shifted_points'], "color": "red"},
                    {"points": covariation_results['shifted_points'], "color": "orange"},
                    {"points": tolerance_results['shifted_points'], "color": "green"},
                    ]
    plot_manifold.plot(tests, "Cost Shifts", point_sets)

def main5():
    tests = library.tests.TestLibrary("data")
    blocks = tests.break_into_blocks(datetime.timedelta(minutes=1))
    for block in blocks["NM006"]:
        first,second,third,fourth = block.split_into_parts(4)
        print "first quarter"
        first.print_summary()
        noise_results = library.costs.compute_noise_cost(first)
        covariation_results = library.costs.compute_covariation_cost(first)
        tolerance_results = library.costs.compute_tolerance_cost(first)
        print "Initial Score: ", noise_results['initial_score']
        print "Tolerance Cost: ", tolerance_results['cost']
        print "Noise Cost: ", noise_results['cost']
        print "Covariation Cost: ", covariation_results['cost']

        print ""

        print "second quarter"
        second.print_summary()
        noise_results = library.costs.compute_noise_cost(second)
        covariation_results = library.costs.compute_covariation_cost(second)
        tolerance_results = library.costs.compute_tolerance_cost(second)

        print "Initial Score: ", noise_results['initial_score']
        print "Tolerance Cost: ", tolerance_results['cost']
        print "Noise Cost: ", noise_results['cost']
        print "Covariation Cost: ", covariation_results['cost']

        print ""

        print "third quarter"
        third.print_summary()
        noise_results = library.costs.compute_noise_cost(third)
        covariation_results = library.costs.compute_covariation_cost(third)
        tolerance_results = library.costs.compute_tolerance_cost(third)

        print "Initial Score: ", noise_results['initial_score']
        print "Tolerance Cost: ", tolerance_results['cost']
        print "Noise Cost: ", noise_results['cost']
        print "Covariation Cost: ", covariation_results['cost']

        print ""

        print "fourth quarter"
        fourth.print_summary()
        noise_results = library.costs.compute_noise_cost(fourth)
        covariation_results = library.costs.compute_covariation_cost(fourth)
        tolerance_results = library.costs.compute_tolerance_cost(fourth)

        print "Initial Score: ", noise_results['initial_score']
        print "Tolerance Cost: ", tolerance_results['cost']
        print "Noise Cost: ", noise_results['cost']
        print "Covariation Cost: ", covariation_results['cost']

def main6():
    tests = library.tests.TestLibrary("data")
    blocks = tests.break_into_blocks(datetime.timedelta(minutes=5))
    for block in blocks["NM008"]:
        first,second = block.split_into_parts(2)
        print "first half"
        first.print_summary()
        noise_results = library.costs.compute_noise_cost(first)
        covariation_results = library.costs.compute_covariation_cost(first)
        tolerance_results = library.costs.compute_tolerance_cost(first)
        print "Initial Score: ", noise_results['initial_score']
        print "Tolerance Cost: ", tolerance_results['cost']
        print "Noise Cost: ", noise_results['cost']
        print "Covariation Cost: ", covariation_results['cost']

        print ""

        print "second quarter"
        second.print_summary()
        noise_results = library.costs.compute_noise_cost(second)
        covariation_results = library.costs.compute_covariation_cost(second)
        tolerance_results = library.costs.compute_tolerance_cost(second)

        print "Initial Score: ", noise_results['initial_score']
        print "Tolerance Cost: ", tolerance_results['cost']
        print "Noise Cost: ", noise_results['cost']
        print "Covariation Cost: ", covariation_results['cost']

if __name__ == "__main__":
    main4()