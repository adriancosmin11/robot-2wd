#!/usr/bin/python3

import rospy
from geometry_msgs.msg import Twist
from functii_cu_masuratori import move_motors

def cmd_vel_callback(msg):
    x = msg.linear.x
    z = msg.angular.z
    move_motors(x, z)

def cmd_vel_listener():
    rospy.init_node('direction_control_node')
    rospy.Subscriber("/cmd_vel", Twist, cmd_vel_callback)
    rospy.spin()
    
if __name__ == '__main__':
    cmd_vel_listener()
 
