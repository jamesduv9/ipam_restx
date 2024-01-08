"""
Author: James Duvall
Purpose: Simple cli built to interact with the 
ipam_restx flask application through requests
Caveat: Not ready yet, still implementing commands
"""
import os
import click
import logging
import requests
import yaml
from pprint import pprint

# These three env variables must be set
IPAM_HOST = os.getenv("IPAM_HOST")
IPAM_APIKEY = os.getenv("IPAM_APIKEY")

if not IPAM_HOST:
    logging.error(
        "No IPAM_HOST environment variable set, all requests will fail. Exiting.")
    exit()

BASE_URL = f"http://{IPAM_HOST}:8080"
BASE_HEADERS = {"Content-type": "application/json"}
if not IPAM_APIKEY:
    logging.error(
        "No IPAM_APIKEY environment variable set, please issue (cli.py auth login --username X --password Y) to set \n")
else:
    BASE_HEADERS["X-Ipam-Apikey"] = IPAM_APIKEY

def print_yaml(data):
    """
    Using this function when I'm too lazy to create a pretty way to print the data
    """
    yaml_data = yaml.dump(data, default_flow_style=False, sort_keys=False)
    print(yaml_data)

def default_failed_response(added_response:str=""):
    response = f"Something went wrong, please validate your inputs and try again. {added_response}"
    print(response)

@click.group()
def main_menu():
    """
    Interacts with the ipam_restx api through requests library
    """


@main_menu.group()
def auth():
    """
    Access the menu for auth routes - /auth
    """

@main_menu.group()
def rpc():
    """
    Access the menu for rpc routes - /api/v1/rpc
    """

@main_menu.group()
def ipam_crud():
    """
    Access the menu for CRUD operations on the IPAM - /api/v1/
    """

@ipam_crud.group()
def vrf():
    """
    Access the menu for CRUD operations for VRFs
    """

@ipam_crud.group()
def supernet():
    """
    Access the menu for CRUD operations for supernets
    """

@ipam_crud.group()
def subnet():
    """
    Access the menu for CRUD operations for subnets
    """

@ipam_crud.group()
def address():
    """
    Access the menu for CRUD operations for addresses
    """

@vrf.command(name="delete")
@click.option("--vrf-name", help="name of the vrf you'd like to delete", type=click.STRING)
@click.option("--id", help="id of the vrf you'd like to delete")
def delete_vrf(vrf_name: str, id: int) -> None:
    """
    /api/v1/vrf DELETE
    Delete a single vrf
    """
    q_params = ""
    if vrf_name:
        q_params = f"?name={vrf_name}"
    elif id:
        q_params = f"?id={vrf_name}"
    else:
        print("id or vrf_name must be provided")
        exit()
    response = requests.delete(f"{BASE_URL}/api/v1/vrf{q_params}", headers=BASE_HEADERS)
    if response.status_code != 200 or response.json().get("status") == "Failed":
        default_failed_response()
        exit()
    print("Succesfully deleted VRF")

@vrf.command(name="get")
@click.option("--vrf-name", help="name of the vrf you'd like to see details of", type=click.STRING)
@click.option("--id", help="id of the vrf you'd like to see details of")
def get_vrf(vrf_name: str, id: int) -> None:
    """
    /api/v1/vrf GET
    View single vrf or all vrfs, output in yaml 
    """
    q_params = ""
    if vrf_name:
        q_params = f"?name={vrf_name}"
    elif id:
        q_params = f"?id={vrf_name}"
    response = requests.get(f"{BASE_URL}/api/v1/vrf{q_params}", headers=BASE_HEADERS)
    if response.status_code != 200:
        default_failed_response()
        exit()
    print_yaml(response.json().get("data"))

@vrf.command(name="create")
@click.option("--vrf-name", help="name of the vrf you'd like to create", required=True, type=click.STRING)
def create_vrf(vrf_name: str) -> None:
    """
    /api/v1/vrf POST
    Create new vrf
    """
    request_body = {"name": vrf_name}
    response = requests.post(
        f"{BASE_URL}/api/v1/vrf", json=request_body, headers=BASE_HEADERS
    ).json()
    if response.get("errors"):
        print("The following error(s) occured:")
        for error in response.get("errors"):
            print(error)
    else:
        print(f"VRF {vrf_name} successfully created")

@auth.command(name="authorize")
@click.option("--username", help="Username of the target account", required=True, prompt=True)
@click.option("--permission-level", help="Permission level 0-15 for the account", required=True, prompt=True, type=click.INT)
def authorize(username: str, permission_level: int) -> None:
    """
    /auth/authorize
    Authorize a new user and set permission level
    """
    request_body = {"username": username, "permission_level": permission_level}
    response = requests.post(
        f"{BASE_URL}/auth/authorize", json=request_body, headers=BASE_HEADERS
    ).json()
    if response.get("errors"):
        print("The following error(s) occured:")
        for error in response.get("errors"):
            print(error)
    else:
        print(f"User {username} now successfully active with the set permission level of {permission_level}")


@auth.command(name="register")
@click.option("--username", help="Username of your ipam account", required=True, prompt=True)
@click.option("--password", help="Password of your ipam account", required=True, prompt=True, hide_input=True)
def register(username: str, password: str) -> None:
    """
    /auth/register
    Register a new (inactive) user. 
    User will not be active until authorized by priv 15 user
    """
    request_body = {"username": username, "password": password}
    response = requests.post(
        f"{BASE_URL}/auth/register", json=request_body, headers=BASE_HEADERS
    ).json()
    if response.get("errors"):
        print("The following error(s) occured:")
        for error in response.get("errors"):
            print(error)
    else:
        print(f"User {username} registered successfully, now awaiting admin approval")

@auth.command(name="login")
@click.option("--username", help="Username of your ipam account", required=True, prompt=True)
@click.option("--password", help="Password of your ipam account", required=True, prompt=True, hide_input=True)
def login(username: str , password: str) -> None:
    """
    /auth/login
    login and retrieve new apikey
    """
    request_body = {"username": username, "password": password}
    response = requests.post(
        f"{BASE_URL}/auth/login", json=request_body, headers=BASE_HEADERS)
    data = response.json().get("data", {})
    if data.get("X-Ipam-Apikey"):
        print(
            f'Your apikey is - "{data.get("X-Ipam-Apikey")}" Please set this as your IPAM_APIKEY environmental variable')
        print(f'This token will expire at {data.get("expiration")}')
        print(
            f'Your current permission level is {data.get("permission_level")}')
    else:
        default_failed_response()

if __name__ == "__main__":
    main_menu()
