import ansible_runner

def execute_ansible_playbook(playbook_path, inventory_path, extra_vars=None):
    """
    Führt ein Ansible-Playbook mit ansible-runner aus.
    :param playbook_path: Pfad zum Ansible-Playbook
    :param inventory_path: Pfad zur Inventory-Datei
    :param extra_vars: Dictionary mit zusätzlichen Variablen
    :return: Ergebnis des Playbook-Laufs
    """
    try:
        # Ansible-Runner starten
        result = ansible_runner.run(
            private_data_dir=".",  # Arbeitsverzeichnis
            playbook=playbook_path,
            inventory=inventory_path,
            extravars=extra_vars,
        )

        # Ergebnisse auswerten
        if result.status == "successful":
            print(f"Playbook executed successfully: {result.status}")
            return {
                "status": "success",
                "rc": result.rc,
                "stdout": result.stdout.read(),
            }
        else:
            print(f"Playbook execution failed: {result.status}")
            return {
                "status": "failure",
                "rc": result.rc,
                "stdout": result.stdout.read(),
                "stderr": result.stderr.read() if result.stderr else "",
            }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }