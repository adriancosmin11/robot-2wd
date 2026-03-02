#!/usr/bin/python3

import rospy
from std_msgs.msg import Empty

if __name__ == '__main__':
    rospy.init_node('stop_motors_node')
    
    # Create a publisher for the /stop_motors topic
    stop_motors_pub = rospy.Publisher('/stop_motors', Empty, queue_size=1)
    
    # Wait for a short duration to ensure the publisher is registered
    rospy.sleep(1)

    # Publish an empty message to stop the motors
    stop_motors_pub.publish(Empty())
    
    rospy.spin()

