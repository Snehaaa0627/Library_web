from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64

import time

class RobotControl(Node):
    # Reference for euler to quart conversion
    preset_ref = {
        -1.57: [-0.707, 0.707],
        0: [1.0, 0.0],
        1.57: [0.707, 0.707],
        3.14: [0.0, 1.0]
    }

    def __init__(self, initial_pose):
        rclpy.init()
        super().__init__('library_interface')

        self.initial_pose = initial_pose

        self.navigator = BasicNavigator()
        self.navigator.setInitialPose(self.eulerToMapPose(self.initial_pose))
        self.navigator.waitUntilNav2Active()
        self.door_publisher = self.create_publisher(Float64, 'door_control', 1)

        self.goal_poses = []
        self.current_pose_tuple = self.initial_pose

        self.initial_start = True
        self.has_completed = True
        self.task_result = TaskResult.SUCCEEDED

    # Basic rad to quartion conversion function
    # If the angle is not present in the dict, returns a default value to avoid crashing
    def simpleRadToQuart(self, rad):
        res = self.preset_ref.get(rad)
        if res: return res
        return [0.707, 0.707]

    # Converts (x, y, theta) into map pose
    def eulerToMapPose(self, map_pose):
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.navigator.get_clock().now().to_msg()
        pose.pose.position.x = map_pose[0]
        pose.pose.position.y = map_pose[1]

        quart = self.simpleRadToQuart(map_pose[2])

        pose.pose.orientation.z = quart[0]
        pose.pose.orientation.w = quart[1]

        return pose

    # Makes NAV2 navigate to the given pose tuple
    def goToEulerPose(self, pose_tuple):
        self.navigator.goToPose(self.eulerToMapPose(pose_tuple))
        self.has_completed = False

    def add_new_goal_pose(self, pose_tuple):
        print(f"Adding {pose_tuple} to queue")

        # Inserting goals into the queue
        if (self.goal_poses):
            self.goal_poses.insert(-1, pose_tuple)
            return
        
        # Starting without initial goals
        self.goal_poses.append(pose_tuple)
        self.goal_poses.append(self.initial_pose)
        self.initial_start = True

    # Check whether goals are present in the queue
    def is_goals_present(self):
        return bool(self.goal_poses)

    # Getter for has_completed
    def is_task_complete(self):
        return self.has_completed

    # Must be called repeatedly to manage the queue and navigating to poses
    def update(self):
        if self.is_goals_present():
            self.has_completed = self.navigator.isTaskComplete()
            self.task_result = self.navigator.getResult()

            if self.is_task_complete():
                if not self.initial_start:
                    self.door_open()
                    input("Load/Unload the tray and press ENTER")
                    self.door_close()
                else:
                    self.initial_start = False

                self.current_pose_tuple = self.goal_poses.pop(0)
                self.goToEulerPose(self.current_pose_tuple)

    # Opens the delivery door
    def door_open(self):
        print(f"Opening door")
        msg = Float64()
        msg.data = 1.0
        self.door_publisher.publish(msg)
        time.sleep(3)

    # Closes the delivery door
    def door_close(self):
        print(f"Closing door")
        msg = Float64()
        msg.data = -1.0
        self.door_publisher.publish(msg)
        time.sleep(3)

def main():
    robot = RobotControl((0.0, 0.0, 3.14))
    robot.add_new_goal_pose((4.0, 0.0, 0.0))
    robot.add_new_goal_pose((1.0, 0.0, 0.0))

    while robot.is_goals_present():
        robot.update()

    robot.add_new_goal_pose((4.0, 0.0, 0.0))

    while robot.is_goals_present():
        robot.update()
    
if __name__ == "__main__":
    main()