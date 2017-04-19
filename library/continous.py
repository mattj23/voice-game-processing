import json
import library.costs

class ContinousGroup:
    """
    Should emulate the important parts of the TestGroup
    """

    def __init__(self, file_name):
        self.file_name = file_name
        with open(file_name, "r") as handle:
            self.data = json.loads(handle.read())

    def prepare_for_costs(self):
        list_of_tests = []
        for element in self.data['trace']:
            new_item = dict(self.data)
            list_of_tests.append(new_item)
        return list_of_tests

def main():
    x = ContinousGroup("data/20170412_AM/Test 2017-04-12_16-40-31.json")
    results = library.costs.compute_tolerance_cost(x)
if __name__ == '__main__':
    main()