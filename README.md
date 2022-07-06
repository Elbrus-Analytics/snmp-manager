# snmp-manager

## Usage

The snmp-manager is used to frequently send snmp-requests towards multiple different network devices like routers and
switches. In order to do so, it's important to use the correct snmp version and config to reach the snmp-clients. The
snmp-manager is simply being called by a linux job which calls the needed scripts regularly.

## Installation

### virtual environment:

Install the virtual environment: `python -m venv ./venv`

Activate it: `source venv/bin/activate`

Deactivate it: `deactivate`

## Dependencies

All needed dependencies are noted in the <a href="requirements.txt">requirements</a>.

In order to install them, type the following command:

`pip install -r requirements.txt`
