
import library.tests


def main():
    print "Loading library..."

    tests = library.tests.TestLibrary("data")

    results = tests.filter({"subject": "Jarrad"})

    for result in results:
        print result


if __name__ == "__main__":
    main()