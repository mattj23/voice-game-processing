
import library.tests
import library.costs

def main():
    print "Loading library..."

    tests = library.tests.TestLibrary("data")
    tests = tests.filter({"subject": "Jarrad"})


    results = library.costs.compute_tolerance_cost(tests)
    print results



if __name__ == "__main__":
    main()