"""
    This is my python vector library, which I have used for many projects over a long period of time.  It has been
    made to handle the specifics of most common vector mathematics and to make vectors easy to work with in
    Python.

"""

__author__ = 'Matt Jarvis'

import math
import numpy as np

EQUALS_TOLERANCE = 0.00001

class Vector:
    x = 0.0
    y = 0.0
    z = 0.0
    def __init__(self, *args, **kwargs):
        if len(args) == 0:
            return
        if (len(args) == 1):
            oneArgument = True
            singleArgument = args[0]
        else:
            oneArgument = False
            singleArgument = None
        if (oneArgument and isinstance(singleArgument, Vector)):
            self.x = singleArgument.x
            self.y = singleArgument.y
            self.z = singleArgument.z
        elif (oneArgument and isinstance(singleArgument, dict)):
            self.x = singleArgument['x']
            self.y = singleArgument['y']
            self.z = singleArgument['z']
        elif (oneArgument):
            self.x = singleArgument[0]
            self.y = singleArgument[1]
            self.z = singleArgument[2]
        else:
            self.x = args[0]
            self.y = args[1]
            self.z = args[2]
        return

    def dict(self):
        return self.__dict__

    def list(self):
        return [self.x, self.y, self.z]

    def rotate_x(self, angle):
        nx = self.x
        ny = 0 * self.x + math.cos(angle) * self.y + math.sin(angle) * self.z
        nz = 0 * self.x - math.sin(angle) * self.y + math.cos(angle) * self.z
        return Vector(nx, ny, nz)

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)
    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)
    def __mul__(self, scale):
        return Vector(self.x * scale, self.y * scale, self.z * scale)

    def __div__(self, other):
        return self * (1.0 / other)

    def __str__(self):
        return "Vector({}, {}, {})".format(self.x, self.y, self.z)

    def scale(self, scale):
        return self * scale

    def dot(self, other):
        return self.x*other.x + self.y*other.y + self.z*other.z

    def cross(self, other):
        # Cross product of b x c (this vector is b)
        b = self
        c = other
        a = Vector(0, 0, 0)
        a.x = b.y * c.z - b.z * c.y
        a.y = b.z * c.x - b.x * c.z
        a.z = b.x * c.y - b.y * c.x
        return a

    def equals(self, other):
        if self.distance_to(other) < EQUALS_TOLERANCE:
            return True
        return

    def unit(self):
        l = self.length()
        return self * (1.0 / l)


    def distance_to(self, v2):
        return math.sqrt( (self.x-v2.x)**2 + (self.y-v2.y)**2 + (self.z-v2.z)**2 )

    def length(self):
        return self.distance_to(Vector(0,0,0))

    def transform(self, T):
        """ Transform the given vector instance by the transformation matrix T """
        v = np.matrix([self.x, self.y, self.z, 1]).transpose()
        t = T * v
        return Vector(t[0,0], t[1,0], t[2,0])

    def str(self):
        return "Vector({}, {}, {})".format(self.x, self.y, self.z)

    def __repr__(self):
        return self.str()

def pick_closest_point(vec1, veclist):
    select = [ (vec1.distance_to(vec), vec) for vec in veclist ]
    return min(select)[1]

def pick_closest_index(vec1, veclist):
    select = [ (vec1.distance_to(vec), i) for i, vec in enumerate(veclist) ]
    return min(select)[1]

def remove_adjacent_duplicates(veclist):
    """ Remove any adjacent duplicate points and return a cleaned version of the
        vector list """
    cleaned = []
    for i in range(len(veclist) - 1):
        p0 = veclist[i]
        p1 = veclist[i+1]
        if p0.distance_to(p1) > 0.001:
            cleaned.append(p0)
    if p1.distance_to(veclist[0]) > 0.001:
        cleaned.append(p1)
    return cleaned

def get_average_point(points):
    """
    Get the average (mean) point of a list of points
    :param points: a list of Vector objects
    :return: a single Vector at the mean location
    """
    n = float(len(points))
    a = Vector()
    for v in points:
        a += v
    return a / n

def max_distance_between_points(points):
    return max([max([[p.distance_to(p2), p, p2] for p2 in points]) for p in points])[0]

def points_with_max_distance(points):
    result = max([max([[p.distance_to(p2), p, p2] for p2 in points]) for p in points])
    return result[1], result[2]

