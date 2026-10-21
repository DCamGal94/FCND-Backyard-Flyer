import argparse
import time
from enum import Enum

import numpy as np

from udacidrone import Drone
from udacidrone.connection import MavlinkConnection, WebSocketConnection  # noqa: F401
from udacidrone.messaging import MsgID


class States(Enum):
    MANUAL = 0
    ARMING = 1
    TAKEOFF = 2
    WAYPOINT = 3
    LANDING = 4
    DISARMING = 5


class BackyardFlyer(Drone):

    def __init__(self, connection):
        super().__init__(connection)
        self.target_position = np.array([0.0, 0.0, 0.0])
        self.all_waypoints = []
        self.in_mission = True
        self.check_state = {}

        # initial state
        self.flight_state = States.MANUAL

        # Telemetry events that drive the state machine;
        # each callback fires when its message arrives
        self.register_callback(MsgID.LOCAL_POSITION, self.local_position_callback)
        self.register_callback(MsgID.LOCAL_VELOCITY, self.velocity_callback)
        self.register_callback(MsgID.STATE, self.state_callback)

    def local_position_callback(self):
        """
        TODO: Implement this method

        This triggers when `MsgID.LOCAL_POSITION` is received and self.local_position contains new data
        """
        pass

    def velocity_callback(self):
        """
        TODO: Implement this method

        This triggers when `MsgID.LOCAL_VELOCITY` is received and self.local_velocity contains new data
        """
        pass

    def state_callback(self):
        """
        This triggers when `MsgID.STATE` is received and self.armed and self.guided contain new data
        """

        # Mission is over (set False when we return to MANUAL); ignore further
        # STATE messages so the callback can't restart the sequence.
        if not self.in_mission:
            return
        # Idle on the ground, waiting for the first STATE message: start the
        # mission. The transition sets flight_state to ARMING, so later messages
        # skip this branch and don't re-send the arm command.
        if self.flight_state == States.MANUAL:
            self.arming_transition()
        # Arm command sent, not yet confirmed. self.armed is telemetry from the
        # vehicle, so wait for it to read True before taking off. Taking off
        # before the autopilot confirms the arm would be rejected.
        elif self.flight_state == States.ARMING:
            if self.armed:
                self.takeoff_transition()
        # Landed and disarm commanded: wait for the vehicle to confirm
        # (armed == False) before handing control back and ending the mission.
        elif self.flight_state == States.DISARMING:
            if not self.armed:
                self.manual_transition()

    def calculate_box(self):
        """TODO: Fill out this method
        
        1. Return waypoints to fly a box
        """
        pass

    def arming_transition(self):
        """
        1. Take control of the drone
        2. Pass an arming command
        3. Set the home location to current position
        4. Transition to the ARMING state
        """
        print("arming transition")

        # Take control of the drone using take_control() from the API documentation
        self.take_control()

        # Arm the drone using arm() from the API documentation
        self.arm()

        # Set the starting position to the current location of the drone using set_home_position(longitude, latitude, altitude)
        # where the longitude, latitude, and altitude parameters can be defined using the
        # global_position array in the form [longitude (deg), latitude (deg), altitude (m)]
        self.set_home_position(self.global_position[0], 
                               self.global_position[1],
                                self.global_position[2])
        
        # Set the flight_state to the arming state
        self.flight_state = States.ARMING

    def takeoff_transition(self):
        """
        1. Set target_position altitude to 3.0m
        2. Command a takeoff to 3.0m
        3. Transition to the TAKEOFF state
        """
        print("takeoff transition")

        # Set a target altitude position of 3.0m using takeoff(target_altitude) from the API
        target_altitude = 3.0 # define a variable that stores the desired altitude value
        self.target_position[2] = target_altitude # set the third index in the target_position array from __init__ to the desired altitude
        self.takeoff(target_altitude) # issue takeoff command
        self.flight_state = States.TAKEOFF # Set the flight_state to the takeoff state

    def waypoint_transition(self):
        """TODO: Fill out this method
    
        1. Command the next waypoint position
        2. Transition to WAYPOINT state
        """
        print("waypoint transition")

    def landing_transition(self):
        """TODO: Fill out this method
        
        1. Command the drone to land
        2. Transition to the LANDING state
        """
        print("landing transition")

    def disarming_transition(self):
        """TODO: Fill out this method
        
        1. Command the drone to disarm
        2. Transition to the DISARMING state
        """
        print("disarm transition")

    def manual_transition(self):
        """This method is provided
        
        1. Release control of the drone
        2. Stop the connection (and telemetry log)
        3. End the mission
        4. Transition to the MANUAL state
        """
        print("manual transition")

        self.release_control()
        self.stop()
        self.in_mission = False
        self.flight_state = States.MANUAL

    def start(self):
        """This method is provided
        
        1. Open a log file
        2. Start the drone connection
        3. Close the log file
        """
        print("Creating log file")
        self.start_log("Logs", "NavLog.txt")
        print("starting connection")
        self.connection.start()
        print("Closing log file")
        self.stop_log()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5760, help='Port number')
    parser.add_argument('--host', type=str, default='127.0.0.1', help="host address, i.e. '127.0.0.1'")
    args = parser.parse_args()

    conn = MavlinkConnection('tcp:{0}:{1}'.format(args.host, args.port), threaded=False, PX4=False)
    #conn = WebSocketConnection('ws://{0}:{1}'.format(args.host, args.port))
    drone = BackyardFlyer(conn)
    time.sleep(2)
    drone.start()
