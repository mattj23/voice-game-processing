"""
    This is a library for helping in the processing of solution manifolds for
    the voice trial data.  The intent of this library is to abstract the
    majority of the computationally complex operations so that processing code
    for analysis relating to solution manifolds becomes simple and
    straightforward.  Thus this file contains no analysis on its own.

    Matt Jarvis, 10/10/2014
"""

import os
import json
import subprocess
import hashlib
import math

try:
    import tests
except:
    import library.tests as tests

MODULE_PATH = os.path.dirname(__file__)
BINARY_FOLDER = os.path.join(MODULE_PATH, "manifold_binaries")
CACHE_FOLDER  = os.path.join(MODULE_PATH, "manifold_cache")


class SolutionManifold:
    """ The SolutionManifold class exists to perform live computations of the
    closest approach given a settings file and a series of angles and stretches.
    The class operates by spawning a background instance of ComputeSolution.exe
    and communicating with it through the standard in and standard out pipes.
    When finished, the process is closed with a termination command. """
    process = None

    def __init__(self, settings_object):
        """ Create an instance of the ComputeManifold class, using a settings
        dictionary object to give the ComputeSolution.exe process the parameters
        of the simulation. """

        # Find the executable and create a process
        # The manifold was not cached and must be generated.
        current_directory = os.getcwd()

        os.chdir(BINARY_FOLDER)
        if os.path.exists("settings.json"):
            os.remove("settings.json")

        with open("settings.json", "w") as handle:
            handle.write(json.dumps(settings_object, indent=4))
        self.process = subprocess.Popen("ComputeSolution.exe", stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=256)
        os.chdir(current_directory)

    def get_closest_approach(self, angle, stretch):
        """ Feed the angle and stretch to the embedded simulation process and
        return the results. """
        self.process.stdin.write("{},{}\n".format(angle, stretch))
        self.process.stdin.flush()
        self.process.stdout.flush()
        result = self.process.stdout.readline()
        return float(result)

    def close_process(self):
        self.process.stdin.write("end\n")


def get_angle(pitch, data):
    """ Compute the angle associated with any pitch the same way that the game
    engine does it"""
    fraction = 0
    if data['settings']['UseSemitones']:
        semitone = 12 * math.log(pitch / data['starting_pitch'], 2)
        fraction = semitone / data['settings']['SemitoneSpan']
    else:
        fraction = (pitch - data['starting_pitch']) / data['settings']['PitchSpan']
    if fraction < -1:
        fraction = -1
    if fraction > 1:
        fraction = 1
    return fraction * (data['settings']['AngleMaximum'] - data['settings']['AngleMinimum']) + (data['settings']['AngleMaximum'] + data['settings']['AngleMinimum']) / 2.0


def get_stretch(volume, data):
    """ Compute the stretch associated with any volume the same way that the
    game engine does it.""" 
    fraction = (volume - data['starting_volume']) / data['settings']['VolumeSpan']
    if fraction < 0:
        fraction = 0
    if fraction > 1:
        fraction = 1
    return fraction * (data['settings']['StretchMaximum'] - data['settings']['StretchMinimum']) + data['settings']['StretchMinimum']


def validate_same_manifold(test_list):
    """
    Given a list of test data or test files, validate that they have the same settings such that their manifolds are
    identical. This is for pre-analysis validation of any code that attempts to perform some analysis which requires all
    tests in an analysis set to be on the same solution manifold. Return True if the manifold tokens are all the same,
    return False if they are not.
    :param test_list: a list of test files or a list of test result dictionaries, or a TestGroup object
    :return: True if the tests all lie on the same manifold, False if they do not
    """
    if isinstance(test_list, tests.TestGroup):
        test_list = test_list.get_data_list()

    # If the elements of test are all dictionaries with the "settings" key in them, we continue as expected. If they are
    # strings then we assume they are filepaths and attempt to load them.  Technically they can be mixed (filenames and
    # result dictionaries) but that's bad practice.
    test_data = []
    for element in test_list:
        if type(element) is dict:
            if "settings" in element.keys():
                test_data.append(element)
            else:
                raise Exception("An element in test_list is a dictionary but does not have a settings subelement")
        elif type(element) is str:
            data = tests.load_test_file(element)
            if data is None:
                raise Exception("An element in test_list is a string but cannot be loaded as a test file")
            else:
                test_data.append(data)
        else:
            raise Exception("An element in test_list is neither dictionary nor string nor TestGroup object")

    # Check to make sure that they all have the same manifold token
    tokens = {}
    for test in test_data:
        token = generate_manifold_token(test)
        tokens[token] = None
    if len(tokens.keys()) == 1:
        return True
    return False


def generate_manifold_token(data): 
    """ Generate a hashed manifold 'token' which is a unique identifier that
    represents the contents of the data settings which contribute to changes in
    the solution manifold.  Data sets with the same manifold token have the same
    manifold.  This can be checked programmatically or written theoretically.
    For now we use the theoretical method by identifying parameters which we
    know contribute to solution manifold change."""

    # Specify the contributing parameters of the settings file which change the
    # value of the solution manifold
    contributors = ["PitchMinimum", "UseSemitones", "Gravity", "VolumeMinimum", "PitchMaximum", "SemitoneSpan", "TargetValidDiameter", "VolumeMaximum", "PitchSpan", "AngleMinimum", "FieldWidth", "Target", "AngleMaximum", "StretchMinimum", "StretchMaximum", "Obstacle", "VolumeSpan"]
    
    # Create a hash engine
    engine = hashlib.sha1()

    # extract the settings
    for key in contributors:
        element = data['settings'][key]
        
        # If the element type is a dictionary, we will assume that all elements
        # of the dictionary are contributors and so we will extract and sort the
        # keys and update the hash engine with each subelement in order.
        # Otherwise we will assume that the element is itself should be hashed
        # and we will update the hash engine directly.
        if type(element) == dict:
            subkeys = sorted(element.keys())
            for subkey in subkeys:
                engine.update("{}".format(element[subkey]))
        else:
            engine.update("{}".format(element))

    # Return the hexdigest as the manifold token
    return engine.hexdigest()


