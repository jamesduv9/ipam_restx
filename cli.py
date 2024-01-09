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
from ipaddress import IPv4Network, IPv4Address, AddressValueError
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

@rpc.command("get_usable_subnet")
@click.option("--vrf", help="Target VRF of the supernet you want an subnet from, must also include network", default="Global", show_default=True)
@click.option("--network", help="Target supernet CIDR prefix you want an address from, must also include VRF")
@click.option("--id", help="ID of the supernet you want an subnet from, can be only arg")
@click.option("--name", help="name of the supernet you want an subnet from, can be only arg")
@click.option("--cidr_length", help="CIDR prefix length of the subnet you want", type=click.INT)
@click.option("--all", help="If true, recieve all available subnets within the supernet at the request cidr_length", type=click.BOOL, default=False, is_flag=True, show_default=True)
def get_usable_subnet(vrf: str, network: str, id: int, name: str, cidr_length: int, all: bool) -> None:
    """
    /api/v1/rpc/getUsableSubnet
    Given a supernet, will return usable subnets at the requested cidr_length
    Must include vrf + network || id || name
    """
    q_params = ""
    if vrf and network:
        try: 
            IPv4Network(network)
        except AddressValueError:
            print("Provided network is not in correct format, example - 192.168.0.0/16")
            exit()
        q_params = f"?network={network}&vrf={vrf}"
    elif id:
        q_params = f"?id={id}"
    elif name:
        q_params = f"?name={name}"
    else:
        print("Must provide name, id, or vrf+network")
        exit()
    if not cidr_length:
        print("Must provide cidr_length")
        exit()
    q_params += f"&cidr_length={cidr_length}"
    q_params += f"&all={all}"
    print(q_params)
    response = requests.get(f"{BASE_URL}/api/v1/rpc/getUsableSubnet{q_params}", headers=BASE_HEADERS).json()
    if response.get("errors"):
        print("The following error(s) occured:")
        for error in response.get("errors"):
            print(error)
    else:
        print_yaml(response.get("data"))

@rpc.command("get_usable_address")
@click.option("--vrf", help="Target VRF of the subnet you want an address from, must also include network")
@click.option("--network", help="Target subnet CIDR prefix you want an address from, must also include VRF")
@click.option("--id", help="ID of the subnet you want an address from, can be only arg")
@click.option("--name", help="name of the subnet you want an address from, can be only arg")
def get_usable_address(vrf: str, network: str, id: int, name: str) -> None:
    """
    /api/v1/rpc/getUsableAddress
    Given a subnet will return first usable and all available subnets
    Must include vrf + network || id || name
    """
    q_params = ""
    if vrf and network:
        try: 
            IPv4Network(network)
        except AddressValueError:
            print("Provided network is not in correct format, example - 192.168.0.0/16")
            exit()
        q_params = f"?network={network}&vrf={vrf}"
    elif id:
        q_params = f"?id={id}"
    elif name:
        q_params = f"?name={name}"
    else:
        print("Must provide name, id, or vrf+network")
        exit()
    
    response = requests.get(f"{BASE_URL}/api/v1/rpc/getUsableAddresses{q_params}", headers=BASE_HEADERS).json()
    if response.get("errors"):
        print("The following error(s) occured:")
        for error in response.get("errors"):
            print(error)
    else:
        print_yaml(response.get("data"))


@address.command("delete")
@click.option("--name", help="Delete address with this name")
@click.option("--id", help="Delete address with this id", type=click.INT)
def delete_address(name:str, id:int) -> None:
    """
    /api/v1/address DELETE
    delete single address by id or name
    """
    q_params = ""
    if name:
        q_params = f"?name={name}"
    elif id:
        q_params = f"?id={id}"
    else:
        print("id or vrf_name must be provided")
        exit()
    response = requests.delete(f"{BASE_URL}/api/v1/address{q_params}", headers=BASE_HEADERS).json()
    if response.get("errors"):
        print("The following error(s) occured:")
        for error in response.get("errors"):
            print(error)
    else:
        print("Succesfully deleted address")

@address.command("get")
@click.option("--vrf-name", help="Get addresss with this vrf", default="Global")
@click.option("--name", help="Get address with this name")
@click.option("--id", help="Get address with this id", type=click.INT)
def get_address(vrf_name, name:str, id:int) -> None:
    """
    /api/v1/address GET
    View single address, all addresss, or all address by vrf
    output in yaml 
    """
    q_params = ""
    if name:
        q_params = f"?name={name}"
    elif id:
        q_params = f"?id={id}"
    elif vrf_name:
        q_params = f"?vrf={vrf_name}"
    response = requests.get(f"{BASE_URL}/api/v1/address{q_params}", headers=BASE_HEADERS)
    if response.status_code != 200:
        default_failed_response()
        exit()
    print_yaml(response.json().get("data"))

@address.command(name="create")
@click.option("--vrf-name", help="VRF this address is attached to", default="Global", show_default=True)
@click.option("--address", help="Network in cidr format ex. 192.168.0.0/16", required=True)
@click.option("--name", help="Name associated with this address", required=True)
def create_address(vrf_name:str, address:str, name:str) -> None:
    """
    /api/v1/address POST
    Add a address
    """
    try:
        IPv4Address(address)
    except AddressValueError:
        print("Provided address is not in correct format, example - 192.168.10.10")
        exit()
    request_body = {"address": address, "name": name, "vrf": vrf_name}
    response = requests.post(f"{BASE_URL}/api/v1/address", headers=BASE_HEADERS, json=request_body).json()
    if response.get("errors"):
        print("The following error(s) occured:")
        for error in response.get("errors"):
            print(error)
    else:
        print("address successfully added")


