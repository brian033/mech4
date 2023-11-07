from Motor import MotorClass
import math
from rtcbot import RTCConnection, getRTCBotJS, CVCamera
from aiohttp import web
import asyncio
import cv2

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


def preprocess(frame):
    # gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # print("Done!")
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
