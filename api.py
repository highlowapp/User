from flask import Flask, request
from User import User
import requests

app = Flask(__name__)

@app.route("/get_user", methods=["POST"])
def get_user():
    #Create a payload
    payload = { 'token': request.form["token"] }

    #Make a request to the Auth service
    token_verification_request = requests.get("https://auth_service/verify_token", params=payload)

    #Obtain the result as JSON
    result = token_verification_request.json()

    #If there was an error, return the error
    if "error" in result:
        return "{ 'error': '" + result["error"] + "' }"

    return "{ uid: '" + result["uid"] + "' }"


