"""


"""


import os       # We use the operating system module for file handling
import json     # This is the json parsing library, it makes reading json easy
import datetime 
import subprocess

import matplotlib
import matplotlib.pyplot as plt 
import numpy
import matplotlib.cm as cm 
import matplotlib.mlab as mlab 

def load_solution_manifold(filepath):
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

def get_solution_manifold(filepath):
    """ given a test trace json, compute the solution manifold using the
    subprocess module and load it into memory """
    currentDirectory = os.getcwd()
    data = json.loads(file(filepath).read())

    os.chdir("manifold")
    if os.path.exists("settings.json"):
        os.remove("settings.json")
    file("settings.json", "w").write(json.dumps(data['settings']))

    subprocess.call(["Manifold Mapper.exe"])


    os.chdir(currentDirectory)


def make(name):
    manifold = load_solution_manifold("{}.txt".format(name))

    angles    = list(set([p['angle'] for k, p in manifold.items()]))
    stretches = list(set([p['stretch'] for k, p in manifold.items()]))

    angles.sort()
    stretches.sort()




    output = []
    grid = []
    g2   = []

    for stretch in stretches:
        row = []
        g2row = []
        for angle in angles:
            key = (angle, stretch)
            row.append(600 - abs(manifold[key]['cpa']))
            if manifold[key]['outcome'] == "hit":
                g2row.append([0,0,1, 1])
            else:
                g2row.append([0,0,0, 0])
        g2.append(g2row)
        grid.append(list(row))
        output.append(",".join(["{}".format(p) for p in row]))

    with open("transformed.csv", "w") as handle:
        handle.write("\n".join(output))

    x = numpy.array(angles)
    y = numpy.array(stretches)
    z = numpy.array(grid)
    z2 = numpy.array(g2)    
    #plt.contourf(x, y, z, 8, cmap=plt.cm.hot)
    #plt.show()
    
    fig, ax = plt.subplots(figsize=(6,6))
    ax.imshow(z, aspect='auto', origin ='lower', cmap = plt.cm.hot, extent=(x.min(), x.max(), y.min(), y.max()))
    #ax.imshow(z2)
    #ax.scatter([0, 0.2], [0, 0])
    #ax.autoscale(False)
    #plt.show()
    plt.savefig("{}.png".format(name))
    
def main():
    mfld = get_solution_manifold(r"D:\Workbench\PERSONAL\Voice\Processing\Solution Manifold 20141007\Easy Data for Plot\Test 2014-10-07_11-18-39.json")


# Disregard this for now.  It's the little bit of magic that makes sure that
# main() is only run if this program is run directly, and not when this program
# is loaded as a code module.
if __name__ == '__main__':
    main()