import asyncio
import math
from typing import Dict

from sphero_bolt import SpheroBolt
# mac address of sphero bolt
address = (
    "DD:E6:08:45:EA:7D"
)

# connect to sphero bolt
my_sphero = SpheroBolt(address)

async def run(my_sphero):
    
    try:
        await my_sphero.connect()

        # wake sphero
        await my_sphero.wake()

        await my_sphero.resetYaw()
        await asyncio.sleep(2)

        # roll in a square
        for i in range(4):
            await my_sphero.roll(50, 90 * i)
            await asyncio.sleep(2)

    finally:
        await my_sphero.disconnect()


async def calculate_distance(my_sphero, action_collection):
    #255 speed 1 seconde = 78 cm
    #bx = y

    # distance = 0.78
    # speed = 255
    # time = 1
    # 0.78m per seconde 255 speed
    # time = distance/0.78
    action_backup = action_collection
    print(action_backup)
    for i in action_backup:
        print(i['heading'])
        i['heading'] += 180

    #22 cm 50 speed 2 seconde
    await my_sphero.connect()
    await my_sphero.wake()
    await my_sphero.resetYaw()

    for i in action_collection:
        # print(1 + i['heading'])
        distance = int(i['distance'])
        heading = int(i['heading'])
        while distance != 0:
            #distance = i['distance']
            if distance > 1.56:
                passed_distance = math.floor(distance/1.56)
                distance -= 1.56*passed_distance
                i['distance'] = distance
                #print(i['heading'])
                
                await asyncio.sleep(2)

                # roll in a square
                for index in range(passed_distance-1):
                    heading = int(i['heading'])
                    await my_sphero.roll(255, heading)
                    await asyncio.sleep(2)

            else:
                heading = int(i['heading'])
                distance = int(i['distance'])
                while(distance >= 0):
                    time = math.floor(distance/0.22)
                    if time <= 0:
                        time = 1
                    print(time)
                    distance -= time*0.22
                    await asyncio.sleep(2)
                    for i in range(time-1):
                        await my_sphero.roll(35, heading)
                        await asyncio.sleep(2)
                    print(distance)
                    # loop.set_debug(True)
                    # await loop.run_until_complete(calculate_distance_reverse(my_sphero, distance_backup, heading-180))
                
    await asyncio.sleep(10)
    loop = asyncio._set_running_loop(await calculate_distance_reverse(my_sphero, action_backup))
    await my_sphero.disconnect()

async def calculate_distance_reverse(my_sphero, action_collection):
    #255 speed 1 seconde = 78 cm
    #bx = y

    # distance = 0.78
    # speed = 255
    # time = 1
    # 0.78m per seconde 255 speed
    # time = distance/0.78

    #22 cm 50 speed 2 seconde

    for i in action_collection:
        distance = i['distance']
        while distance != 0:
            if distance > 1.56:
                passed_distance = math.floor(distance/1.56)
                distance -= 1.56*passed_distance
                i['distance'] = distance
                
                await asyncio.sleep(2)

                # roll in a square
                for index in range(passed_distance-1):
                    heading = int(i['heading'])
                    await my_sphero.roll(255, heading)
                    await asyncio.sleep(2)

            else:
                if i['heading'] > 360:
                    i['heading'] -= 180
                distance = i['distance']
                time = math.floor(distance/0.22)
                distance -= time*0.22
                i['distance'] = distance
                await asyncio.sleep(2)
                for i in range(time-1):
                    heading = int(i['heading'])
                    await my_sphero.roll(35, heading)
                    await asyncio.sleep(2)
                print('stopping')

if __name__ == "__main__":
    distance = 1.5
    angle = 90
    collection = [{
        "distance":  1.5,
        "heading": 90
    }]
    collection.append({
        "distance": 1.5,
        "heading": 180
    })
    print(collection)
    #value = input('test')
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    loop.run_until_complete(calculate_distance(my_sphero, collection))