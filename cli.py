#!/Users/amitm/sample/venv-pythonProject/bin/python3.7

import requests
from argparse import ArgumentParser
from requests.structures import CaseInsensitiveDict
import json
import os
import sys



f = open(".gitignore", "r")
lines = f.readlines()
X_JFrog_Token = lines[0].strip()
f.close()

parser = ArgumentParser(description='Manage an Artifactory SaaS instance')

parser.add_argument('--user', '-u',  type=str, help="The user name", required=True)
parser.add_argument('--password', '-p',  type=str, help="The user password", required=True)
parser.add_argument('--ping',   help = "System Ping")
parser.add_argument('--version',  help="Get Artifactory version")
parser.add_argument('--createuser', '-cu',  type=str, help="Enter a new user name")
parser.add_argument('--deleteuser', '-du',  type=str, help="Enter a user name to delete")
parser.add_argument('--storageinfo', '-si',  type=str, help="Get Storage Summary Info")


args = parser.parse_args()

def generate_token(username, password):
    url = f"https://{args.user}.jfrog.io/artifactory/api/security/token"
    headers = CaseInsensitiveDict()
    headers["Authorization"] = "Basic YW1pdG1AamZyb2cuY29tOkFtaXQxNTEwIQ=="
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    data = f"username={username}&expires_in=0&scope=member-of-groups:\"readers\""
    resp = requests.post(url, headers=headers, data=data)
    temp_token = (resp.json()["access_token"])
    return temp_token

def get_token_id():
    url = f"https://{args.user}.jfrog.io/artifactory/api/security/token"
    headers = CaseInsensitiveDict()
    headers["Authorization"] = "Basic YW1pdG1AamZyb2cuY29tOkFtaXQxNTEwIQ=="
    resp = requests.get(url, headers=headers)
    temp_token = (resp.json()["tokens"][0]["token_id"])
    print(temp_token)

def revoke_token(username, token_id):
    url = f"https://{args.user}.jfrog.io/artifactory/api/security/token/revoke"
    headers = CaseInsensitiveDict()
    headers["Authorization"] = "Basic YW1pdG1AamZyb2cuY29tOkFtaXQxNTEwIQ=="
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    data = f"username={username}&expires_in=0&scope=member-of-groups:\"readers\"&token_id={token_id}"
    resp = requests.post(url, headers=headers, data=data)


def validate_user_details():
    f = open(".gitignore", "r")
    lines = f.readlines()
    Token = lines[0].strip()
    username = lines[1].strip()
    password = lines[2].strip()
    f.close()

    if (args.user == username and args.password == password):
        return True
    else:
        print ("Details incorrect... ")
        return False


def check_if_user_exist(user):
    url = f"https://{args.user}.jfrog.io/artifactory/api/security/users/{user}"
    headers = CaseInsensitiveDict()
    headers["Authorization"] = X_JFrog_Token
    resp = requests.get(url, headers=headers)
    if (resp.status_code == 200):
        return True
    else:
        return False

def api_request(api, token, state, content_type):
    url = f"https://{args.user}.jfrog.io/artifactory/{api}"
    headers = CaseInsensitiveDict()
    if (token == 'token'):
        headers["Authorization"] = X_JFrog_Token

    if (content_type == 'content_type'):
        headers["Content-Type"] = "application/json"

    if state == "GET":
        response = requests.get(url, headers=headers)
    elif state == "POST":
        response = requests.post(url, headers=headers)
    elif state == "PUT":
        response = requests.put(url, headers=headers, data=json_dump)
    elif state == 'DELETE':
        response = requests.delete(url, headers=headers)
    else:
        print("api=[%s] is not supported" % api)
        return False

    resp = requests.get(url, headers=headers)
    return resp

# Token
if args.user != None and validate_user_details():
    print(api_request('api/security/apiKey', 'token', 'GET', None).status_code)

# make an health check - ping
if args.ping == 't' and validate_user_details():
    resp2 = (api_request('api/system/ping', None, 'GET', None).status_code)
    if(resp2 == 200):
        print ("OK")
    else:
        print ("BAD")


# return the artifactory version if flag is true
if args.version == 'y' and validate_user_details():
    resp3 = (api_request('api/system/version', 'token', 'GET', None))
    print(resp3.json()["version"])


# create a new user
if args.createuser != None and validate_user_details():
    data_set = {}
    data_set['email'] = input ("Enter an email ").lower().strip()
    data_set['password'] = input ("Enter a password ").lower().strip()
    json_dump = json.dumps(data_set)
    print(json_dump)

    if not check_if_user_exist(args.createuser):
        resp4 = (api_request(f'api/security/users/{args.createuser}', 'token', 'PUT', 'content_type').status_code)
        print(f"User {args.createuser} created. ")
    else:
        print ("The user already exist. doing nothing.")

# Delete a user
if args.deleteuser != None and validate_user_details():
    if check_if_user_exist(args.deleteuser):
        resp5 = (api_request(f'api/security/users/{args.deleteuser}', 'token', 'DELETE', None).status_code)
        print(f"User {args.deleteuser} removed. ")
    else:
        print ("The user does not exist. Doing nothing.")


# Get Storage Summary Info
if args.storageinfo != None and validate_user_details():
    resp6 = (api_request('api/storageinfo', 'token', 'GET', None))
    print(resp6.json())