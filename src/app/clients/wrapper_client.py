'''
This webclient is responsible for sending requests to the LLM Wrapper.
'''

from typing import Dict
import requests
import json
from app.utils.logger import console_logger
import paramiko

def deploy_llm(llm_address: str, llm_config: Dict):
    '''
    Sends a POST request to the LLM Wrapper to deploy a new LLM instance.
    :param llm_address: Address of the LLM Wrapper
    :param llm_config_json: JSON configuration of the LLM
    :return: Response from the LLM Wrapper
    '''
    try:
        console_logger.info(f"Deploying LLM to {llm_address}")
        console_logger.info(f"LLM config: {llm_config}")
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"http://{llm_address}:8000/deploy", data=llm_config, headers=headers, timeout=300)
        if response.status_code == 200:
            console_logger.info(f"LLM deployed successfully: {response.content}")
            return response.json()["status"]    
        else:
            console_logger.error(f"Failed to deploy LLM: {response.content}")
            return "failure"

    except Exception as e:
        console_logger.error(f"An exception occurred: {e}")
        return None
    
def stop_llm(llm_address: str):
    '''
    Sends a POST request to the LLM Wrapper to stop the LLM instance.
    :param llm_address: Address of the LLM Wrapper
    :return: Response from the LLM Wrapper
    '''
    try:
        #with a timeout of 5 minutes
        
        console_logger.info(f"Stopping LLM at {llm_address}")
        response = requests.post(f"http://{llm_address}:8000/shutdown", timeout=300)
        if response.status_code == 200:
            console_logger.info(f"LLM stopped successfully: {response.json()}")
            return response.json()["status"]
        else:
            console_logger.error(f"Failed to stop LLM: {response.json()}")
            return "failure"

    except Exception as e:
        console_logger.error(f"An exception occurred: {e}")
        return None

def check_status(llm_address: str):
    '''
    Sends a GET request to the LLM Wrapper to check the status of the LLM instance.
    :param llm_address: Address of the LLM Wrapper
    :return: Response from the LLM Wrapper
    '''
    try:
        response = requests.get(f"http://{llm_address}:8000/get_status")
        if response.status_code == 200:
            console_logger.info(f"LLM status: {response.content}")
            return response.json()["message"]
        else:
            console_logger.error(f"Failed to get LLM status: {response.content}")
            return "failure"

    except Exception as e:
        console_logger.error(f"An exception occurred: {e}")
        return None
    


def stop_wrapper(wrapper_ip: str, wrapper_password: str, wrapper_username: str) -> bool:
    """
    Connects to the LLM Wrapper via SSH and stops the LLM Wrapper service.

    :param wrapper_ip: IP address (oder Hostname) des Servers mit dem LLM Wrapper
    :param wrapper_password: SSH-Passwort für den Server
    :param wrapper_username: SSH-Benutzer
    :return: Ausgabe des Stop-Befehls (stdout) oder Fehlermeldung (stderr)
    """
    # SSH-Client anlegen
    ssh_client = paramiko.SSHClient()
    # Automatisch unbekannte Hosts akzeptieren (in produktiven Umgebungen sorgfältiger konfigurieren!)
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Verbindung aufbauen
        ssh_client.connect(
            hostname=wrapper_ip,
            username=wrapper_username,
            password=wrapper_password,
            timeout=10
        )

        # Beispiel: Service beenden via systemd
        # Passe den Befehl an deine Service-Bezeichnung an, z.B. "sudo systemctl stop llm-wrapper"
        command = "sudo systemctl stop llm-wrapper"

        stdin, stdout, stderr = ssh_client.exec_command(command)

        # Optional: Falls das Passwort für sudo erneut erforderlich ist
        # könntest du hier z.B. stdin.write(f"{wrapper_password}\n")
        # und stdin.flush() ausführen.

        # Ausgaben einsammeln
        out = stdout.read().decode("utf-8").strip()
        err = stderr.read().decode("utf-8").strip()

        if err:
            console_logger.error(f"An error occurred: {err}")
            return False
        else:
            console_logger.info(f"Command output: {out}")
            return True
        

    except Exception as e:
        console_logger.error(f"An exception occurred: {e}")
        return False
    finally:
        ssh_client.close()
        