@subnet.command("delete")
@click.option("--name", help="Delete subnet with this name")
@click.option("--id", help="Delete subnet with this id", type=click.INT)
def delete_subnet(name:str, id:int) -> None:
    """
    /api/v1/subnet DELETE
    delete single subnet by id or name
    """
    q_params = ""
    if name:
        q_params = f"?name={name}"
    elif id:
        q_params = f"?id={id}"
    else:
        print("id or vrf_name must be provided")
        exit()
    response = requests.delete(f"{BASE_URL}/api/v1/subnet{q_params}", headers=BASE_HEADERS).json()
    if response.get("errors"):
        print("The following error(s) occured:")
        for error in response.get("errors"):
            print(error)
    else:
        print("Succesfully deleted subnet")

@subnet.command("get")
@click.option("--vrf-name", help="Get subnets with this vrf", default="Global")
@click.option("--name", help="Get subnet with this name")
@click.option("--id", help="Get subnet with this id", type=click.INT)
def get_subnet(vrf_name, name:str, id:int) -> None:
    """
    /api/v1/subnet GET
    View single subnet, all subnets, or all subnet by vrf
    output in yaml 
    """
    q_params = ""
    if name:
        q_params = f"?name={name}"
    elif id:
        q_params = f"?id={id}"
    elif vrf_name:
        q_params = f"?vrf={vrf_name}"
    response = requests.get(f"{BASE_URL}/api/v1/subnet{q_params}", headers=BASE_HEADERS)
    if response.status_code != 200:
        default_failed_response()
        exit()
    print_yaml(response.json().get("data"))

@subnet.command(name="create")
@click.option("--vrf-name", help="VRF this subnet is attached to", default="Global", show_default=True)
@click.option("--network", help="Network in cidr format ex. 192.168.0.0/16", required=True)
@click.option("--name", help="Name associated with this subnet", required=True)
def create_subnet(vrf_name:str, network:str, name:str) -> None:
    """
    /api/v1/subnet POST
    Add a subnet
    """
    try:
        IPv4Network(network)
    except AddressValueError:
        print("Provided network is not in correct format, example - 192.168.0.0/16")
        exit()
    request_body = {"network": network, "name": name, "vrf": vrf_name}
    response = requests.post(f"{BASE_URL}/api/v1/subnet", headers=BASE_HEADERS, json=request_body).json()
    if response.get("errors"):
        print("The following error(s) occured:")
        for error in response.get("errors"):
            print(error)
    else:
        print("subnet successfully added")


@supernet.command("delete")
@click.option("--name", help="Delete supernet with this name")
@click.option("--id", help="Delete supernet with this id", type=click.INT)
def delete_supernet(name:str, id:int) -> None:
    """
    /api/v1/supernet DELETE
    delete single supernet by id or name
    """
    q_params = ""
    if name:
        q_params = f"?name={name}"
    elif id:
        q_params = f"?id={id}"
    else:
        print("id or vrf_name must be provided")
        exit()
    response = requests.delete(f"{BASE_URL}/api/v1/supernet{q_params}", headers=BASE_HEADERS).json()
    if response.get("errors"):
        print("The following error(s) occured:")
        for error in response.get("errors"):
            print(error)
    else:
        print("Succesfully deleted supernet")

@supernet.command("get")
@click.option("--vrf-name", help="Get supernets with this vrf", default="Global")
@click.option("--name", help="Get supernet with this name")
@click.option("--id", help="Get supernet with this id", type=click.INT)
def get_supernet(vrf_name, name:str, id:int) -> None:
    """
    /api/v1/supernet GET
    View single supernet, all supernets, or all supernet by vrf
    output in yaml 
    """
    q_params = ""
    if name:
        q_params = f"?name={name}"
    elif id:
        q_params = f"?id={id}"
    elif vrf_name:
        q_params = f"?vrf={vrf_name}"
    response = requests.get(f"{BASE_URL}/api/v1/supernet{q_params}", headers=BASE_HEADERS)
    if response.status_code != 200:
        default_failed_response()
        exit()
    print_yaml(response.json().get("data"))

@supernet.command(name="create")
@click.option("--vrf-name", help="VRF this supernet is attached to", default="Global", show_default=True)
@click.option("--network", help="Network in cidr format ex. 192.168.0.0/16", required=True)
@click.option("--name", help="Name associated with this supernet", required=True)
def create_supernet(vrf_name:str, network:str, name:str) -> None:
    """
    /api/v1/supernet POST
    Add a supernet
    """
    try:
        IPv4Network(network)
    except AddressValueError:
        print("Provided network is not in correct format, example - 192.168.0.0/16")
        exit()
    request_body = {"network": network, "name": name, "vrf": vrf_name}
    response = requests.post(f"{BASE_URL}/api/v1/supernet", headers=BASE_HEADERS, json=request_body).json()
    if response.get("errors"):
        print("The following error(s) occured:")
        for error in response.get("errors"):
            print(error)
    else:
        print("Supernet successfully added")


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
        q_params = f"?id={id}"
    else:
        print("id or vrf_name must be provided")
        exit()
    response = requests.delete(f"{BASE_URL}/api/v1/vrf{q_params}", headers=BASE_HEADERS).json()
    if response.get("errors"):
        print("The following error(s) occured:")
        for error in response.get("errors"):
            print(error)
    else:
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
        q_params = f"?id={id}"
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
