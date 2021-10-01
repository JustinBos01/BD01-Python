from flask import Flask, request, render_template
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
api_url = "http://localhost:8080"

@app.route('/', methods=['GET', 'POST'])
def index():
    response = requests.get(api_url)
    json_string = response.json()
    return render_template("create-environment.html", value = json_string)          

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    return render_template("edit-environment.html")

@app.route('/users', methods=['GET', 'POST'])
def users():
    response = requests.get(api_url+"/users")
    json_string = response.json()
    return render_template('create-users.html', users = json_string)

@app.route('/users/create/<username>/<password>', methods=['POST'])
def create_user():
    json_string = {"userName": request.args.get('username'), "password": request.args.get('password')}
    response = requests.post(api_url, json=json_string)
    return