def restart_llm_wrapper(wrapper_ip: str, wrapper_password: str, wrapper_username: str) -> bool:
    """
    Connects to the LLM Wrapper via SSH and restarts the LLM Wrapper service.

    :param wrapper_ip: IP address (oder Hostname) des Servers mit dem LLM Wrapper
    :param wrapper_password: SSH-Passwort für den Server
    :param wrapper_username: SSH-Benutzer
    :return: Ausgabe des Restart-Befehls (stdout) oder Fehlermeldung (stderr)
    """
    # SSH-Client anlegen
    ssh_client = paramiko.SSHClient()
    # Automatisch unbekannte Hosts akzeptieren (in produktiven Umgebungen sorgfältiger konfigurieren!)
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Verbindung aufbauen
        ssh_client.connect(
            hostname=wrapper_ip,
            username=wrapper_username,
            password=wrapper_password,
            timeout=10
        )

        # Beispiel: Service neustarten via systemd
        # Passe den Befehl an deine Service-Bezeichnung an, z.B. "sudo systemctl restart llm-wrapper"
        command = "sudo systemctl restart llm-wrapper"

        stdin, stdout, stderr = ssh_client.exec_command(command)

        # Optional: Falls das Passwort für sudo erneut erforderlich ist
        # könntest du hier z.B. stdin.write(f"{wrapper_password}\n")
        # und stdin.flush() ausführen.

        # Ausgaben einsammeln
        out = stdout.read().decode("utf-8").strip()
        err = stderr.read().decode("utf-8").strip()

        if err:
            console_logger.error(f"An error occurred: {err}")
            return False
        else:
            console_logger.info(f"Command output: {out}")
            return True
        

    except Exception as e:
        console_logger.error(f"An exception occurred: {e}")
        return False
    finally:
        ssh_client.close()

def execute_ssh_command(wrapper_ip: str, username: str, password: str, command: str):
    """
    Führt einen SSH-Befehl auf einer Zielmaschine aus.
    :param wrapper_ip: IP-Adresse oder Hostname der Zielmaschine
    :param username: SSH-Benutzername
    :param password: SSH-Passwort
    :param command: Der auszuführende Befehl
    :return: Tuple (stdout, stderr, exit_status)
    """
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh_client.connect(hostname=wrapper_ip, username=username, password=password, timeout=10)
        stdin, stdout, stderr = ssh_client.exec_command(command)

        out = stdout.read().decode("utf-8").strip()
        err = stderr.read().decode("utf-8").strip()
        exit_status = stdout.channel.recv_exit_status()  # Exit-Code abrufen

        return out, err, exit_status
    except Exception as e:
        return None, str(e), -1
    finally:
        ssh_client.close()

        
def deploy_fastapi_service(wrapper_ip: str, username: str, password: str):
    """
    Bereitstellung des FastAPI-Service für den LLM Wrapper auf einer Zielmaschine via SSH.
    :param wrapper_ip: IP-Adresse oder Hostname der Zielmaschine
    :param username: SSH-Benutzername
    :param password: SSH-Passwort
    """
    repo_url = "https://github.com/gflachs/GreenPrompt_LLM_Wrapper.git"
    branch = "main"
    service_name = "llm-wrapper"
    app_directory = "/opt/llm-wrapper"
    service_port = 8000
    python_exec = "/usr/bin/python3"

    tasks = [
        {
            "name": "Install necessary packages",
            "command": "sudo apt-get update && sudo apt-get install -y python3 python3-pip git ufw"
        },
        {
            "name": "Ensure application directory exists",
            "command": f"sudo mkdir -p {app_directory} && sudo chown {username}:{username} {app_directory}"
        },
        {
            "name": "Clone or update the Python application from GitHub",
            "command": f"""
            if [ -d "{app_directory}/.git" ]; then
                cd {app_directory} && sudo git reset --hard && sudo git pull
            else
                sudo rm -rf {app_directory} && sudo git clone -b {branch} {repo_url} {app_directory}
            fi
            """
        },
        {
            "name": "Install Python dependencies",
            "command": f"cd {app_directory} && sudo {python_exec} -m pip install -r requirements.txt"
        },
        {
            "name": "Open port using UFW",
            "command": f"sudo ufw allow {service_port}/tcp"
        },
        {
            "name": "Create systemd service file",
            "command": f"""echo '[Unit]
            Description=FastAPI Service for LLM Wrapper
            After=network.target

            [Service]
            ExecStart={python_exec} -m uvicorn src.app.main:app --host 0.0.0.0 --port {service_port}
            WorkingDirectory={app_directory}
            Restart=always
            Environment=PYTHONUNBUFFERED=1
            Environment=PYTHONPATH={app_directory}

            [Install]
            WantedBy=multi-user.target' | sudo tee /etc/systemd/system/{service_name}.service"""
        },
        {
            "name": "Reload systemd",
            "command": "sudo systemctl daemon-reload"
        },
        {
            "name": "Enable and start FastAPI service",
            "command": f"sudo systemctl enable {service_name} && sudo systemctl start {service_name}"
        }
    ]

    for task in tasks:
        console_logger.info(f"Executing task: {task['name']} on {wrapper_ip}")
        out, err, exit_status = execute_ssh_command(wrapper_ip, username, password, task['command'])
        
        if exit_status != 0:  # Überprüfe den Exit-Code
            console_logger.info(f"Task '{task['name']}' failed: {err}")
            return False
        else:
            console_logger.info(f"Task '{task['name']}' succeeded: {out}")
    
    return True
