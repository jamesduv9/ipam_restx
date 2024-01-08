# IPAM RESTx

## Introduction
IPAM RESTx is a Flask-based IP Address Management (IPAM) REST API. This project is designed for educational purposes, created while studying for the Cisco DevNet Expert certification. Created to better understand RESTful API design. 

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
- Configure the database URI in `app.py` if not using SQLite.

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
- Authentication: `/auth/login`, `/auth/register`
- VRF Management: `/vrf`
- Subnet Management: `/subnet`
- Supernet Management: `/supernet`
- Address Management: `/address`
- RPC actions: `/rpc`

Swagger documentation is available at - `/doc`

## Testing
Run the unit tests to ensure everything is working correctly:
```
pytest
```

