from flask import Flask, request, render_template
from flask_modals import Modal
import Include
import requests

from requests import api
#import scanner, get_tcp_adapter
#from spherov2 import scanner
#from spherov2.adapter.tcp_adapter import get_tcp_adapter
#from spherov2.sphero_edu import SpheroEduAPI
#
#
#with scanner.find_toy(adapter=get_tcp_adapter('localhost')) as toy:
#    ...

app =  Flask(__name__)
modal = Modal(app)
api_url = "http://localhost:8080"

@app.route('/')
def index():
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
    return workspaces()

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    return render_template("edit-environment.html")

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