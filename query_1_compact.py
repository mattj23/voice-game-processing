"""
    Query #1, Compact

    This program does the exact same thing as query_1.py, but it is written
    compactly and efficiently for the purpose of demonstrating how the same
    thing can be accomplished in python without the same verbosity.

    Matt Jarvis, 09/24/2014


"""

import os       
import json     
import datetime 

def load_test_file(filepath): 
    with open(filepath, "r") as handle:
        results = json.loads(handle.read())
    results['timestamp'] = datetime.datetime.strptime(results['timestamp'], "%H:%M:%S, %Y-%m-%d")
    return results

def format_output_row(testInfo, headers):
    return ", ".join(["{"+header+"}" for header in headers]).format(**testInfo)

def main():
    
    testFiles = [os.path.join("Data", item) for item in os.listdir("Data")]
    tests     = [load_test_file(path) for path in testFiles]    
    subjects  = set([test['subject'] for test in tests])


    for subject in subjects:
        subjectTests = [test for test in tests if test['subject'] == subject]
        subjectTests.sort(key = lambda x: x['timestamp'])

        columns = ["timestamp", "starting_pitch", "starting_volume", "closest_approach", "outcome"]
        output = [", ".join(columns)] + [format_output_row(test, columns) for test in subjectTests]
        outputFileName = "{} Test History.csv".format(subject)
        with open(outputFileName, "w") as handle:
            handle.write("\n".join(output))
            

if __name__ == '__main__':
    main()