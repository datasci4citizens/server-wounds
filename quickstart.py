#!/usr/bin/env python3

r"""
    This python script file is meant exclusively for development use.

    USE FROM SERVER-WOUNDS ROOT DIRECTORY | as it depends on .env

    
    Commands:

    - python quickstart.py
        > initialize both server and database.

    - python quickstart.py db
        > database-only startup

    - python quickstart.py api
        > server-only startup (django still needs an active database to startup)

    - python quickstart.py sql
        > automatically starts database if needed.
        > execute a psql terminal inside database docker:
        > here you can run SQL queries directly on database
        > you can also use "\?" inside the terminal for additional options (press q to leave help menu)
        > type "\q" to leave psql terminal and go back to your usual terminal.

    - python quickstart.py test <testname>
        > runs a specific test or all tests if no testname is given
        > make sure to type the exact test name
        > you can also test a specific method of a test case, by doing <testcasename.testcasemethodname>
        > e.g. "AuthenticationTests.PostUser" | this will ONLY run the PostUser test, contained in the authenticationtests testcases
"""

import os
import subprocess
import sys
from time import sleep

import dotenv




def compose_base_cmd():
    "The base command that correlates .env file with compose file"

    return [
        "docker",
        "compose",
        "--env-file",
        ".env",
        "-f",
        "docker/docker-compose.yml",
    ]

def sudo(cmd):
    "adds sudo to the command based on user operating system"

    if os.name == "nt":
        return cmd
    return ["sudo", *cmd]


def is_db_running() -> bool:

    cmd = ["pg_isready", "-h", "localhost" , "-q"]
    result = subprocess.run(cmd, cwd=".").returncode

    if result == 0:
        return True
        
    else:
        return False

def is_server_running() -> bool:

    cmd = sudo([*compose_base_cmd(), "ps", "--services", "--filter", "status=running"])

    response = (subprocess.run(cmd, cwd=".", capture_output=True, text=True).stdout).split()
    for service in response:
        if service == 'web':
            return True
    
    return False


def run_sql_terminal_in_docker_db():
    "runs the command to initialize psql, autostarts database if not online"

    if not is_db_running():
        print("starting up Database...")
        startup("db")

        while(not is_db_running()):
            sleep(5)
        print("Database Online, initializing psql...")

    dotenv.load_dotenv()

    user = os.environ.get("SERVER_WOUNDS_DB_USER")
    database_name = os.environ.get("SERVER_WOUNDS_DATABASE")
    
    cmd = sudo( [*compose_base_cmd(),
                 "exec",
                 "db",
                 "psql",
                 "-U",
                 user,
                 "-d",
                 database_name
            ]   )
    
    return subprocess.run(cmd , cwd=".").returncode
    

def startup(service_name):
    " starts up database and/or django server using .env parameters"


    cmd = sudo( [*compose_base_cmd(), "up", "-d"])

    if(len(service_name)):
        cmd = [*cmd, service_name]


    return subprocess.run(cmd, cwd=".").returncode


def run_test(test_name):
    if ( not is_db_running) or (not is_server_running):
        startup("")

    cmd = sudo([*compose_base_cmd(), "exec", "web", "python", "citizens_project/manage.py", "test", test_name])

    return subprocess.run(cmd, cwd=".").returncode

if __name__ == "__main__":

    if(len(sys.argv)) < 2:

        print("starting up database and server")
        sys.exit(startup(""))

    function = sys.argv[1]

    match function:
        case "db":
            print("inicializando banco de dados")
            sys.exit(startup("db"))

        case "api":
            print("inicializando servidor")
            sys.exit(startup("web"))

        case "sql":
            sys.exit(run_sql_terminal_in_docker_db())

        case "test":
            if len(sys.argv) > 2:
                testcase =  "app_cicatrizando.tests." + sys.argv[2]
            else:
                testcase = "app_cicatrizando"
            sys.exit(run_test(testcase))