def remove_all_duplicates(veclist, tolerance):
    """ Comprehensinvely remove all duplicate points from the manifold.  Note
        that this can cause issues on manifolds which cross themselves.
        """
    cleaned = []

    for v in veclist:
        notRepeating = True
        for c in cleaned:
            if v.distance_to(c) <= tolerance:
                notRepeating = False
                break
        if notRepeating:
            cleaned.append(v)
    return cleaned

def three_point_angle(anchor, p1, p2):
    v1 = p1 - anchor
    v2 = p2 - anchor
    return math.acos(v1.dot(v2) / (v1.length() * v2.length()) )

def two_vector_angle(v1, v2):
    return math.acos( v1.dot(v2) / (v1.length() * v2.length()))


def GetAngle(v1, v2):
    v1t = Vector(0, v1.y, v1.z)
    v2t = Vector(0, v2.y, v2.z)
    return math.acos( v1t.dot(v2t) / (v1t.length() * v2t.length()))

def manifold_split_between( splitPoint1, splitPoint2, manifold):
    # Extracts the section of a manifold between two points that lie on it
    if type(splitPoint1) == int:
        split1 = splitPoint1
        splitPoint1 = manifold[split1]
    else:
        split1 = manifold_preceeding_point_index(splitPoint1, manifold)

    if type(splitPoint2) == int:
        split2 = splitPoint2
        splitPoint2 = manifold[split2]
    else:
        split2 = manifold_preceeding_point_index(splitPoint2, manifold)
    splitManifold = []


    if (split1 < split2):
        s1 = split1
        s2 = split2
        p1 = splitPoint1
        p2 = splitPoint2
    else:
        s1 = split2
        s2 = split1
        p1 = splitPoint2
        p2 = splitPoint1

    splitManifold.append(p1)
    for i, p in enumerate(manifold):
        if i > s1 and i <= s2:
            splitManifold.append(p)

    # if splitPoint2 is after the last point on the manifold (that is, past 90 degrees on a
    # comparison such that the projection onto the last segment is out of bounds and the
    # last point itself is returned as the preceeding point index), it is possible to have
    # the last point so close that it doubles up.  As a result it is necessary to check here
    # to make sure that we aren't repeating the final point.
    if not splitManifold[-1].equals(p2):
        splitManifold.append(p2)

    return splitManifold

def manifold_partition_closed2(splitPoint1, splitPoint2, manifold):
    temp = list(manifold)
    if temp[0].equals(temp[-1]):
        del temp[-1]

    center = manifold_split_between(splitPoint1, splitPoint2, temp)
    lead   = manifold_split_between(0, splitPoint1, temp)

    k      = manifold_preceeding_point_index(splitPoint2, manifold)
    trail  = [splitPoint2] + manifold[k+1:]

    outer  = remove_adjacent_duplicates(trail + lead)
    return center, outer

def manifold_partition_closed(splitPoint1, splitPoint2, manifold):
    temp = list(manifold)
    temp = remove_adjacent_duplicates(temp)

    center = manifold_split_between(splitPoint1, splitPoint2, temp)

    # Rotate the manifold
    s1 = manifold_preceeding_point_index(splitPoint1, temp)
    s2 = manifold_preceeding_point_index(splitPoint2, temp)
    sc = int((s1 + s2)/2)
    temp = temp[sc:] + temp[:sc]
    temp = remove_adjacent_duplicates(temp)
    if not temp[0].equals(temp[-1]):
        temp.append(temp[0])

    outer = manifold_split_between(splitPoint1, splitPoint2, temp)

    return center, outer

def manifold_preceeding_point_index( testPoint, manifold ):
    # This function scans a manifold to see if the testPoint lies on it.  If it does, the function
    # returns the index number of the preceeding point, if it does not the function returns a -1
    #closest, smallestErr = closestPoint1( testPoint, manifold)
    d, p, preceeding = closest_point(testPoint, manifold)
    return preceeding

def manifold_length(manifold):
    l = 0
    for i in range(len(manifold) - 1):
        l += manifold[i].distance_to(manifold[i+1])
    return l

def point_along_manifold_fractional(manifold, fractionalDistanceAlongCurve):
    """ Return a vector which corresponds with the fractional distance along this
        manifold.  Uses point_along_manifold and manifold_length. """
    length   = manifold_length(manifold)
    distance = fractionalDistanceAlongCurve * length
    return point_along_manifold(manifold, distance)