def load_solution_manifold(filepath):
    """ Load a solution manifold from a comma separated value text file of the
    sort which is exported by the "Manifold Mapper.exe" binary.  Return the
    manifold as a dictionary of dictionary subelements, each of which has four
    key-value pairs for the angle, the stretch, the closest point of approach,
    and the outcome for each point in the solution space. The keys of the main
    dictionary itself are tuples with the angle, stretch pair that defines the
    point in the solution space."""

    with open(filepath) as handle:
        lines = [line.strip() for line in handle if line.strip()]

    manifold = {}
    for line in lines[1:]:
        angle, stretch, cpa, outcome = [p.strip() for p in line.split(",")]
        angle = float(angle)
        stretch = float(stretch)
        cpa = float(cpa)

        manifold[(angle, stretch)] = {"angle":angle, "stretch":stretch, "cpa":cpa, "outcome":outcome}

    return manifold 

def load_cached_manifold(token):
    """ Load the cached manifold file and return the manifold object.  If the
    manifold is not already cached, return False."""
    filepath = os.path.join(CACHE_FOLDER, "{}.mfld".format(token))
    if not os.path.exists(filepath):
        return False

    manifold = load_solution_manifold(filepath)
    return manifold 

def save_cached_manifold(token, manifold):
    """ Save the cached manifold file to the CACHE_FOLDER. """
    if not os.path.exists(CACHE_FOLDER):
        os.mkdir(CACHE_FOLDER)

    output_path = os.path.join(CACHE_FOLDER, "{}.mfld".format(token))

    output = ["angle,stretch,cpa,outcome"]
    for k, v in manifold.items():
        output.append("{angle},{stretch},{cpa},{outcome}".format(**v))
    output_string = "\n".join(output)

    with open(output_path, "w") as handle:
        handle.write(output_string)


def get_solution_manifold(data):
    """ Given the test data dictionary, check to see whether or not this
    solution manifold has been computed and cached already.  If it has not been,
    use the binary "Manifold Mapper.exe" file in the manifold_binaries folder to
    generate the solution manifold and cache it.  Otherwise load the cached
    manifold.  In either case return the manifold object, which is a list of
    dictionaries, each of which represents a single point in the solution space
    and has key-value pairs for the angle, stretch, CPA, and outcome."""

    # Get the manifold token and attempt to load the manifold from cache.
    token = generate_manifold_token(data)
    cached = load_cached_manifold(token)
    if cached:
        return cached 
    # The manifold was not cached and must be generated.
    current_directory = os.getcwd()

    os.chdir(BINARY_FOLDER)
    if os.path.exists("settings.json"):
        os.remove("settings.json")
    if os.path.exists("solution_manifold.txt"):
        os.remove("solution_manifold.txt")

    file("settings.json", "w").write(json.dumps(data['settings']))

    subprocess.call(["Manifold Mapper.exe"])
    manifold = load_solution_manifold("solution_manifold.txt")
    os.remove("solution_manifold.txt")
    os.chdir(current_directory)

    # Cache the manifold so we won't have to do this again in the future
    save_cached_manifold(token, manifold)

    return manifold


def get_manifold_matrix(manifold):
    """ Transform the solution manifold as computer or loaded from cache into a
    2 dimensional array of the format for the Total Cost Analysis matlab code.
    This should return a nested list which can be direclty converted into a
    numpy n-dimensional array."""
    angles = list(set([p['angle'] for k, p in manifold.items()]))
    stretches = list(set([p['stretch'] for k, p in manifold.items()]))
    angles.sort()
    stretches.sort()

    output = []
    for stretch in stretches:
        row = [manifold[(angle, stretch)]['cpa'] for angle in angles]
        output.append(row)

    return angles, stretches, output


def get_manifold_draw_matrix(manifold):
    """ Given a manifold list/dictionary object, generate the nested list which
    can be directly converted to a numpy n-dimensional array and plotted via
    imshow, as well as the x and y axis lists."""

    # Resolve the unique angles and stretches, and get the furthest closest
    # point of approach so that the color base can be scaled against it.
    angles    = list(set([p['angle'] for k, p in manifold.items()]))
    stretches = list(set([p['stretch'] for k, p in manifold.items()]))
    cpaMax    = max([abs(p['cpa']) for k, p in manifold.items()])

    # Sort the angles and stretches
    angles.sort()
    stretches.sort()

    output = []

    for stretch in stretches:
        row = []
        for angle in angles:
            key = (angle, stretch)
            
            cpa = abs(manifold[key]['cpa'])
            outcome = manifold[key]['outcome']

            if outcome == "hit":
                row.append([1, 1, 1])
            else:
                value = (cpaMax - cpa) / cpaMax
                if value < 0:
                    value = 0
                if outcome == "obstacle":
                    row.append([2*value,value,0])
                else:
                    row.append([value,value,0])
        output.append(row)

    return angles, stretches, output

if __name__ == '__main__':

    pass