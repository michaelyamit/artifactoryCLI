#!/Users/amitm/sample/venv-pythonProject/bin/python3.7
from base64 import b64encode

import requests
from argparse import ArgumentParser
from requests.structures import CaseInsensitiveDict
import json
import os
import sys


def get_admin_token():
    f_admin = open("keys.txt", "r")
    lines = f_admin.readlines()
    admin_token = lines[0].strip()
    f_admin.close()
    return admin_token


def get_temp_token():
    f_temp = open("tempToken.txt", "r")
    lines = f_temp.readlines()
    temp_token = lines[0].strip()
    f_temp.close()
    return temp_token


def generate_token(username):
    url = f"https://{args.server}.jfrog.io/artifactory/api/security/token"
    headers = CaseInsensitiveDict()
    headers["Authorization"] = "Basic YWRtaW46UGFzc3dvcmQ="
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    data = f"username={username}&expires_in=0&scope=member-of-groups:\"readers\""
    resp = requests.post(url, headers=headers, data=data)
    temp_token = (resp.json()["access_token"])
    print("Token generated.")
    return temp_token


def get_token_id():
    url = f"https://{args.server}.jfrog.io/artifactory/api/security/token"
    headers = CaseInsensitiveDict()
    headers["Authorization"] = "Basic YW1pdG1AamZyb2cuY29tOkFtaXQxNTEwIQ=="
    resp = requests.get(url, headers=headers)
    temp_token = (resp.json()["tokens"][0]["token_id"])
    return temp_token


def revoke_token(token_id):
    url = f"https://{args.server}.jfrog.io/artifactory/api/security/token/revoke"
    headers = CaseInsensitiveDict()
    headers["Authorization"] = "Basic YW1pdG1AamZyb2cuY29tOkFtaXQxNTEwIQ=="
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    data = f"username={args.server}&expires_in=0&scope=member-of-groups:\"readers\"&token_id={token_id}"
    resp = requests.post(url, headers=headers, data=data)
    print("Token has been deleted!")


def validate_user_password(user, password):
    url = "https://amitmichaely.jfrog.io/artifactory/api/system/ping"
    headers = CaseInsensitiveDict()
    headers["Authorization"] = "Basic {}".format(b64encode(bytes(f"{user}:{password}", "utf-8")).decode("ascii"))
    resp = requests.get(url, headers=headers)

    if resp.status_code == 200:
        print("Password correct... ")
        return True
    else:
        print("Password incorrect... ")
        return False


def check_if_user_exist(user):
    url = f"https://{args.server}.jfrog.io/artifactory/api/security/users/{user}"
    headers = CaseInsensitiveDict()
    headers["Authorization"] = 'Bearer ' + X_JFrog_Token
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        print("User exists...")
        return True
    else:
        print("User doesn't exists...")
        return False


def check_admin_or_temp_user_for_token():
    if args.user == 'admin':
        main_token = get_admin_token()
    else:
        main_token = get_temp_token()
    return main_token


def api_request(api, token, state, content_type):
    url = f"https://{args.server}.jfrog.io/artifactory/{api}"
    headers = CaseInsensitiveDict()
    if token == 'token':
        headers["Authorization"] = 'Bearer ' + check_admin_or_temp_user_for_token()
    if content_type == 'content_type':
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
    return response


parser = ArgumentParser(description='Manage an Artifactory SaaS instance')

parser.add_argument('--server', '-s', type=str, help="Server name", default='amitmichaely')
parser.add_argument('--user', '-u',  type=str, help="The user name", required=True)
parser.add_argument('--password', '-p',  type=str, help="The user password", required=True)
parser.add_argument('--ping', action='store_true', help="System Ping")
parser.add_argument('--version', action='store_true', help="Get Artifactory version")
parser.add_argument('--createuser', '-cu',  type=str, help="Enter a new user name")
parser.add_argument('--deleteuser', '-du',  type=str, help="Enter a user name to delete")
parser.add_argument('--storageinfo', '-si', action='store_true', help="Get Storage Summary Info")

args = parser.parse_args()

file = open("keys.txt", "r+")
file_len = file.read()


if os.stat("keys.txt").st_size == 0:  # There isn't a admin token
    file.write(generate_token('admin'))
    admin_token_flag = True
file.close()

X_JFrog_Token = get_admin_token()
temp_JFrog_Token = ''
admin_token_flag = False

# make an health check - ping
if args.ping and check_if_user_exist(args.user) and validate_user_password(args.user, args.password):
    resp2 = api_request('api/system/ping', None, 'GET', None).status_code
    if resp2 == 200:
        print("OK")
    else:
        print("BAD")

# return the artifactory version if flag is true
if args.version and check_if_user_exist(args.user) and validate_user_password(args.user, args.password):
    resp3 = (api_request('api/system/version', 'token', 'GET', None))
    print(resp3.json()["version"])

# create a new user
if args.createuser is not None and check_if_user_exist(args.user) and validate_user_password(args.user, args.password):
    data_set = {}
    data_set['email'] = input("Enter an email ").lower().strip()
    data_set['password'] = input("Enter a password ").strip()
    #data_set['admin'] = "false"
    json_dump = json.dumps(data_set)
    print(json_dump)
    if not check_if_user_exist(args.createuser):
        resp4 = api_request(f'api/security/users/{args.createuser}', 'token', 'PUT', 'content_type').status_code
        temp_JFrog_Token = generate_token(args.createuser)
        f = open("tempToken.txt", "a")
        f.seek(0)
        f.truncate()
        f.write(temp_JFrog_Token)
        f.close

        if resp4 == 200 or resp4 == 201:
            print(f"User {args.createuser} created. ")
        elif resp4 == 401:
            print("401")
    else:
        print("The user already exists. doing nothing.")

# Delete a user
if args.deleteuser is not None and check_if_user_exist(args.user) and validate_user_password(args.user, args.password):
    if check_if_user_exist(args.deleteuser):
        resp5 = api_request(f'api/security/users/{args.deleteuser}', 'token', 'DELETE', None).status_code
        print(f"User {args.deleteuser} removed. ")
    else:
        print("The user does not exist. Doing nothing.")

# Get Storage Summary Info
if args.storageinfo and check_if_user_exist(args.user) and validate_user_password(args.user, args.password):
    resp6 = (api_request('api/storageinfo', 'token', 'GET', None))
    print(resp6.json())

# delete the admin token in the end
if admin_token_flag:
    token_to_revoke = get_token_id()
    revoke_token(token_to_revoke)
