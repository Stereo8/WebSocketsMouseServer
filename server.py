import asyncio
from asyncio.events import new_event_loop
import functools
import socket
import websockets
from zeroconf import ServiceInfo, Zeroconf
from multiprocessing import freeze_support
from screeninfo import get_monitors


from pynput.mouse import Controller, Button

delta = 0.03
screen_center = (0, 0)
zc = None

mouse : Controller = Controller()

def move_mouse(x, y):
    mouse.move(x, y)

async def listener(websocket):
    async for message in websocket:

        if message == 'levi':
            mouse.click(Button.left)
        elif message == 'desni':
            mouse.click(Button.right)
        elif message == 'center':
            mouse.position = screen_center
        elif message== 'close':
            await websocket.close()
        else:
            x, y, z = message.split()

            # print(f"{x}\t{y}\t{z}")

            x = float(x)
            y = float(y)
            z = float(z)

            if z > delta or x > delta or z < -delta or x < -delta:
                mouse_x = int(-z*20)
                mouse_y = int(-x*20)
                await loop.run_in_executor(None, functools.partial(move_mouse, mouse_x, mouse_y))

async def main():
    global zc
    global screen_center
    props = {}

    zc = Zeroconf()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    localIP = s.getsockname()[0]

    for monitor in get_monitors():
        print(monitor)
        if monitor.is_primary:
            screen_center = (monitor.width/2, monitor.height/2)


    info : ServiceInfo = ServiceInfo("_http._tcp.local.",
        "NintendoWiid._http._tcp.local.",
        8765,
        properties=props,
        addresses=[localIP])

    await zc.async_register_service(info)

    server = await websockets.serve(listener, "0.0.0.0", 8765)
    await server.serve_forever()

async def finish():
    global zc
    await zc.async_unregister_all_services() 

freeze_support()
loop = new_event_loop()
try:
    loop.run_until_complete(main())
except KeyboardInterrupt:
    loop.run_until_complete(finish())
finally:
    print("Izlazim...\n")
