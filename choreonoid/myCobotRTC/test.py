#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
import math3d
from pymycobot import MyCobot280
import numpy

# print(dir(math3d))
#vec = math3d.Vector()
#trans_matrix = [[1, 0, 0, 10], [0, 1, 0, 20], [0, 0, 1, 30]]
trans_matrix = [[math.cos(0.3), -math.sin(0.3), 0, 10],
                [math.sin(0.3), math.cos(0.3), 0, 20], [0, 0, 1, 30]]
trans = math3d.Transform(trans_matrix)


print(dir(trans))
print(trans.pos.x)
print(trans.pos.y)
print(trans.pos.z)
print(trans.matrix)
print(trans.array)
print(trans.orient)
print(trans.pose_vector)

rpy = trans.orient.to_euler('xyz')
print(rpy)
"""

mycobot = MyCobot280("COM8", 115200)
print(mycobot.get_coords())
"""
trans = math3d.Transform([[-1, 0, 0, 0.2], [0, 1, 0, 0.2], [0, 0, -1, 0.16]])
vec = trans.orient.to_euler('xyz')
roll = vec[0]*180/math.pi
pitch = vec[1]*180/math.pi
yaw = vec[2]*180/math.pi


print(roll)
print(pitch)
print(yaw)


def diffMatrix(R4_target, R4_current, e):

    R_current = R4_current[:, :3]
    t_current = R4_current[:, 3]

    R_target = R4_target[:, :3]
    t_target = R4_target[:, 3]

    R_diff = R_target @ R_current.T

    cos_theta = (numpy.trace(R_diff) - 1.0) / 2.0
    cos_theta = numpy.clip(cos_theta, -1.0, 1.0)

    rot_diff = numpy.arccos(cos_theta)

    position_error = numpy.linalg.norm(t_target - t_current)

    if rot_diff+position_error > e:
        return True
    return False


n1 = numpy.array([[-1.0, 0.0, 0.0, 0.0], [0.0, 0.0, -1.0, 0.0], [0.0, -1.0, 0.0, 0.4]])
n2 = numpy.array([[-1.0, 0.0, 0.0, 1.2], [0.0, 0.0, -1.0, -0.5], [0.0, -1.0, 0.0, 0.4]])
diffMatrix(n1, n2, 0.01)