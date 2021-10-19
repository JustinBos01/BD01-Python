import json
from flask import Flask, request, render_template, redirect, url_for
from flask_modals import Modal
import requests
import sys
#sys.path.append('C:/Users/31638/Documents/GitHub/BD01-Python/venv/Include/Sphero_Bolt_Multiplatform_Python_Bleak-master/sphero_bolt.py')
import asyncio
import math
from typing import Dict
from sphero_bolt import SpheroBolt
import azure.cognitiveservices.speech as speechsdk


app =  Flask(__name__)
modal = Modal(app)
api_url = "http://localhost:8080"

stop_at_checkpoints = []

#C8:A9:B8:65:67:EA
address = (
    "F5:68:22:6D:5D:9D"
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
        while distance > 0:
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
        
        if (stop_at_checkpoints.__contains__(str(checkpoint))):
            await asyncio.sleep(10)
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
    return render_template("full-route.html", routes = json_string)

@app.route('/route/create/<route_id>/<id>/<name>/<angle>/<distance>', methods=['GET','POST'])
def create_route(route_id, id, name, angle, distance):
    json_string = {"route_id": int(route_id), "id": int(id), "name": name, "angle": int(angle), "distance": float(distance)}
    response = requests.get(api_url+"/route/insert", json=json_string)
    return redirect('/')

@app.route('/route/delete/<id>')
def delete_route(id):
    json_string = {"id": int(id)}
    response = requests.delete(api_url+"/route/delete", json=json_string)
    return redirect('/')
    
@app.route('/route/update/<id>/<name>/<angle>/<distance>', methods=['GET', 'POST'])
def update_route(id, name, angle, distance):
    json_string = { 'id': int(id), 'name': name, 'angle': int(angle), 'distance': float(distance)}
    requests.put(api_url+"/route/update", json=json_string)
    return redirect('/')

@app.route('/roll/route/<route_id>')



def roll_route(route_id):
    json_string = { 'route_id': int(route_id) }
    response = requests.get(api_url+"/route/by_id", json=json_string)
    route_data = response.json()
    route = []
    counter = 0
    # try:
    for i in route_data:
        # if route != []:
        #     if i['angle'] == route[-1]['heading']:
        #         route[-1]['distance'] += i['distance']
        #         print('toevoegen', route)
        #     else:
        #         route.append({
        #             "step": i['id'],
        #             "distance": i['distance'],
        #             "heading": i['angle']
        #         })
        # else:
        route.append({
            "step": i['id'],
            "distance": i['distance'],
            "heading": i['angle']
        })
        route.sort(key=get_step)
    # except:
    #     print('Empty route')
    print(route)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.set_debug(True)
    loop.run_until_complete(sphero_roll(my_sphero, route))
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

@app.route('/speech')
async def from_mic():
    speech_config = speechsdk.SpeechConfig(subscription="<paste-your-speech-key-here>", region="<paste-your-speech-location/region-here>")
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
    speech_config.speech_recognition_language="en-US"
    
    print("Speak into your microphone.")
    result = speech_recognizer.recognize_once_async().get()
    print(result.text)
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(result.text))
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(result.no_match_details))
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
    await asyncio.sleep(10)
    return redirect('/')

@app.route('/set/checkpoint/<checkpoint>')
def add_checkpoint(checkpoint):
    if stop_at_checkpoints.__contains__(checkpoint) == False:
        stop_at_checkpoints.append(checkpoint)
        print(stop_at_checkpoints)
    return redirect('/')

@app.route('/remove/checkpoint/<checkpoint>')
def remove_checkpoint(checkpoint):
    if stop_at_checkpoints.__contains__(checkpoint):
        stop_at_checkpoints.remove(checkpoint)
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