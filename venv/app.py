import json
from flask import Flask, request, render_template, redirect, url_for
import requests
import sys
#sys.path.append('C:/Users/31638/Documents/GitHub/BD01-Python/venv/Include/Sphero_Bolt_Multiplatform_Python_Bleak-master/sphero_bolt.py')
import asyncio
import math
from typing import Dict
from sphero_bolt import SpheroBolt


app =  Flask(__name__)
api_url = "http://localhost:8080"

rolling_route = []
stop_at_checkpoints = []
my_sphero = None
run_route = 0

# #C8:A9:B8:65:67:EA
address = (
    "D0:56:BC:B1:69:8B"
    #"DD:E6:08:45:EA:7D"
)

# connect to sphero bolt

my_sphero = SpheroBolt(address)

#65 speed = slow
#100 speed = fast

async def sphero_roll(my_sphero, actions):
    next_heading = None
    action_nr = 1
    time = 0

    await my_sphero.connect()
    await my_sphero.wake()
    await my_sphero.resetYaw()

    for i in actions:
        checkpoint = i['step']
        distance = i['distance']
        heading = i['heading']
        if action_nr < len(actions):
            next_heading = actions[action_nr]['heading']
                
        while distance > 0:
            
            if i['heading'] == next_heading or distance >= 0.695 + 0.49:
                if distance >= 0.695:
                    time = int(distance//0.695)
                    distance -= 0.695*time

                    for iteration in range(time):
                        await asyncio.sleep(2)
                        await my_sphero.roll(100, heading)
                        await asyncio.sleep(2)

            if distance >= 0.49:
                time = int(distance//0.49)
                print(time)
                distance -= 0.49*time

                for iteration in range(time):
                    await asyncio.sleep(2)
                    await my_sphero.roll(65, heading)
                    await asyncio.sleep(2)
            
            elif distance >= 0.2 and ((distance <= 0.05)== False):
                time = int(distance//0.2)
                if time == 0:
                    time = 1
                distance -= 0.2*time

                for iteration in range(time):
                    await asyncio.sleep(2)
                    await my_sphero.roll(50, heading)
                    await asyncio.sleep(2)
            
            else:
                distance = 0
        # print(stop_at_checkpoints)
        if (stop_at_checkpoints.__contains__(checkpoint)):
            await asyncio.sleep(5)
            print('stop')
            
        if action_nr < len(actions):
            next_heading = actions[action_nr]['heading']
            if heading != next_heading:
                await asyncio.sleep(2)
                await my_sphero.roll(65, heading)
                await asyncio.sleep(2)
            action_nr += 1
        else:
            await asyncio.sleep(2)
            await my_sphero.roll(65, heading)
            await asyncio.sleep(2)
        
        
    await my_sphero.disconnect()
    return

def get_step(route):
    return route.get('step')

def get_route(route):
    return route.get('Route_id')

def get_step_id(route):
    return route.get('id')


@app.route('/')
def index():
    return route()

@app.route('/workspaces', methods=['GET', 'POST'])
def workspaces():
    response = requests.get(api_url+"/workspaces")
    json_string = response.json()
    return render_template("create-environment.html", workspaces = json_string)

@app.route('/locations/select_error', methods=['GET', 'POST'])
def locations_select_error():
    response = requests.get(api_url+"/workspaces")
    json_string = response.json()
    return render_template("edit-environment-on-error-table.html", workspaces = json_string)

@app.route('/locations/select_error/<workspace_id>', methods=['GET', 'POST'])
def locations_select_error_clicked(workspace_id):
    return render_template("edit-environment-on-error.html", id = workspace_id)

@app.route('/workspaces/on_error', methods=['GET', 'POST'])
def workspaces_on_error():
    return render_template("create-environment-on-error.html")

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

@app.route('/route', methods=['GET', 'POST'])
def route():
    response = requests.get(api_url+"/route")
    json_string = response.json()
    json_string.sort(key=get_step_id)
    json_string.sort(key=get_route)
    return render_template("full-route.html", routes = json_string, stop_at_checkpoints = stop_at_checkpoints, run_route = run_route)

@app.route('/route/create/<route_id>/<id>/<name>/<angle>/<distance>/<alt_route>/<alt_route_id>', methods=['GET','POST'])
def create_route(route_id, id, name, angle, distance, alt_route, alt_route_id):
    if alt_route == None:
        alt_route = 0
    if alt_route_id == None:
        alt_route_id = 0
    print(str(alt_route) + " | " + str(alt_route_id))
    json_string = {"Route_id": int(route_id), "id": int(id), "name": name, "angle": int(angle), "distance": float(distance), "alt_route": int(alt_route), "alt_route_id": int(alt_route_id)}
    response = requests.get(api_url+"/route/insert", json=json_string)
    return redirect('/')

@app.route('/route/delete/<id>')
def delete_route(id):
    json_string = {"id": int(id)}
    response = requests.delete(api_url+"/route/delete", json=json_string)
    return redirect('/')
    
@app.route('/route/update/<new_id>/<new_route>/<name>/<angle>/<distance>/<id>/<route_id>/<alt_route>/<alt_route_id>', methods=['GET', 'POST'])
def update_route(new_id, new_route, name, angle, distance, id, route_id, alt_route, alt_route_id):
    if alt_route == None:
        alt_route = 0
    if alt_route_id == None:
        alt_route_id = 0
    if new_id == None:
        new_id == id
    if new_route == None:
        new_route = route_id
    json_string = { 'new_id': int(new_id), 'new_route': int(new_route),'name': name, 'angle': int(angle), 'distance': float(distance), 'id': int(id), 'Route_id': int(route_id), 'alt_route': int(alt_route), 'alt_route_id': int(alt_route_id)}
    requests.put(api_url+"/route/update", json=json_string)
    return redirect('/')

@app.route('/roll/route/<route_id>')
def roll_route(route_id):
    print(my_sphero)
    json_string = { 'route_id': int(route_id) }
    response = requests.get(api_url+"/route/by_id", json=json_string)
    route_data = response.json()
    stop_check = False
    for i in stop_at_checkpoints:
        i = int(i)
    print(stop_at_checkpoints)
    route_data.sort(key=get_step_id)
    for i in route_data:
        if rolling_route != []:
            if i['angle'] == rolling_route[len(rolling_route)-1]['heading']:
                if stop_at_checkpoints.__contains__(str(i['id'])):
                    rolling_route.append({
                        "step": i['id'],
                        "distance": i['distance'],
                        "heading": i['angle']
                    })
                else:
                    rolling_route[-1]['distance'] += i['distance']

            else:
                rolling_route.append({
                    "step": i['id'],
                    "distance": i['distance'],
                    "heading": i['angle']
                })

        else:
            rolling_route.append({
                "step": i['id'],
                "distance": i['distance'],
                "heading": i['angle']
            })
        print(str(i['id']) + " | " + str(i['alt_route']))
        if int(i['alt_route']) != 0:
            if stop_at_checkpoints != []:
                if int(i['id']) >= int(max(stop_at_checkpoints)):
                    return roll_route(str(i['alt_route']))

    rolling_route.sort(key=get_step)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.set_debug(True)
    loop.run_until_complete(sphero_roll(my_sphero, rolling_route))
    stop_at_checkpoints.clear()
    rolling_route.clear()
    return redirect('/')
    


# def jimmy(route_id)
#     json_string = { 'route_id': int(route_id) }
#     response = requests.get(api_url+"/route/by_id", json=json_string)
#     route_data = response.json()

#     for k in range(len(stop_at_checkpoints)):
#         start_of_sum = int(stop_at_checkpoints[k])-1
#         for i in range(1)

#         stop_at_checkpoints
#         route_data[0]['distance']
#         route = []
#         counter = 0

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
    print(route)
    #loop = asyncio.new_event_loop()
    #asyncio.set_event_loop(loop)
    #loop.set_debug(True)
    #loop.run_until_complete(calculate_distance(my_sphero, route))
    return redirect('/')

@app.route('/set/checkpoint/<checkpoint>')
def add_checkpoint(checkpoint):
    if stop_at_checkpoints.__contains__(checkpoint) == False:
        stop_at_checkpoints.append(int(checkpoint))
        print(stop_at_checkpoints)
    return redirect('/')

@app.route('/remove/checkpoint/<checkpoint>')
def remove_checkpoint(checkpoint):
    if stop_at_checkpoints.__contains__(int(checkpoint)):
        stop_at_checkpoints.remove(int(checkpoint))
        print(stop_at_checkpoints)
    return redirect('/')

@app.errorhandler(404)
def page_not_found(e):
    return redirect('/')

@app.errorhandler(500)
def empty_element_detected(e):
    return render_template('error-handle.html')

if __name__ == "__main__":
    app.debug = True
    app.run()
    rolling_route = []
    my_sphero = None