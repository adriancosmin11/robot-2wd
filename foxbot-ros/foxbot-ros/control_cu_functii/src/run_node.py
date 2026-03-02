#!/usr/bin/python3

import rospy
import os

if __name__ == "__main__":
    rospy.init_node("pyfirmata_node")
    
    script_file = os.path.join(os.path.dirname(__file__), "functii.py")
    os.system("python " + script_file)
