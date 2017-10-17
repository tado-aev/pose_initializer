#!/usr/bin/env python2

import rospy

import pose_initializer

rospy.init_node('pose_initializer')

initializer = pose_initializer.PoseInitializer()

rospy.spin()
