import ansible_runner
import app.clients.wrapper_client as wrapper_client
from app.utils.logger import console_logger

def execute_ansible_playbook_with_config(host: str, user: str, password: str) -> bool:
    
    playbook_path = "./app/ansible/install_wrapper.ansible.yml"
    try:
        #check if the host has ansible installed
        if not wrapper_client.check_if_ansible_is_installed(host, password, user):
            #install ansible
            if not wrapper_client.install_ansible(host, password, user):
                console_logger.error("Ansible konnte nicht installiert werden")
                return
        
        result = ansible_runner.run(
            private_data_dir=".",
            playbook=playbook_path,
            inventory=None,  # Inventory wird nicht benötigt, wir übergeben direkt
            extravars={
                "ansible_user": user,
                "ansible_password": password
            },
            cmdline=f"-i {host},"
        )

        if result.status == "successful":
            console_logger.info(f"Playbook erfolgreich ausgeführt auf {host}")
            return True
        else:
            console_logger.error(f"Fehler beim Ausführen: {result.stdout.read()}")
            return False
    except Exception as e:
        console_logger.error(f"Fehler beim Ausführen: {e}")
        return False