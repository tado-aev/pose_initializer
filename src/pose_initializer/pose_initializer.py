#!/usr/bin/env python2

import rospy
from sensor_msgs.msg import NavSatFix
from geometry_msgs.msg import Pose
from tf import transformations

import numpy as np
import collections
import datetime

from geo_pos_conv import GeoPosConv


class PoseInitializer:
    def __init__(self):
        self.plane = rospy.get_param('~plane')
        self.num_samples = rospy.get_param('~num_samples')
        self.cov_threshold = rospy.get_param('~cov_threshold')
        self.move_distance = rospy.get_param('~move_distance')
        self.write_to_file = rospy.get_param('~write_to_file')

        rospy.loginfo('Using plane {0} ({1})',
                      self.plane,
                      GeoPosConv.coordinates[self.plane]['desc'])

        # Reset member variables
        self.converter = None
        self.start_point = None
        self.goal_point = None
        self.samples = None
        self.is_moving = None
        self.reset()

        self.gps_sub = rospy.Subscriber('fix', NavSatFix, self.gps_callback)
        self.pose_pub = rospy.Publisher('initial_pose', Pose, queue_size=1)

    def process_xyz(self, x, y, z):
        self.samples.append((x, y, z))

        avg = np.mean(self.samples, axis=0)
        cov = np.corrcoef(self.samples, rowvar=False)

        if self.is_moving:
            current_dist = self.get_distance_from_start(*avg)
            rospy.loginfo('{0}m left'.format(self.move_distance - current_dist))
            if current_dist >= self.move_distance:
                rospy.loginfo('Okay! You can stop now.')
                self.is_moving = False

        # Calculate the covariance to determine whether the vehicle has stopped
        if len(self.samples) != self.samples.maxlen:
            return
        if np.all([val <= self.cov_threshold for val in cov]):
            if not self.start_point:
                self.start_point = avg
                self.samples.clear()
                rospy.loginfo('Registered starting point. Please move {0}m and stop.'.format(self.move_distance))
                self.is_moving = True
            elif not self.goal_point:
                self.goal_point = avg
                pose = Pose()
                pose.position.x = self.goal_point[0]
                pose.position.y = self.goal_point[1]
                pose.position.z = self.goal_point[2]
                pose.orientation = self.get_orientation()
                self.pose_pub.publish(pose)
                if self.write_to_file:
                    with open(PoseInitializer.get_filename()) as fh:
                        fh.write(str(pose))
                rospy.loginfo('My job is done. Bye!')
                rospy.signal_shutdown('Initialization finished')

    def gps_callback(self, msg):
        self.converter.llh_to_xyz(msg.latitude, msg.longitude, msg.altitude)
        x = self.converter.y()
        y = self.converter.x()
        z = self.converter.z()
        self.process_xyz(x, y, z)

    def get_distance_from_start(self, x, y, z):
        dx = x - self.start_point[0]
        dy = y - self.start_point[1]
        dz = z - self.start_point[2]
        return np.sqrt(dx**2 + dy**2 + dz**2)

    def get_orientation(self):
        dx = self.goal_point[0] - self.start_point[0]
        dy = self.goal_point[1] - self.start_point[1]
        dz = self.goal_point[2] - self.start_point[2]
        dxy = np.sqrt(dx**2 + dy**2)
        # No roll for a line segment
        roll = 0
        pitch = np.arctan2(dy, dx)
        yaw = np.arctan2(dz, dxy)
        return transformations.quaternion_from_euler(roll, pitch, yaw)

    def reset(self):
        self.converter = GeoPosConv()
        self.converter.set_plane(self.plane)
        self.start_point = None
        self.goal_point = None
        self.samples = collections.deque([], maxlen=self.num_samples)
        self.is_moving = False

    @staticmethod
    def get_filename():
        t = rospy.Time.now().to_sec()
        dt = datetime.datetime.fromtimestamp(t)
        fn = dt.strftime('%Y-%m-%d-%H-%M-%S.txt')
        return fn
