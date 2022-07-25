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

## dependencies

All needed dependencies are noted in the '<a href="requirements.txt">requirements.txt</a>' file.

In order to install all of them, type the following command:

`pip install -r requirements.txt`

## deployment

Clone the project:

`git clone https://github.com/Elbrus-Analytics/snmp-manager.git`

Go to the project directory:

`cd snmp-manager`

### setup

  - run '<a href="src/install.sh">install.sh</a>'
  - check if the '.env' file has been correctly created
    - if not: add a '.env' file corresponding to '<a href=".env.example">.env.example</a>'

### Option 1: Automatic execution of the script

#### deployment
  - set custom user in <a href="snmp-manager.service.example">snmp-manager.service.example</a> if needed
  - set custom times in <a href="src/snmp-manager.timer.example">snmp-manager.timer.example</a> if needed

Copy the service script

```bash
    cp src/snmp-manager.service.example /etc/systemd/system/snmp-manager.service
```

Copy the scheduler

```bash
    cp src/snmp-manager.timer.example /etc/systemd/system/snmp-manager.timer
```

Reload systemctl daemon

```bash
    systemctl daemon-reload
```

Enable the service

```bash
    systemctl enable snmp-manager.service
```
- should create a output like the following:

    ```bash
        Created symlink /etc/systemd/system/multi-user.target.wants/snmp-manager.service → /etc/systemd/system/snmp-manager.service.
    ```

Enable the timer

```bash
    systemctl enable snmp-manager.timer
```

Start the timer

```bash
    systemctl start snmp-manager.timer
```

Check if timer is running

```bash
    systemctl status snmp-manager.timer
```

#### The elb-snmp-manager.sh script should now be automatically executed in the interval which is declared in 'snmp-manager.timer'  

### Option 2: Manual execution

run manager script

```bash
    src/elb-snmp-manager.sh
```