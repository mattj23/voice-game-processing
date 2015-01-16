voice-game-processing

This project contains the processing code for working with the results of the vocal motor learning game.  Written
almost exclusively in Python, the code does use a few 64 bit Windows binaries (written in C#) to do things like
simulate the outcome of a game trial, or use parallel threads to speed up the computation of large solution manifolds.

Raw data and installation
=========================
    
    The processing project is designed to be pointable at any repository of test files through the use of the
    TestLibrary object in the library.tests module.  This means that you can have a folder (or many folders) full of
    test result files (in the .json format) and access these files by instancing a TestLibrary object and pointing it at
    that folder. As a result there isn't really a necessary convention as far as location for storing data files, but
    for the sake of the development queries we've been placing them in a folder located at voice-game-processing/data


Library code
============

    In the voice-game-processing folder there is a Python package called "library" which contains several helper modules
    to aid with various parts of the analysis.  They exist to simplify complex tasks and allow general analysis code to
    be written at a very abstract, high level without worrying about the implementation details.

    library.tests
    =============

        The library.tests module exists to help locate, sort, filter, and manage large volumes of test files.  Think of
        this module as serving some of the same functions as a primitive NoSQL database management system similar to a
        heavily watered down version of MongoDB.

        There are two main classes in library.tests: TestGroup and TestLibrary.  TestLibrary is a child class of
        TestGroup, and so has access to the same methods as TestGroup, but has a slightly different purpose...creating
        an original "source" of test data.

        Intended Usage Example:
        =======================
        The intended usage of TestLibrary and TestGroup in a piece of analysis code or a query is as follows:

            * First, you would create a TestLibrary and point it at a folder full of test .json files

                source = library.tests.TestLibrary("path/to/data")

            * Next you might filter it down.  For example, the following code produces a TestGroup that contains only
              hits from the subject "Alice"

                group1 = source.filter( {"subject": "Alice", "outcome": "hit"} )

            * You might then produce another group, for instance, one which contains the obstacle impacts from "Alice"

                group2 = source.filter( {"subject": "Alice", "outcome": "obstacle"} )

            * You might combine these two groups to create a group containing Alice's hits and misses

                combined = group1 + group2

            * Finally, using the combined group, you would begin your analysis.  In this example, you might perform a
              tolerance cost analysis on the combined group

                result = library.costs.compute_tolerance_cost( combined )

        TestLibrary Class
        =================

        A TestLibrary class is instanced with a path to a folder full of test classes.  It internally creates a list of
        all the test files in that folder. Because the TestLibrary class inherits from the TestGroup class, you can
        perform any of the filtering/summarizing/grouping functions which exist in that class.  However, the object
        which results from those methods will be a TestGroup, not a TestLibrary.  This difference currently has little
        effect.

        Instancing a TestLibrary:

            # You can use either a relative path...
            test_source = library.tests.TestLibrary("data/example/path")

            # ...or an absolute path
            test_source = library.tests.TestLibrary("C:/absolute/example/path")

        Once a TestLibrary is created, you can use it just like you would a TestGroup

        TestGroup Class
        ===============

        A TestGroup class is, quite simply, a group of tests stored in a single object.  For the most part the TestGroup
        class only tracks the paths to the file, so the full data from the tests is not all loaded into memory at any
        given time.  This is for memory considerations, but it also means that when performing operations which require
        a peek at the data inside the tests (like filtering), the TestGroup must perform a time-consuming disk access
        operation for every file in the list.

        The main purpose of a TestGroup is to be a convenient object which handles sets of tests and allows combining,
        filtering, sorting, and partitioning of sets as well as being a form which can be passed directly to analysis
        code.

        Class Constructor:  TestGroup(file_list=[])
        ===========================================

            The TestGroup class constructor is rarely used directly in analysis code, but an optional argument
            "file_list" can be included which contains a list of file paths of test result files.  Otherwise an empty
            TestGroup is created, which isn't much use for anyone.

        Addition Operator:  TestGroup.__add__
        =====================================
        
            TestGroups can be combined through the addition operator "+".  The addition operation will produce the union
            of two TestGroup objects, with redundant tests eliminated.

            group1 = library.tests.TestGroup([...list of files...])
            group2 = library.tests.TestGroup([...list of files...])

            combined = group1 + group2

        Get List of Attributes: TestGroup.get_list_of_key(key)
        ======================================================

            In order to extract a list of the values of a specific key for every test in the TestGroup, you can use the
            get_list_of_key method, providing the key of interest as an argument. The result will be two identically
            sized list, where the i-th element of the first list is the key value of that test, and the i-th element of
            the second list is the filename of the test which corresponds with the value in the first list.

            For example:

                group = library.tests.TestLibrary("path/to/data")   # Remember that TestLibrarys are TestGroups too
                attributes, filenames = group.get_list_of_key("subject")

            will return two lists:

                attributes = ["Alice", "Bob", "Bob", "Alice", "Bob"]
                filenames  = ["test1.json", "test2.json", "test3.json", "test4.json", "test5.json"]

            They can be assembled into tuple pairs with Python's zip function:

                pairs = zip(attributes, filenames)

                # produces something that looks like this:
                # [ ("Alice", "test1.json"), ("Bob", "test2.json"), ("Bob", "test3.json") ... ]

            If you want just the attributes, you can use the index operator

                attributes = group.get_list_of_key("subject")[0]

        Get Unique List of Attributes: TestGroup.get_unique_list_of_key(key)
        ====================================================================

            Getting a unique list of keys is useful for operations where you might want to answer a question like "which
            subjects are in this group?"

            The key provided must index a value which is a hashable result, like a string, an integer, or a tuple.  The
            data is returned as list of the results.

            For example:

                group = library.tests.TestLibrary("path/to/data")
                subjects = group.get_unique_list_of_keys("subject")

            Might create a "subjects" that looks something like this:

                ["Alice", "Bob", "Carol"]

            ...even if there are 10 tests with Alice, 30 with Bob, and 2 with Carol.

        Getting the raw data dictionaries: TestGroup.get_data_list()
        ============================================================

            The contents of the test .json files are essentially python dictionaries which contain all of the data from
            the tests.  In certain cases we need to access this data directly, and in such a case we can use the
            get_data_list method to extract a list of the dictionaries and have them in their native python form all
            loaded simultaneously into memory.  The reason that we do not store the data in the TestGroup in this form
            under normal circumstances is that, in the case of a very large TestGroup, such a scheme could require a lot
            of memory.  As such be careful using this method with very large TestGroups.

            For example:

                group = library.tests.TestLibrary("path/to/data")
                data  = group.get_data_list()

            Will produce a "data" that looks something like this:

                [   {"test_id":#####, "subject":"Alice", "settings":{...}},
                    {"test_id":#####, "subject":"Bob", "settings":{...}},
                    {"test_id":#####, "subject":"Bob", "settings":{...}},  ...]

        Getting the release angle and stretch pairs: TestGroup.get_release_points()
        ===========================================================================

            This method will extract the release angle and release stretch pairs as a list of tuples.

            For example:

                pairs = group.get_release_points()

            will produce a "pairs" that looks like:

                [   (a1, v1), (a2, v2), (a3, v3) ... (an, vn)   ]

            These can be separated into lists of angles and stretches with Python's zip function

                angles, stretches = zip(*pairs)     # make sure to include the * operator here

            which will produce two lists that look as follows:

                angles    = [a1, a2, a3, ... an]
                stretches = [v1, v2, v3, ... vn]

        Filtering groups of tests: TestGroup.filter(filter_data)
        ========================================================

            This method produces filtering similar to the way MongoDB does.  A query dictionary (filter_data) is
            produced and matched against all elements in the TestGroup.  The tests which pass the filter are added to a
            reduced set and returned as a new TestGroup.

            Simple comparisons are done by providing a dictionary where the key-value pairs are elements to directly
            match values in the test dictionary.  For example, a key "subject" with a value of "Alice" would go through
            each test in the TestGroup and only return tests where the "subject" key returned a value equal to "Alice".

            Filtering on a single key:

                # The following will produce a TestGroup composed only of Bob's tests
                source = library.tests.TestLibrary("path/to/data")
                group  = source.filter( {"subject":"Bob"} )

            Filtering on multiple keys:

                # The following will produce a TestGroup composed only of Bob's misses
                source = library.tests.TestLibrary("path/to/data")
                group  = source.filter( {"subject":"Bob", "outcome":"miss"} )

            Complex comparisons like "less than", "greater than", and 'within range of' can be done by passing the
            filter_data a callable object (a function) instead of a simple value.  The filter method will plug the test
            value that matches the given key into the function you provide in filter_data and check whether or not the
            result evaluates to True.  If it does, the test passes the filter and is added to the TestGroup returned by
            the function.

            For example, a simple callable here can isolate tests in which the closest point of approach is less than 10
            pixels:

                def my_filter(x):
                    if abs(x) < 10:
                        return True
                    else:
                        return False
                
                source = library.tests.TestLibrary("path/to/data")
                group  = source.filter( {"closest_approach":my_filter } )

            An identical result can be achieved with Python's lambda function definitions:

                source = library.tests.TestLibrary("path/to/data")
                group  = source.filter( {"closest_approach":lambda x : abs(x) < 10 } )

            A more complex query here can be used to isolate tests in which the starting pitch was between 100Hz and
            200Hz:

                group  = source.filter( {"starting_pitch":lambda x : x > 100 and x < 200 } )

            Finally, don't forget that multiple conditions can be combined, and the filter_data dictionary can be built
            externally from the function call.  The following filter returns all of Alice's hits where the stretch was
            less than 0.8:

                conditions = {
                            "subject": "Alice",
                            "outcome": "hit",
                            "release_stretch": lambda x: x < 0.8
                }
                group = source.filter(conditions)

        Break into test blocks: TestGroup.break_into_blocks(time_delay)
        ===============================================================

            Often it is desirable to break a bulk jumble of test files into organized blocks, where a block is defined
            as a set of consecutive tests performed by a single person with no time delay between tests greater than a
            certain amount.

            For example, if Alice does 30 consecutive tests, takes a 2 hour break, and does another 15 tests, while Bob
            does 45 tests, takes a 3 day break, and then does 10 tests, we have four total blocks: two done by Alice of
            30 and 15 trials, and two done by Bob of 45 and 10 trials.

            If all of these test files are in a single directory, they can be loaded and broken into their blocks with
            the break_into_blocks method.

            For example, in the above case:

                source = library.tests.TestLibrary("path/to/data")
                blocks = source.break_into_blocks()

            will produce a "blocks" which looks like this:

                {
                    "Alice": [AliceTestGroup1, AliceTestGroup2],
                    "Bob": [BobTestGroup1, BobTestGroup2]
                }

            ...in which AliceTestGroup1 is a TestGroup object with 30 tests in it, AliceTestGroup2 is a TestGroup object
            with 15 tests in it, and so on.

            By default the break_into_blocks method uses a max adjacency delay of 10 minutes, but this can be specified
            by the user.  For example, breaking into blocks with a 10 second max delay would look like this:

                blocks = source.break_into_blocks(datetime.timedelta(seconds=10))   # remember to import datetime

            A two day, twenty second delay would look like this:

                blocks = source.break_into_blocks(datetime.timedelta(days=2, seconds=20))

        Getting a summary of the test group: TestGroup.summarize() and TestGroup.print_summary()
        ========================================================================================

            These two methods are meant to make the process of exploring and filtering data a bit easier.  The
            summarize() method returns a dictionary with a few summary statistics of the TestGroup and the
            print_summary() method prints these statistics to the screen in an organized, formatted way.

            For example:

                source = library.tests.TestLibrary("path/to/data")
                summary = source.summarize()

            will produce a "summary" that looks like this:
                
                {   
                    'count': 25, 
                    'hits': 7, 
                    'timespan': '1 minute, 3 seconds', 
                    'obstacles': 0, 
                    'misses': 18, 
                    'subjects': [u'Jarrad'] 
                }

            while this:

                source.print_summary()

            will produce output on the console that looks like this:

                Group Summary:
                  Subjects:      1
                                 Jarrad
                  Trials:        25
                  Hits:          7
                  Misses:        18
                  Obstacles:     0
                  Time span:     1 minute, 3 seconds

