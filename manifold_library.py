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
import datetime
import subprocess
import zipfile
import zlib
import hashlib
import math
import time 

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

    def __init__(self, settingsObject):
        """ Create an isntance of the ComputeManifold class, using a settings
        dictionary object to give the ComputeSolution.exe process the parameters
        of the simulation. """

        # Find the executable and create a process
        # The manifold was not cached and must be generated.
        currentDirectory = os.getcwd()

        os.chdir(BINARY_FOLDER)
        if os.path.exists("settings.json"):
            os.remove("settings.json")

        with open("settings.json", "w") as handle:
            handle.write(json.dumps(settingsObject, indent=4))
        self.process = subprocess.Popen("ComputeSolution.exe", stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=256)
        os.chdir(currentDirectory)

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


class SolutionManifold_obselete:
    """ The SolutionManifold class exists to speed up interpolation lookups on a
    solution manifold. """
    data = {}
    angles = []
    stretches = []
    anglePitch = 0
    stretchPitch = 0


    def __init__(self, manifold):
        """ Initialize a SolutionManifold class using a manifold data
        dictionary, creating the interpolation models and all. """
        # Set the internal data dictionary to the provided manifold
        self.data = manifold 

        # Capture the angles and stretches
        angles = list(set([p['angle'] for k, p in manifold.items()]))
        stretches = list(set([p['stretch'] for k, p in manifold.items()]))
        angles.sort()
        stretches.sort()

        # Create the mathematical model of the stretches and the angles, such
        # that when given a stretch or an angle it returns the closest values
        self.angles = angles
        self.stretches = stretches
        self.anglePitch = (max(angles) - min(angles)) / (len(angles) - 1)
        self.stretchPitch = (max(stretches) - min(stretches)) / (len(stretches) - 1)

    def get_angle_set(self, angle):
        index = int((angle - self.angles[0]) / self.anglePitch)
        return self.angles[index], self.angles[index + 1]

    def get_stretch_set(self, stretch):
        index = int((stretch - self.stretches[0]) / self.stretchPitch)
        return self.stretches[index], self.stretches[index + 1]

    def get(self, angle, stretch):
        """ Perform a lookup to get the closest approach at the element below """
        x1, x2 = self.get_angle_set(angle)
        y1, y2 = self.get_stretch_set(stretch)

        # Check to make sure everything is kosher
        if x1 > angle or x2 < angle:
            raise Exception("angle interpolation didn't work")
        if y1 > stretch or y2 < stretch:
            raise Exception("stretch interpolation didn't work")

        print (x1, angle, x2)
        print (y1, stretch, y2)
        # print self.data[(x1, y1)]['cpa']
        return self.data[(x1, y1)]['cpa']

    def interpolate(self, angle, stretch):
        """ Perform a bilinear interpolation to find the approximate value of
        the solution manifold at a given angle and stretch """
        x1, x2 = self.get_angle_set(angle)
        y1, y2 = self.get_stretch_set(stretch)

        # Check to make sure everything is kosher
        if x1 > angle or x2 < angle:
            raise Exception("angle interpolation didn't work")
        if y1 > stretch or y2 < stretch:
            raise Exception("stretch interpolation didn't work")

        q11 = self.data[(x1, y1)]['cpa']
        q12 = self.data[(x1, y2)]['cpa']
        q21 = self.data[(x2, y1)]['cpa']
        q22 = self.data[(x2, y2)]['cpa']

        r1 = (x2 - angle)/(x2 - x1) * q11 + (angle - x1)/(x2 - x1) * q21 
        r2 = (x2 - angle)/(x2 - x1) * q12 + (angle - x1)/(x2 - x1) * q22 
        p  = (y2 - stretch)/(y2 - y1) * r1 + (stretch - y1)/(y2 - y1) * r2 
        return p

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

def validate_same_manifold(testFiles):
    """ Given a list of test files, validate that they all have the same
    settings such that their manifolds are identical. This is for the pre-
    analysis validation of code that attempts to do some sort of analysis which
    requires a set of tests to all lie on the same manifold. Return True if the
    manifold tokens are all the same, return False if they're not."""
    tokens = {}
    for test in testFiles:
        data = load_test_file(test)
        token = generate_manifold_token(data)
        tokens[token] = 1
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

    outputPath = os.path.join(CACHE_FOLDER, "{}.mfld".format(token))

    output = []
    for k, v in manifold.items():
        output.append("{angle},{stretch},{cpa},{outcome}".format(**v))
    outputString = "\n".join(output)

    with open(outputPath, "w") as handle:
        handle.write(outputString)


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
    currentDirectory = os.getcwd()

    os.chdir(BINARY_FOLDER)
    if os.path.exists("settings.json"):
        os.remove("settings.json")
    if os.path.exists("solution_manifold.txt"):
        os.remove("solution_manifold.txt")

    file("settings.json", "w").write(json.dumps(data['settings']))

    subprocess.call(["Manifold Mapper.exe"])
    manifold = load_solution_manifold("solution_manifold.txt")
    os.chdir(currentDirectory)

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
    can be directly converted to a numpy n-dimenisonal array and plotted via
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
                row.append([1,1,1])
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