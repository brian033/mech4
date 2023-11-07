from Motor import MotorClass
import math
from rtcbot import RTCConnection, getRTCBotJS, CVCamera
from aiohttp import web
import asyncio
import cv2
import numpy as np

routes = web.RouteTableDef()
# settings
leftValStraight = 125
leftValTurn = 60
rightValStraight = 125
rightValTurn = 60
TURNING_MULTIPLIER = 1

PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600

# Initialize the serial connection

motorController = MotorClass(PORT, BAUD_RATE)

def detect_red_dot_and_draw_contours(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # lower_red = np.array([0, 120, 70])
    # upper_red = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    # mask1 = cv2.inRange(hsv, lower_red, upper_red)
    red_mask = cv2.inRange(hsv, lower_red2, upper_red2)
    # red_mask = cv2.add(mask1, mask2)

    contours, _ = cv2.findContours(red_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    red_dot_detected = False

    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 50:  # Threshold
            red_dot_detected = True
            cv2.drawContours(frame, [contour], -1, (0, 255, 0), 3)  # Draw the contour on the frame

    return red_dot_detected, frame

def preprocess(frame):
    detected, f = detect_red_dot_and_draw_contours(frame) 
    if(detected):
        print("Detected!!")
    return frame


# Initialize the camera
camera = CVCamera(preprocessframe=preprocess, fps=15)


# For this example, we use just one global connection
conn = RTCConnection()


def sendSignal(leftForwardVal, leftBackwardVal, rightForwardVal, rightBackwardVal, _sucky=None):
    # 255, 0, 0, 0 (left forward)
    # 0, 255, 0, 0 (left backward)
    print(
        f"[Controller] sending ({leftForwardVal}, {leftBackwardVal}, {rightForwardVal}, {rightBackwardVal}, {_sucky})")
    ret = motorController.send_data(
        leftForwardVal, leftBackwardVal, rightForwardVal, rightBackwardVal, _sucky)
    print(f"[Controller] returned value => {ret}")


@conn.subscribe
def onMessage(msg):  # Called when each message is sent
    global leftValStraight
    global leftValTurn
    global rightValStraight
    global rightValTurn
    global TURNING_MULTIPLIER
    print(msg)
    if (msg == "up"):
        sendSignal(0, leftValStraight, 0, rightValStraight)
    elif (msg == "right"):
        sendSignal(0, leftValTurn, rightValTurn, 0)
    elif (msg == "left"):
        sendSignal(leftValTurn, 0, 0, rightValTurn)
    elif (msg == "down"):
        sendSignal(leftValStraight, 0, rightValStraight, 0)
    elif (msg == "break"):
        sendSignal(0, 0, 0, 0)
    elif (msg == "off"):
        sendSignal(0, 0, 0, 0, _sucky=0)
    elif (msg == "on"):
        sendSignal(0, 0, 0, 0, _sucky=1)
    elif (msg == "light"):
        pass
    else:
        if ("ls=" in msg):
            leftValStraight = int(msg[3:])
            leftValTurn = min(math.floor(
                leftValStraight * TURNING_MULTIPLIER), 255)
        elif ("rs=" in msg):
            rightValStraight = int(msg[3:])
            rightValTurn = min(math.floor(
                rightValStraight * TURNING_MULTIPLIER), 255)


# Send images from the camera through the connection
# conn.video.putSubscription(camera)
conn.video.putSubscription(camera)


# Serve the RTCBot javascript library at /rtcbot.js
@routes.get("/rtcbot.js")
async def rtcbotjs(request):
    return web.Response(content_type="application/javascript", text=getRTCBotJS())

# This sets up the connection


@routes.post("/connect")
async def connect(request):
    clientOffer = await request.json()
    serverResponse = await conn.getLocalDescription(clientOffer)
    return web.json_response(serverResponse)


@routes.get("/")
async def index(request):
    f = open("index.html", "r")
    ret = f.read()
    return web.Response(
        content_type="text/html",
        text=ret)


async def cleanup(app=None):
    await conn.close()
    camera.close()  # Singletons like a camera are not awaited on close

app = web.Application()
app.add_routes(routes)
app.on_shutdown.append(cleanup)
web.run_app(app)