def point_along_manifold(manifold, distanceAlongCurve):
    length = 0
    if (distanceAlongCurve > manifold_length(manifold)):
        return manifold[-1]

    for i in range(len(manifold) - 1):
        v = manifold[i+1] - manifold[i]
        distanceHere = length
        distanceThere = length + v.length()

        if (distanceAlongCurve >= distanceHere and distanceAlongCurve <= distanceThere):
            u = v.unit()
            return manifold[i] + (u * (distanceAlongCurve - distanceHere))
        length = distanceThere

    last = len(manifold) - 1
    v = manifold[last] - manifold[last-1]
    u = v.unit()
    return manifold[last-1] + (u * (distanceAlongCurve - length))

def length_along_manifold(point, manifold):
    """ measure the distance of the closest point on the manifold to the beginning
        of the manifold """
    distance, closest, preceeding = closest_point(point, manifold)
    totalLength = 0

    i = 0
    while i < preceeding:
        totalLength += manifold[i].distance_to(manifold[i+1])
        i+=1

    return totalLength + manifold[preceeding].distance_to(closest)

def resample_curve(manifold, samplingDistance):
    l = samplingDistance
    total = manifold_length(manifold)

    resampled = [manifold[0], ]
    while l <= total:
        resampled.append(point_along_manifold(manifold, l))
        l += samplingDistance
    return resampled

def project_onto_segment(p0, p1, point):
    """ project the vector "point" onto the segment p0 -> p1
    """
    u = point - p0
    v = (p1 - p0).unit()
    s = u.dot(v)
    r = v * s
    return p0 + r

def scalar_projection(q, p, v):
    """ Return the scalar projection (positive or negative) of q projected onto
        the vector v located at point p. """
    u = q - p
    v = v.unit()
    s = u.dot(v)
    return s

def closest_point( pnt, pntList ):
    # New closest point algorithm, probably not terribly efficient, but it's damn accurate
    rangeList = [ [pnt.distance_to(pntList[0]), pntList[0], 0],  ]  # Add the first point
    for i in range(1, len(pntList)):
        p0 = pntList[i-1]
        p1 = pntList[i]

        # Project pnt onto vector p0->p1
        r      = project_onto_segment(p0, p1, pnt)

        # If r lies on the segment, add it to the range list
        length = p0.distance_to(p1)
        l0     = p0.distance_to(r)
        l1     = p1.distance_to(r)
        if (l0 < length and l1 < length) and l0 > 0.001 and l1 > 0.001:
            rangeList.append([pnt.distance_to(r), r, i-1])

        # Add point i
        rangeList.append( [p1.distance_to(pnt), p1, i]) # Add the point itself (includes the last point)
    ret = min(rangeList) # Find the closest one
    return ret

def closest_point_only(pnt, pntList):
    d, c, k = closest_point(pnt, pntList)
    return c

def closest_n_points( pnt, pntList, n):
    # New closest point algorithm, probably not terribly efficient, but it's damn accurate
    rangeList = [ [pnt.distance_to(pntList[0]), pntList[0], 0],  ]  # Add the first point
    for i in range(1, len(pntList)):
        p0 = pntList[i-1]
        p1 = pntList[i]

        # Project pnt onto vector p0->p1
        r      = project_onto_segment(p0, p1, pnt)

        # If r lies on the segment, add it to the range list
        length = p0.distance_to(p1)
        l0     = p0.distance_to(r)
        l1     = p1.distance_to(r)
        if (l0 < length and l1 < length) and l0 > 0.001 and l1 > 0.001:
            rangeList.append([pnt.distance_to(r), r, i-1])

        # Add point i
        rangeList.append( [p1.distance_to(pnt), p1, i]) # Add the point itself (includes the last point)
    rangeList.sort()
    return rangeList[:n]

def compute_intersection(r1start, r1end, r2start, r2end, debug=False):
    P0 = r1start
    Q0 = r2start
    u = (r1end - r1start).unit()
    v = (r2end - r2start).unit()

    w0 = P0 - Q0

    a = u.dot(u)
    b = u.dot(v)
    c = v.dot(v)
    d = u.dot(w0)
    e = v.dot(w0)

    if (a * c - b * b) == 0:
        return None

    sc = (b * e - c * d) / (a * c - b * b)
    tc = (a * e - b * d) / (a * c - b * b)
    P = (u * sc) + P0
    Q = (v * tc) + Q0

    if debug:
        import code
        code.interact(local=locals())
    if (sc < 0):
        return None

    if (tc < 0):
        return None

    if r1start.distance_to(P) > r1start.distance_to(r1end):
        return None

    if r2start.distance_to(Q) > r2start.distance_to(r2end):
        return None

    i = (P + Q) * 0.5
    if (i.x != i.x or i.y != i.y or i.z != i.z):
        return None

    iq = project_onto_segment(r1start, r1end, i)
    if i.distance_to(iq) < 0.003:
        return iq

    return None


