"""
    Query #1

    For all given users, plot the error over successive trials.

    ----------------------------------------------------------------------------

    This is a very simple, somewhat naieve query in the sense that it does not
    automatically take into account the parameters which would change the
    physics (and thus the difficulty) of the problem.  Future queries should
    remedy this by checking to make sure that error is only compared between
    tests which had identical testing conditions.

    The query performs the following steps:

        1. Using python's built in OS module, locate all of the available test
           result sets in the "Data" subfolder

        2. Loop through every test and load/parse it using python's built in
           json parsing module

        3. Identify the unique test subjects by name

        4. Loop through each test subject and isolate and sort their tests

        5. For each test subject, create a csv file with the test number and the
           error

    ----------------------------------------------------------------------------

    Matt Jarvis, 09/24/2014


"""

# Here at the beginning of the program we load any python modules that we want
# to use later on. It isn't strictly necessary to do things in this order, but
# it helps with the overall organization and readability, and it prevents you
# from importing the same module twice.

import os       # We use the operating system module for file handling
import json     # This is the json parsing library, it makes reading json easy
import datetime 

# Jarrad, python is a full featured, object-oriented programming language and
# can take advantage of all the wonderful things that modern programming
# languages have to offer. Starting out on the simple side, I've written
# reusable blocks of code which I've packaged into functions that I can call
# later, or potentially from other queries.  This saves an enormous amount of
# time, effort, and uncertainty in the long run.  It does, however, make the
# structure of a program less linear, which takes a little getting used to.

def load_test_file(filepath): 
    """ Given the file path of a .json test file, open that test file and use
    the json module to parse the contents into a results dictionary, then return
    it from the function.
    """
    with open(filepath, "r") as handle:
        contents = handle.read()
        results  = json.loads(contents)

    # Convert the string timestamp into a python datetime object 
    timestamp = datetime.datetime.strptime(results['timestamp'], "%H:%M:%S, %Y-%m-%d")
    results['timestamp'] = timestamp
    return results

def format_output_row(testInfo, headers):
    """ Given a test result dictionary (testInfo) and a list of string headers,
    prepare and format a comma separated output string containing the test data
    reformatted as if the header strings were columns. """
    keys = []
    for header in headers:
        keys.append( "{" + header + "}" )
    keyString = ", ".join(keys)
    return keyString.format(**testInfo)

# It isn't necessary to organize a program this way, but it opens up a wide
# array of very powerful possibilities down the road to do so.  Python reads the
# file from top to bottom.  Most statements will get evaluated as they are read,
# but function defintions (like these 'def' statements) don't get evaluated, but
# rather their code is packaged into a reusable block that's saved for later.

# By defining an intended "main" function that only gets called when this python
# program is run directly, it allows you to use this program as a module in
# another program later.  Thus you could be writing query_3.py and import the
# tools and functions you wrote in query_1 without having to copy/paste or
# rewrite them.

# That's what I've done here.  The "main" function is where the program will
# start unless it's been loaded as a module, in which case the other program
# will decide what gets run and what doesn't.  But for now, think of the
# "main()" function as where the program starts.

def main():
    
    # Program starts here, gather the names of all the available test files from
    # the "Data" folder
    data_folder = r"C:\Users\Jarrad\Desktop\Master Research Folder\Projects\Voice Throwing Game\Data\NF003\Day 1\Filtered"
    testFiles = os.listdir(data_folder)

    # Load all of the tests into one big list. I've written this in a very
    # deliberate, explict way.  We loop through the list of test file names,
    # join it with the name of the folder it's in, load the test data using the
    # load_test_data() function I defined above, and then add it to a new list
    # of raw test data.
    tests = []
    for filename in testFiles:
        path = os.path.join(data_folder, filename)
        testData = load_test_file(path)
        tests.append(testData)

    # Let's find the names of all of the test subjects. I go through each test
    # we've loaded and add the value of the 'subject' field to a list.  Then I
    # convert the list into a set (a datatype that can only hold unique
    # elements) to find the names of all of the test subjects.
    subjects = []
    for test in tests:
        subjects.append(test['subject'])
    subjects = set(subjects)


    for subject in subjects:
        # Create a list of tests for this subject
        subjectTests = []
        for test in tests:
            if test['subject'] == subject:
                subjectTests.append(test)

        # Sort this subject's tests by the timestamp
        subjectTests.sort(key = lambda x: x['timestamp'])

        # Determine the columns we're interested in
        columns = ["timestamp", "starting_pitch", "starting_volume", "closest_approach", "outcome"]

        # The output list is a list of strings which each will be a row in the
        # output csv file. Eventually it will be joined with line breaks and
        # written to file.
        output = [ ", ".join(columns) ]     # The output list starts with the column headers
        for test in subjectTests:
            output.append(format_output_row(test, columns))

        # Create an output file and write to it
        outputFileName = "{} Test History.csv".format(subject)
        with open(outputFileName, "w") as handle:
            handle.write("\n".join(output))
            

# Disregard this for now.  It's the little bit of magic that makes sure that
# main() is only run if this program is run directly, and not when this program
# is loaded as a code module.
if __name__ == '__main__':
    main()