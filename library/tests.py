"""
    tests.py

    This module exists to aid in the management of tests files.  It functions as a primitive database management
    system in the selection of groups of test files from the data.
"""
import json
import datetime
import os

class TestLibrary:
    """
    The TestLibrary class serves as a primitive database management system, and aids in the selection, grouping, and
    filtering of test files.
    """
    library_path = None
    files = None

    def __init__(self, library_path):
        """
        :param library_path: the directory path that points at a folder full of test files
        :return: None
        """
        # Set the library path
        self.library_path = library_path
        if not os.path.exists(self.library_path):
            raise Exception("TestLibrary could not find the path '{}'".format(self.library_path))

        # Update the self.files list from the library
        self.update_library()

    def update_library(self):
        """
        Go through the library_path and find all test files and verify them
        :return:
        """
        file_objects = [os.path.join(self.library_path, item) for item in os.listdir(self.library_path) if item.endswith(".json")]

        # Validate the files
        validated = []
        for item in file_objects:
            if load_test_file(item) is not None:
                validated.append(item)

        self.files = validated

    def get_group(self):
        """
        Return a TestGroup of all files in this library
        """
        return TestGroup(self.files)

    def filter(self, filter_data):
        """
        Spawns a TestGroup and returns the filter of it.  A shortcut to filter.
        """
        return self.get_group().filter(filter_data)

class TestGroup:
    """
    The TestGroup class is a group of test files.  It is similar to the TestLibrary except that it is not bound to
    a particular directory on the disk.  Rather, the TestGroup manages a list of files which, as imagined, comes from
    one or more test libraries.  Test groups can be added together, filtered further (returning other TestGroup
    objects), sorted, and so on.  Analyses which are based on groups of tests should be written to handle TestGroups.
    """
    files = []

    def __init__(self, file_list = []):
        """
        :param file_list: optional list of file paths to initialize the test group
        """
        self.files = file_list

    def __add__(self, other):
        """
        TestGroups should be capable of being added together to join them.  The addition should make sure that no
        files are repeated.
        :param other: the other TestGroup object to be combined with this one
        :return: a new TestGroup object that is the join of the two
        """
        all_files = self.files + other.files

        # Use the fast method of searching out unique values
        uniques = {}
        for f in all_files:
            uniques[f] = None
        return TestGroup(uniques.keys())

    def get_list_of_key(self, key):
        """
        Return a list of a particular key from all of the test files, along with a second list containing the names
        of the filenames, such that zip() can combine the two into a list of tuples containing the attribute and the
        file from which it came.
        :param key: the key to aggregate
        :return: two lists, the first containing the assembled values, and the second containing the filenames
        """
        attributes = []
        filenames = []
        for item in self.files:
            data = load_test_file(item)
            if data is not None:
                if key in data.keys():
                    attributes.append(data[key])
                else:
                    attributes.append(None)
            filenames.append(item)
        return attributes, filenames

    def get_unique_list_of_key(self, key):
        """
        Return a unique list of a particular key from all of the test files.  This method uses get_list_of_key.
        :param key: the key to aggregate
        :return: a list of unique values
        """
        attributes, filenames = self.get_list_of_key(key)
        return list(set(attributes))

    def get_data_list(self):
        """
        Return a list of python dictionaries containing the data in the test group
        :return: list of python dictionaries
        """
        return [load_test_file(path) for path in self.files]

    def get_release_points(self):
        """
        Return a list of release angles and stretches
        :return: a list of 2-element lists containing the release angle and stretches
        """
        return [[r['release_angle'], r['release_stretch']] for r in self.get_data_list()]

    def filter(self, filter_data):
        """
        Simple filtering: use dictionary based filter to sort the existing elements in the group. The filter_data
        dictionary/dictionaries should be of the form:

            {   key1:value1, key2:value2  }

        The value can be a single value, in the case of a simple match, or a function which returns true or false based
         on the filter conditions.
        :param filter_data: a dictionary or list of dictionaries containing the filter items to match
        :return: a TestGroup of the items which passed the filter
        """
        if type(filter_data) is not dict:
            raise Exception("The filter_data argument must be a dictionary")

        reduced = list(self.files)
        for key, value in filter_data.items():

            subgroup = []
            if hasattr(value, '__call__'):
                # the sorting value is a callable object (a function) and should be used to evaluate the filter
                function = value
                for item in reduced:
                    data = load_test_file(item)
                    if data is not None:
                        if function(data[key]):
                            subgroup.append(item)
            else:
                for item in reduced:
                    data = load_test_file(item)
                    if data is not None:
                        if data[key] == value:
                            subgroup.append(item)
            reduced = list(subgroup)

        return TestGroup(reduced)

    def save_to_file(self, file_path):
        """
        Save the group to a zip file at file_path
        """
        # TODO: implement TestGroup.save_to_file()
        raise Exception("TestGroup.save_to_file() is not implemented yet")

    def load_from_file(self, file_path):
        """
        Load a group from a zip file at file_path
        """
        # TODO: implement TestGroup.load_from_file()
        raise Exception("TestGroup.load_from_file() is not implemented yet")

def load_test_file(filepath):
    """
    Given the path of a .json test file, load it, parse it to a test dictionary, and return it.  If the file does not
    appear to be a valid test (no 'settings', 'timestamp', or 'test_id' key) return None
    :param filepath: the filepath of the .json test file
    :return: a dictionary with the test data in it
    """
    if not os.path.exists(filepath):
        return None

    # Load the results from the json file
    with open(filepath, "r") as handle:
        contents = handle.read()
        results = json.loads(contents)

    # Validate that the three test keys are in the dictionary
    for valid_key in ['settings', 'timestamp', 'test_id']:
        if valid_key not in results.keys():
            return None

    # Convert the string timestamp into a python datetime object
    timestamp = datetime.datetime.strptime(results['timestamp'], "%H:%M:%S, %Y-%m-%d")
    results['timestamp'] = timestamp
    return results
