import json

import math

import library.costs

class ContinuousGroup:
    """
    Should emulate the important parts of the TestGroup
    """

    def __init__(self, file_name):
        self.file_name = file_name
        with open(file_name, "r") as handle:
            self.data = json.loads(handle.read())

        self.list_of_tests = []
        for tick, frequency, decibels, closest_approach in self.data['trace']:
            new_item = dict(self.data)
            new_item['release_angle'] = self.get_angle(frequency)
            new_item['release_stretch'] = self.get_stretch(decibels)
            self.list_of_tests.append(new_item)

    def prepare_for_costs(self):
        return self.list_of_tests

    def get_data_list(self):
        return self.list_of_tests

    def get_release_points(self):
        """
        Return a list of release angles and stretches
        :return: a list of 2-element tuples containing the release angle and stretches
        """
        return [(r['release_angle'], r['release_stretch']) for r in self.list_of_tests]

    def get_angle(self, frequency):
        fraction = 0.0
        settings = self.data['settings']

        if settings['UseSemitones']:
            raise Exception("Can't do this with semitones")
        else:
            fraction = (frequency - settings['PitchMinimum']) / settings['PitchSpan']

        if fraction < -1:
            fraction = -1.0
        if fraction > 1:
            fraction = 1.0

        return fraction * (settings['AngleMaximum'] - settings["AngleMinimum"]) + (settings['AngleMaximum'] + settings["AngleMinimum"]) / 2.0


    def get_stretch(self, volume):
        settings = self.data['settings']
        fraction = (volume - settings['VolumeMinimum']) / settings['VolumeSpan']
        if fraction < 0:
            fraction = 0.0
        if fraction > 1:
            fraction = 1.0

        return fraction * (settings["StretchMaximum"] - settings['StretchMinimum']) + settings["StretchMinimum"]


def main():
    x = ContinuousGroup("data/20170403_PM/Test 2017-04-03_15-36-39.json")
    results = library.costs.compute_tolerance_cost(x)
    print(results)

if __name__ == '__main__':
    main()