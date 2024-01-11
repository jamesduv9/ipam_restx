# IPAM RESTx
![Alt text](./coverage.svg)
<img src="./coverage.svg">
## Introduction
IPAM RESTx is a Flask-based IP Address Management (IPAM) REST API. This project is designed for educational purposes, created while studying for the Cisco DevNet Expert certification. Created to better understand RESTful API design. Not suggested for use in production networks.

## Features
- User Authentication and Authorization
- CRUD operations for network resources (VRFs, subnets, supernets, addresses)
- RESTful API design
- Database integration using SQLAlchemy
- Unit tests for all API endpoints

## Installation

### Prerequisites
- Python 3.6 or higher
- Pip (Python package installer)
- Virtual environment (recommended)
- SQLite (for local testing and development)

### Setting Up the Environment
1. Clone the repository:
   ```
   git clone https://github.com/jamesduv9/ipam_restx.git
   ```
2. Navigate to the project directory:
   ```
   cd ipam_restx
   ```
3. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   ```
4. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On Unix or MacOS:
     ```
     source venv/bin/activate
     ```
5. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration
Before running the application, ensure the environment is properly configured:
- Set the `MASTER_APIKEY` environment variable for initial setup and authentication.

## Running the Application
1. Start the application:
   ```
   python app.py
   ```
2. The application will start on `http://localhost:8080`.

## Docker
A Dockerfile is also provided, you will need to adjust the configuration to include volumes, or setup an external db to keep persistant data.

## API Endpoints
The following are the primary endpoints provided by the API:
- Authentication: `/auth/login`, `/auth/register`, `/auth/authorize`, `/auth/delete`, `/auth/user-status`
- VRF Management: `/api/v1/vrf`
- Subnet Management: `/api/v1/subnet`
- Supernet Management: `/api/v1/supernet`
- Address Management: `/api/v1/address`
- RPC actions: `api/v1/rpc/getUsableAddresses`, `/api/v1/rpc/getUsableSubnet`

Swagger documentation is available at - `/doc`

## Getting an API key
User accounts are associated to a username and password and are not granted long term apikeys, the user must login using the `/auth/login` route. This request will respond with `X-Ipam-Apikey` in the response body, this apikey must be present in subsequent requests

CURL example:
```
curl -X POST "http://127.0.0.1:8080/auth/login" \ 
    -d '{"username":"admin","password":"password"}' \
    -H "Content-Type: application/json"

Response:
{
    "data": {
        "X-Ipam-Apikey": "Z6TZUdPim5cI3hA14Cb8Fw",
        "expiration": "Tue, 09 Jan 2024 00:44:12 GMT",
        "permission_level": 15
    },
    "status": "Success"
}
```

## Permissions / Registration / Authorization
Permissions are based on different levels ranging 0-15 and checked via the @apikey_validate decorator. In general priv 15 is used for creating new accounts and approvals, 10 is used for write operations, and 5 is used for read. When the application is first launched, a default admin account with privilege level 15 is created with username "admin" and password set to the MASTER_APIKEY env variable. The default admin will always be created on launch as long as there is not another privilege level 15 account

To register a new privilege 15 user do the following:
1. User register to use the app using the authentication URI `/auth/register`
2. Default admin or other privilege level 15 account can authorize the user, and set his permissions at `/auth/authorize`
3. The new privilege 15 user can now delete the default administrator account

CURL example:
```
#1. Get the default admin's Apikey
curl -X POST "http://127.0.0.1:8080/auth/login" -d '{"username":"admin","password":"password"}' -H "Content-Type: application/json" --silent | jq
{
  "data": {
    "X-Ipam-Apikey": "Vfp_0TsOf_vPVkZQiVnvvA",
    "expiration": "Tue, 09 Jan 2024 15:36:38 GMT",
    "permission_level": 15
  },
  "status": "Success"
}

#2. Register a new user
curl -X POST "http://127.0.0.1:8080/auth/register" -d '{"username":"new_user","password":"new_user"}' -H "Content-Type: application/json"
{
    "status":"Success"
}

#3. Set the new user's permissions with apikey set
curl -X POST "http://127.0.0.1:8080/auth/authorize" -d '{"username": "new_user", "permission_level": 15}' -H "Content-Type: application/json" -H "X-Ipam-Apikey: Vfp_0TsOf_vPVkZQiVnvvA" --silent | jq
{
  "status": "Success"
}

#4. Login as new user
curl -X POST "http://127.0.0.1:8080/auth/login" -d '{"username":"new_user","password":"new_user"}' -H "Content-Type: application/json" --silent | jq
{
  "data": {
    "X-Ipam-Apikey": "eqwgqycU8m8WHITnMN2ChA",
    "expiration": "Tue, 09 Jan 2024 15:41:45 GMT",
    "permission_level": 15
  },
  "status": "Success"
}
```

## CLI
A basic CLI is provided using click "cli.py" with all api functionality. The cli should provide sufficient documentation through --help

```
Usage: cli.py [OPTIONS] COMMAND [ARGS]...

  Interacts with the ipam_restx api through requests library

Options:
  --help  Show this message and exit.

Commands:
  auth       Access the menu for auth routes - /auth
  ipam-crud  Access the menu for CRUD operations on the IPAM - /api/v1/
  rpc        Access the menu for rpc routes - /api/v1/rpc
```

## Testing
Unit tests for each endpoint are created through pytest, perform a test from the application's root directory:
```
pytest
```


