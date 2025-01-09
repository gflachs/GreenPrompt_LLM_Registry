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
        llm_config_json = json.dumps(llm_config)
        response = requests.post(f"http://{llm_address}/deploy", json=llm_config_json)
        if response.status_code == 200:
            console_logger.info(f"LLM deployed successfully: {response.json()}")
            return response.json()["status"]
        else:
            console_logger.error(f"Failed to deploy LLM: {response.json()}")
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
        response = requests.post(f"http://{llm_address}/stop")
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
        response = requests.get(f"http://{llm_address}/status")
        if response.status_code == 200:
            console_logger.info(f"LLM status: {response.json()}")
            return response.json()["status"]
        else:
            console_logger.error(f"Failed to get LLM status: {response.json()}")
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
