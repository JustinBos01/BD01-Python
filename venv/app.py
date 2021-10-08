from flask import Flask, request, render_template, redirect, url_for
from flask_modals import Modal
import requests
import sys
#sys.path.append('C:/Users/31638/Documents/GitHub/BD01-Python/venv/Include/Sphero_Bolt_Multiplatform_Python_Bleak-master/sphero_bolt.py')
import asyncio
import math
from typing import Dict
from sphero_bolt import SpheroBolt


app =  Flask(__name__)
modal = Modal(app)
api_url = "http://localhost:8080"


address = (
    "C8:A9:B8:65:67:EA"
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
    print(action_collection)
    await my_sphero.connect()
    await my_sphero.wake()
    await my_sphero.resetYaw()
    for i in action_collection:
        distance = i['distance']
        heading = i['heading']
        action_backup = action_collection

        for looping in range(2):
            if distance > 1.56:
                passed_distance = math.floor(distance/1.56)
                distance -= 1.56*passed_distance
                await asyncio.sleep(2)
                for index in range(passed_distance-1):
                    await my_sphero.roll(255, heading)
                    await asyncio.sleep(2)

            else:
                while distance >= 0:
                    time = math.floor(distance/0.22)
                    #handle remainder of distance
                    if time <= 0:
                        time = 1
                    distance -= time*0.22
                    await asyncio.sleep(2)
                    for i in range(time-1):
                        await my_sphero.roll(35, heading)
                        await asyncio.sleep(2)
    print("returning")
    asyncio._set_running_loop(await calculate_reverse_distance(my_sphero, action_backup))
    return

async def calculate_reverse_distance(my_sphero, action_collection):
    for i in reversed(action_collection):
        distance = i['distance']
        heading = i['heading']+180
        if heading >= 360:
            heading -= 360
        action_backup = action_collection

        for looping in range(2):
            if distance > 1.56:
                passed_distance = math.floor(distance/1.56)
                distance -= 1.56*passed_distance
                await asyncio.sleep(2)
                for index in range(passed_distance-1):
                    await my_sphero.roll(255, heading)
                    await asyncio.sleep(2)

            else:
                while distance >= 0:
                    time = math.floor(distance/0.22)
                    #handle remainder of distance
                    if time <= 0:
                        time = 1
                    distance -= time*0.22
                    await asyncio.sleep(2)
                    for i in range(time-1):
                        await my_sphero.roll(35, heading)
                        await asyncio.sleep(2)
    await my_sphero.disconnect()
    return





@app.route('/')
def index():
    #collection = [{
    #    "distance":  0.5,
    #    "heading": 90
    #}]
    #collection.append({
    #    "distance": 0.5,
    #    "heading": 180
    #})
    #loop = asyncio.new_event_loop()
    #asyncio.set_event_loop(loop)
    #loop.set_debug(True)
    #loop.run_until_complete(calculate_distance(my_sphero, collection))
    return workspaces()

@app.route('/workspaces', methods=['GET', 'POST'])
def workspaces():
    response = requests.get(api_url+"/workspaces")
    json_string = response.json()
    return render_template("create-environment.html", workspaces = json_string)

@app.route('/workspaces/create/<workspace_name>', methods=['GET', 'POST'])
def create_workspace(workspace_name):
    json_string = {"workspace_name": workspace_name}
    response = requests.get(api_url+"/workspaces/insert", json=json_string)
    return redirect('/')

@app.route('/workspaces/delete/<workspace_id>', methods=['GET', 'POST'])
def delete_workspace(workspace_id):
    json_string = {"id": int(workspace_id)}
    response = requests.delete(api_url+"/workspaces/delete/workspace_by_id", json=json_string)
    return redirect('/')

@app.route('/workspaces/update/<workspace_id>/<workspace_name>', methods=['GET', 'POST'])
def update_workspace(workspace_id, workspace_name):
    json_string = {"id": int(workspace_id), "workspace_name": workspace_name}
    response = requests.put(api_url+"/workspaces/update", json=json_string)
    return redirect('/')

@app.route('/locations/<workspace_id>', methods=['GET', 'POST'])
def location(workspace_id):
    json_string = { 'workspace_id': int(workspace_id) }
    response = requests.get(api_url+"/locations/by_workspace_id", json=json_string)
    json_string = response.json()
    return render_template("edit-environment.html", locations = json_string)

@app.route('/locations/create/<workspace_id>/<angle>/<distance>', methods=['GET', 'POST'])
def create_location(workspace_id, angle, distance):
    json_string = { 'workspace_id': int(workspace_id), 'angle': int(angle), 'distance': int(distance) }
    requests.post(api_url+"/locations/insert", json=json_string)
    return redirect('/locations/' + workspace_id)

@app.route('/locations/delete/<id>/<workspace_id>', methods=['GET', 'POST'])
def delete_location(id, workspace_id):
    json_string = { 'id': int(id) }
    requests.delete(api_url+"/locations/delete/location_by_id", json=json_string)
    return redirect('/locations/' + workspace_id)

@app.route('/locations/update/<id>/<workspace_id>/<angle>/<distance>', methods=['GET', 'POST'])
def update_location(id, workspace_id, angle, distance):
    json_string = { 'id': int(id), 'angle': int(angle), 'distance': int(distance)}
    requests.put(api_url+"/locations/update", json=json_string)
    return redirect('/locations/' + workspace_id)

#@app.route('/locations/<workspace_id>/<angle>/<distance>', methods=['GET', 'POST'])
#def location_by_workspace_id(workspace_id, angle, distance):
#    json_string = { 'workspace_id': int(workspace_id) }
#    response = requests.get(api_url+"/locations/by_workspace_id", json=json_string)
#    json_string = response.json()
#    return render_template("edit-environment.html", locations = json_string, angle=angle, distance=distance)

@app.route('/users', methods=['GET', 'POST'])
def users():
    response = requests.get(api_url+"/users")
    json_string = response.json()
    return render_template('create-users.html', users = json_string)

@app.route('/users/create/<username>/<password>', methods=['GET','POST'])
def create_user(username, password):
    json_string = {"userName": username, "password": password}
    response = requests.get(api_url+"/users/insert", json=json_string)
    return users()

@app.route('/roll/<workspace_id>')
def roll_workspace(workspace_id):
    json_string = { 'workspace_id': int(workspace_id) }
    response = requests.get(api_url+"/locations/by_workspace_id", json=json_string)
    route_data = response.json()
    route = []
    for i in route_data:
        route.append({
            "distance": i['distance'],
            "heading": i['angle']
        })
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.set_debug(True)
    loop.run_until_complete(calculate_distance(my_sphero, route))
    return redirect('/')