def get_intersections(a, b, manifold):
    intersections = []

    for i in range(len(manifold) - 1):
        p0 = manifold[i]
        p1 = manifold[i+1]
        result = compute_intersection(a, b, p0, p1)
        if result != None:
            intersections.append(result)
            #print "found"
    return intersections


def rodrigues_matrix(axis, theta):
    axis = np.array([axis.x, axis.y, axis.z])

    axis = axis/math.sqrt(np.dot(axis,axis))
    a = math.cos(theta/2)
    b,c,d = -axis*math.sin(theta/2)
    return np.array([[a*a+b*b-c*c-d*d, 2*(b*c-a*d), 2*(b*d+a*c)],
                     [2*(b*c+a*d), a*a+c*c-b*b-d*d, 2*(c*d-a*b)],
                     [2*(b*d-a*c), 2*(c*d+a*b), a*a+d*d-b*b-c*c]])

def rotate_around(p, axis, theta):
    rotated = np.dot(rodrigues_matrix(axis, theta), np.array([p.x, p.y, p.z]))
    return Vector(rotated)

def rotate_point_around(point, anchor, axis, theta):
    p = point - anchor
    rotated = rotate_around(p, axis, theta)
    return rotated + anchor

def point_plane_distance(q, p, n):
    """ q is the point to be projected, p and n define the plane """
    return (q - p).dot(n) / (n.dot(n))

def get_transformation_matrix(tx, ty, tz, rx, ry, rz):
    """ Assemble a transformation matrix from the given transformations """
    T = np.matrix(np.zeros((4,4)))

    T[0, 0] = math.cos(ry) * math.cos(rz)
    T[1, 0] = -math.cos(ry) * math.sin(rz)
    T[2, 0] = math.sin(ry)

    T[0, 1] = math.cos(rx) * math.sin(rz) + math.sin(rx) * math.sin(ry) * math.cos(rz)
    T[1, 1] = math.cos(rx) * math.cos(rz) - math.sin(rx) * math.sin(ry) * math.sin(rz)
    T[2, 1] = -math.sin(rx) * math.cos(ry)

    T[0, 2] = math.sin(rx) * math.sin(rz) - math.cos(rx) * math.sin(ry) * math.cos(rz)
    T[1, 2] = math.sin(rx) * math.cos(rz) + math.cos(rx) * math.sin(ry) * math.sin(rz)
    T[2, 2] = math.cos(rx) * math.cos(ry)

    T[0,3] = tx
    T[1,3] = ty
    T[2,3] = tz
    T[3,3] = 1

    return T

def set_zero_position_high( points ):
    """ move the 0 position of the manifold to the point of the highest Y value
    (furthest towards the leading edge)  This function does this by rotating the
    0 element in the mesh, and is meant for a CLOSED or near-closed mesh only
    """

    highest = [0, points[0].y]
    for i, point in enumerate( points ):
        if ( point.y > highest[1] ):
            highest = [i, point.y]
    points = points[highest[0]:] + points[:highest[0]]
    return points

def set_zero_position_low( points ):
    """ move the 0 position of the manifold to the point of the lowest Y value
     (furthest towards the trailing edge)  This function does this by rotating
     the 0 element in the mesh, and is meant for a CLOSED or near-closed mesh
     only"""

    lowest = [0,points[0].y]
    for i, point in enumerate( points ):
        if ( point.y < lowest[1] ):
            lowest = [i, point.y]
    points = points[lowest[0]:] + points[:lowest[0]]
    return points

def set_zero_at_largest_gap( points, threshold):
    """ sets the zero position right after the largest gap, assuming it's above
    a threshold value"""

    gapiest = [0, points[-1].distance_to(points[0])]
    for i in range(len(points)-1):
        gap = points[i].distance_to(points[i+1])
        if (gap > gapiest[1]):
            gapiest = [i+1, gap]
    if (gapiest[1] > threshold):
        points = points[gapiest[0]:] + points[:gapiest[0]]
        return points
    else:
        return False

def rotate_manifold_index_to_zero(points, index):
    # Moves the 0 position of the manifold to a point of specified index.  Works for closed
    # meshes only
    return points[index:] + points[:index]

def main():
    a = Vector(1, 0, 0)
    b = Vector(1, 0, 0)
    p = Vector(0.5, 0, 0)


    print(a.__dict__)

if __name__ == '__main__':
    main()