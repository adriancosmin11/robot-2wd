#!/usr/bin/python3

import rospy
from geometry_msgs.msg import Twist

def talker():
    rospy.init_node('cmd_vel_publisher', anonymous=True)
    pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
    rate = rospy.Rate(10)  # 10hz

    while not rospy.is_shutdown():
        try:
            input_str = input("Enter the linear.x and angular.z values separated by space: ")
            linear_x, angular_z = map(float, input_str.split())
            twist = Twist()
            twist.linear.x = linear_x
            twist.angular.z = angular_z

            print("Publishing to /cmd_vel: linear.x = ", linear_x, ", angular.z = ",  angular_z)
            pub.publish(twist)
        except ValueError:
            print("Invalid input. Please enter two float values separated by space.")
        
        rate.sleep()

if __name__ == '__main__':
    try:
        talker()
    except KeyboardInterrupt:
        pass
