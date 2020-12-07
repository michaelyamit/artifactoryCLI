#!/Users/amitm/sample/venv-pythonProject/bin/python3.7

import requests
from argparse import ArgumentParser
from requests.structures import CaseInsensitiveDict
import json
import os

f = open(".gitignore", "r")
X_JFrog_Token = f.read()
print(X_JFrog_Token)
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


# Token
url = f"https://{args.user}.jfrog.io/artifactory/api/security/apiKey"
headers = CaseInsensitiveDict()
headers["Authorization"] = X_JFrog_Token
resp = requests.get(url, headers=headers)
print(resp.status_code)

# make an health check - ping
if args.ping == 't':
    url2 = f"https://{args.user}.jfrog.io/artifactory/api/system/ping"
    headers = CaseInsensitiveDict()
    resp2 = requests.get(url2, headers=headers)
    if(resp2.status_code == 200):
        print ("OK")
    else:
        print ("BAD")


# return the artifactory version if flag is true
#if args.version == 'y':
url3 = f"https://{args.user}.jfrog.io/artifactory/api/system/version"
headers = CaseInsensitiveDict()
headers["Authorization"] = X_JFrog_Token
resp3 = requests.get(url3, headers=headers)
#print(resp3.status_code)
print(resp3.json()["version"])


# create a new user
if args.createuser != None:

    data_set = {}
    data_set['email'] = input ("Enter an email ").lower().strip()
    data_set['password'] = input ("Enter a password ").lower().strip()
    json_dump = json.dumps(data_set)
    print(json_dump)

    url4 = f"https://{args.user}.jfrog.io/artifactory/api/security/users/{args.createuser}"
    headers = CaseInsensitiveDict()
    headers["Authorization"] = X_JFrog_Token
    headers["Content-Type"] = "application/json"

    resp4 = requests.put(url4, headers=headers, data=json_dump)
    print(resp4.status_code)

    print(url4)


# Delete a user
if args.deleteuser != None:
    url5 = f"https://{args.user}.jfrog.io/artifactory/api/security/users/{args.deleteuser}"
    headers = CaseInsensitiveDict()
    headers["Authorization"] = X_JFrog_Token
    resp5 = requests.delete(url5, headers=headers)

    print(resp5.status_code)
    print(f"{args.deleteuser} removed successfully")


# Get Storage Summary Info
if args.storageinfo != None:
    url6 = f"https://{args.user}.jfrog.io/artifactory/api/storageinfo"
    headers = CaseInsensitiveDict()
    headers["Authorization"] = X_JFrog_Token
    resp6 = requests.get(url6, headers=headers)
    print(resp.status_code)
    print(resp6.json())

