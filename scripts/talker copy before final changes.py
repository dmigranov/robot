#!/usr/bin/env python
# Software License Agreement (BSD License)
#
# Copyright (c) 2008, Willow Garage, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of Willow Garage, Inc. nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# Revision $Id$
 
## Simple talker demo that published std_msgs/Strings messages
## to the 'chatter' topic
 
import rospy
import numpy as np
from std_msgs.msg import UInt16
import math
import matplotlib.pyplot as plt
 
x = []
y = []

omega_arr = []
phi_ref_arr = []
phi_k_arr = []

v_l_arr = []
v_r_arr = []


 
def init():
    x_k = 0
    y_k = 0
    fi_k = 0
    return x_k, y_k, fi_k
 
def step(x_k, y_k, fi_k, dt, v, omega):
    x_k = x_k + dt*v*math.sin(fi_k)
    y_k = y_k + dt*v*math.cos(fi_k)
    fi_k = fi_k + omega * dt
    return x_k, y_k, fi_k
 
def go_to_point(x_k, y_k, fi_k, x_ref, y_ref, v, dt):
    global x, y, phi_k_arr, omega_arr, phi_ref_arr
 
    coeff = 1
    
    dx = x_ref - x_k
    dy = y_ref - y_k
    fi_ref = math.atan2(dx, dy)
    omega = -(fi_k - fi_ref) * coeff
    
    x_k, y_k, fi_k = step(x_k, y_k, fi_k, dt, v, omega)
    
    x.append(x_k)
    y.append(y_k) 
    phi_k_arr.append(fi_k)
    phi_ref_arr.append(fi_ref)
    omega_arr.append(omega)

    return x_k, y_k, fi_k, omega
    
 
def talker():
    global v_l_arr, v_r_arr

    eps = 1e-2
    v = 1
    omega = math.pi/2
    wheel_r = 0.02
    wheel_dist = 0.11
    
    k1 = wheel_r/2.0
    k2 = wheel_r/wheel_dist

    curPoint = 0
    points = [(3, 3), (4, -2), (3, 3)]
    x_ref = points[curPoint][0]
    y_ref = points[curPoint][1]
    
    left_wheel_pub = rospy.Publisher('vl', UInt16, queue_size=10)
    right_wheel_pub = rospy.Publisher('vr', UInt16, queue_size=10)
    
    rospy.init_node('talker', anonymous=True)
    rate = rospy.Rate(100) # 10hz
 
    x_k, y_k, phi_k = init()

    achieved_destination = False


    start_time = rospy.get_time()
 
    while not rospy.is_shutdown():
        end_time = rospy.get_time()
        dt = end_time - start_time
        start_time = end_time

        if achieved_destination: #??????????
            left_wheel_pub.publish(0)
            right_wheel_pub.publish(0)
            break

        x_k, y_k, phi_k, omega = go_to_point(x_k, y_k, phi_k, x_ref, y_ref, v, dt)

        if curPoint < len(points):
            if abs(omega) > eps:
                v = 0
            else:
                v = 1

        if abs(x_k - x_ref) < eps and abs(y_k - y_ref) < eps:
            publish_str = "\n X: {:.5f}".format(x_k) + ' Y: ' + "{:.5f}".format(y_k) + ' Phi:' + "{:.5f}".format(phi_k)
            rospy.loginfo(publish_str)

            curPoint += 1
            if curPoint == len(points):
                achieved_destination = True
            if not achieved_destination:
                x_ref = points[curPoint][0]
                y_ref = points[curPoint][1]

        v_r = 0.5 * (v / k1 + omega / k2)
        v_l = 0.5 * (v / k1 - omega / k2)

        v_l_arr.append(v_l)
        v_r_arr.append(v_r)

        # ?? ?????????? ?? ?????? ???????????????? ?? ??????????????????! ???????? ???? ???????????? ?????????????????? ?? ??????????-???? ?????????? ??????????????????, ?? ?????????????????? ?? ????????????... 
        # ?????? ???? ???? ?????????????? ?????????????? ?????
        

        if v_r <= 0:
                v_r = 0
        else:
                v_r = 1
        
        if v_l <= 0:
                v_l = 0
        else:
                v_l = 1

        
        publish_wheels = "{:d}".format(v_l) + ' ' + "{:d}".format(v_r)
        left_wheel_pub.publish(v_l)
        right_wheel_pub.publish(v_r)
        #rospy.loginfo(publish_wheels)

        rate.sleep()
 
 
if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
    
    plt.plot(x,y)
    plt.savefig('pos.png')
    plt.clf()

    plt.plot(omega_arr)
    plt.savefig('omega.png')
    plt.clf()
    
    plt.plot(phi_ref_arr)
    plt.savefig('fi_ref.png')
    plt.clf()

    plt.plot(phi_k_arr)
    plt.savefig('fi_k.png')
    plt.clf()

    plt.plot(v_l_arr)
    plt.plot(v_r_arr)
    plt.savefig('v_lr.png')
    plt.clf()
