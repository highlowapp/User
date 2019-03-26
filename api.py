from flask import Flask, request
from User import User
import requests

app = Flask(__name__)

#MySQL credentials
host = "MySQLhostname"
username = "username"
password = "password"
database = "database"

@app.route("/get/<string:property>", methods=["POST"])
def get(property):
    #Get token from Authorization
    token = request.headers["Authorization"].replace("Bearer ", "")

    #Create the headers
    headers = { 'Authorization': "Bearer " + token }

    #Make a request to the Auth service
    token_verification_request = requests.post("https://auth_service/verify_token", headers=headers)

    #Obtain the result as JSON
    result = token_verification_request.json()

    #If there was an error, return the error
    if "error" in result:
        return "{ 'error': '" + result["error"] + "' }"

    #Otherwise, get the user
    user = User(result["uid"], host, username, password, database)

    #Get the specified property
    prprty = getattr(user, property)

    return "{ '" + property + "': '" + prprty + "'}"


@app.route("/set/<string:property>", methods=["POST"])
def set(property):
    #Get token from Authorization
    token = request.headers["Authorization"].replace("Bearer ", "")

    #Create the headers
    headers = { 'Authorization': "Bearer " + token }

    #Make a request to the Auth service
    token_verification_request = requests.post("https://auth_service/verifyt_token", headers=headers)

    #Obtain the result as JSON
    result = token_verification_request.json()

    #If there was an error, return the error
    if "error" in result:
        return "{ 'error': '" + result["error"] + "' }"


    #Otherwise, get the user
    user = User(result["uid"], host, username, password, database)

    #Set the specified property
    user.set_column(property, request.form["value"])

    return "{ 'status': 'success' }"



if __name__ == '__main__':
    app.run(host='0.0.0.0', port='80')