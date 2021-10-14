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

#C8:A9:B8:65:67:EA
address = (
    #"F5:68:22:6D:5D:9D"
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
    print(action_collection)
    await my_sphero.connect()
    await my_sphero.wake()
    await my_sphero.resetYaw()
    for i in action_collection:
        distance = i['distance']
        heading = i['heading']
        action_backup = action_collection

        for looping in range(2):
            if distance > 1.20:
                passed_distance = math.floor(distance/1.20)
                distance -= 1.20*passed_distance
                await asyncio.sleep(2)
                for index in range(passed_distance):
                    await my_sphero.roll(200, heading)
                    await asyncio.sleep(2)

            else:
                while distance >= 0:
                    time = math.floor(distance/0.50) + 1
                    # #handle remainder of distance
                    # if time <= 0:
                    #     time = 1
                    distance -= time*0.50
                    await asyncio.sleep(2)
                    for i in range(time):
                        await my_sphero.roll(100, heading)
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
            if distance > 1.20:
                passed_distance = math.floor(distance/1.20)
                distance -= 1.20*passed_distance
                await asyncio.sleep(2)
                for index in range(passed_distance):
                    await my_sphero.roll(200, heading)
                    await asyncio.sleep(2)

            else:
                while distance >= 0:
                    time = math.floor(distance/0.50) + 1
                    #handle remainder of distance
                    # if time <= 0:
                    #     time = 1
                    distance -= time*0.50
                    await asyncio.sleep(2)
                    for i in range(time):
                        await my_sphero.roll(100, heading)
                        await asyncio.sleep(2)
    await my_sphero.disconnect()
    return



@app.route('/')
def index():
    return workspaces()

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


@app.errorhandler(404)
def page_not_found(e):
    return redirect('/')

@app.errorhandler(500)
def empty_element_detected(e):
    return render_template('error-handle.html')

if __name__ == "__main__":
  app.debug = True
  app.run()