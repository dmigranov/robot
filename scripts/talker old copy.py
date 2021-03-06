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
from std_msgs.msg import String
import math
import matplotlib.pyplot as plt

from math import sqrt

x = []
y = []
 
def init():
    x_k = 0
    y_k = 0
    fi_k = 0
    return x_k, y_k, fi_k

def step(x_k, y_k, fi_k, dt, v, omega):
    x_k = x_k + dt * v * math.sin(fi_k)
    y_k = y_k + dt * v * math.cos(fi_k)
    fi_k = fi_k + omega * dt
    return x_k, y_k, fi_k

def go_to_point(x_k, y_k, fi_k, x_ref, y_ref, dt):
    global x,y
    coeff1 = 1
    coeff2 = 0.1
    
    dx = x_ref - x_k
    dy = y_ref - y_k

#    fi_ref = math.atan2(dy, dx)   #?????????? ?????????????????? ?????? ??????????, ?????? ???????????????????????
    fi_ref = math.atan(dy/dx)

    if dy < 0:
    	fi_ref = math.pi + fi_ref

    omega = -(fi_k - fi_ref) * coeff1


    v = sqrt(dx ** 2 + dy ** 2) * coeff2
    x_k, y_k, fi_k = step(x_k, y_k, fi_k, dt, v, omega)

    x.append(x_k)
    y.append(y_k)

    return x_k, y_k, fi_k

def go_to_point_opti(x_k, y_k, fi_k, x_ref, y_ref, fi_ref, v, dt):
    #?????????????? ?????????????? ???? ??????????????, ?????????? ????????????????
    global x,y
    coeff = 1
    
    #if close fi_k to fi_ref
        #move
    #else
        #rotate

    omega = -(fi_k - fi_ref) * coeff

    x_k, y_k, fi_k = step(x_k, y_k, fi_k, dt, v, omega)

    x.append(x_k)
    y.append(y_k) 
    return x_k, y_k, fi_k




def talker():
    pub = rospy.Publisher('chatter', String, queue_size=10)
    rospy.init_node('talker', anonymous=True)
    rate = rospy.Rate(100) # 100hz - 0.01 s
 
    x_k, y_k, fi_k = init()

    v = 1.

    x_ref = -10.
    y_ref = 10.

    dx = x_ref - x_k
    dy = y_ref - y_k
    fi_ref = math.atan2(dx, dy) 

    start_time = rospy.get_time()

    while not rospy.is_shutdown():
        end_time = rospy.get_time()
        dt = end_time - start_time
        start_time = end_time

        x_k, y_k, fi_k = go_to_point(x_k, y_k, fi_k, x_ref, y_ref, dt)
        #x_k, y_k, fi_k = go_to_point_opti(x_k, y_k, fi_k, x_ref, y_ref, fi_ref, v, dt)

        hello_str = "x_k = {} y_k = {} fi_k = {} dt = {} ".format(x_k, y_k, fi_k, dt)

        rospy.loginfo(hello_str)
        pub.publish(hello_str)
        rate.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass

    plt.plot(x,y)
    plt.show()
