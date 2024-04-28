import asyncio

from viam.robot.client import RobotClient
from viam.components.camera import Camera
from viam.components.base import Base
from viam.services.vision import VisionClient

async def connect():
    opts = RobotClient.Options.with_api_key(
        api_key='egwl8qu88gq847oyh68pvu3x27fql9qb',
        api_key_id='8d0919cf-f1e3-490f-926b-2b46a30c4b0c'
    )
    return await RobotClient.at_address('viam-main.52wmvmhgya.viam.cloud', opts)

def leftOrRight(detections, midpoint):
    largest_area = 0
    largest = None
    for d in detections:
        area = (d.x_max - d.x_min) * (d.y_max - d.y_min)
        if area > largest_area:
            largest_area = area
            largest = d
    if largest is None:
        print("nothing detected :(")
        return -1, largest_area

    centerX = (largest.x_min + largest.x_max) / 2
    if centerX < midpoint - midpoint / 6:
        return 0, largest_area  # left
    elif centerX > midpoint + midpoint / 6:
        return 2, largest_area  # right
    else:
        return 1, largest_area  # center

def getDistance(area, threshold=50000):
    return "far" if area < threshold else "close"

async def main():
    spinNum = 5.1
    straightNum = 2000
    numCycles = 200
    vel = 500

    robot = await connect()
    base = Base.from_robot(robot, "robot_base")
    camera_name = "Cam"
    camera = Camera.from_robot(robot, camera_name)
    frame = await camera.get_image(mime_type="image/jpeg")

    my_detector = VisionClient.from_robot(robot, "my_colour_detector")

    for i in range(numCycles):
        detections = await my_detector.get_detections_from_camera(camera_name)

        direction, area = leftOrRight(detections, frame.size[0] / 2)
        distance = getDistance(area)

        print(f"Direction: {direction}, Distance: {distance}")

        if distance == "far":  
            straightNum = 500 # Increase distance if target is far

        if direction == 0:  # left
            await base.spin(spinNum, vel)
            await base.move_straight(straightNum, vel)
        elif direction == 1:  # center
            await base.move_straight(straightNum, vel)
        elif direction == 2:  # right
            await base.spin(-spinNum, vel)
        else:
            print("Searching for target...")

    await robot.close()

if __name__ == "__main__":
    asyncio.run(main())
