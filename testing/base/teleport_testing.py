#! /usr/bin/env python
"""
This script tests the 'data stream' oriented feature of the socket interface.
"""

from morse.testing.testing import MorseTestCase

try:
    # Include this import to be able to use your test file as a regular 
    # builder script, ie, usable with: 'morse [run|exec] <your test>.py
    from morse.builder.morsebuilder import *
except ImportError:
    pass

import os
import sys
import socket
import math
import json
import time
import random
from pymorse import Morse

def send_pose(s, x, y, z, yaw, pitch, roll):
    s.send(json.dumps({'x' : x, 'y' : y, 'z' : z, 'yaw' : yaw, 'pitch' : pitch, 'roll' : roll}).encode())


class TeleportTest(MorseTestCase):

    def setUpEnv(self):
        
        robot = Robot('rmax')
        robot.translate(10.0, 8.0, 20.0)
        
        teleport = Actuator('teleport')
        teleport.configure_mw('socket')
        robot.append(teleport)

        pose = Sensor('pose')
        pose.configure_mw('socket')
        robot.append(pose)

        env = Environment('indoors-1/indoor-1')
        env.configure_service('socket')

    def _test_one_pose(self, x, y, z, yaw, pitch, roll):
        send_pose(self.teleport_stream, x, y, z, yaw, pitch, roll)
        time.sleep(0.2)

        pose = self.pose_stream.get()
        self.assertAlmostEqual(pose['yaw'], yaw, delta=self.precision)
        self.assertAlmostEqual(pose['pitch'], pitch, delta=self.precision)
        self.assertAlmostEqual(pose['roll'], roll, delta=self.precision)
        self.assertAlmostEqual(pose['x'], x, delta=self.precision)
        self.assertAlmostEqual(pose['y'], y, delta=self.precision)
        self.assertAlmostEqual(pose['z'], z, delta=self.precision)

    def test_teleport(self):
        """ Test if we can connect to the pose data stream, and read from it.
        """

        with Morse() as morse:
            self.pose_stream = morse.stream('Pose')

            port = morse.get_stream_port('Motion_Controller')
            self.teleport_stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.teleport_stream.connect(('localhost', port))

            self.precision = 0.15

            pose = self.pose_stream.get()
            self.assertAlmostEqual(pose['yaw'], 0.0, delta=self.precision)
            self.assertAlmostEqual(pose['pitch'], 0.0, delta=self.precision)
            self.assertAlmostEqual(pose['roll'], 0.0, delta=self.precision)
            self.assertAlmostEqual(pose['x'], 10.0, delta=self.precision)
            self.assertAlmostEqual(pose['y'], 8.0, delta=self.precision)
            self.assertAlmostEqual(pose['z'], 20.0, delta=self.precision)

            # Test only one rotation each time, otherwise, it a bit more
            # complex to check that it does the good transformation
            # (without a matrix transformation library)
            for i in range(0, 5):
                self._test_one_pose(random.uniform(-30.0, 30.0),
                                    random.uniform(-30.0, 30.0),
                                    random.uniform(10.0, 50.0),
                                    random.uniform(-math.pi, math.pi),
                                    0, 0)
                self._test_one_pose(random.uniform(-30.0, 30.0),
                                    random.uniform(-30.0, 30.0),
                                    random.uniform(10.0, 50.0),
                                    0,
                                    random.uniform(-math.pi, math.pi),
                                    0)
                self._test_one_pose(random.uniform(-30.0, 30.0),
                                    random.uniform(-30.0, 30.0),
                                    random.uniform(10.0, 50.0),
                                    0, 0,
                                    random.uniform(-math.pi, math.pi))



########################## Run these tests ##########################
if __name__ == "__main__":
    import unittest
    from morse.testing.testing import MorseTestRunner
    suite = unittest.TestLoader().loadTestsFromTestCase(TeleportTest)
    sys.exit(not MorseTestRunner().run(suite).wasSuccessful())
