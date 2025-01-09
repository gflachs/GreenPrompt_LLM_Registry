import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient


def test_app_lifespan_in_one_go():
    """
    Prüft Startup und Shutdown in *einem* Test, inklusive Aufrufen 
    von start_check_status/stop_check_status und start/shutdown.
    """
    with patch("app.main.llm_wrapper_status_service.start_check_status") as mock_start_check, \
         patch("app.main.llm_wrapper_status_service.stop_check_status") as mock_stop_check, \
         patch("app.main.llm_registry_service.start") as mock_registry_start, \
         patch("app.main.llm_registry_service.shutdown") as mock_registry_shutdown:

        # Jetzt erst importieren wir 'app', damit die oben gesetzten Patches greifen
        from app.main import app

        # 1) Erstellen des TestClients => Startup wird getriggert
        with TestClient(app) as client:
            # Direkt nach dem Erstellen sollte Startup bereits passiert sein:
            mock_start_check.assert_called_once()
            mock_registry_start.assert_called_once()

            # 2) Testen wir einen normalen Request
            resp = client.get("/")
            assert resp.status_code == 200
            assert resp.json() == {"message": "Hello World"}

        # 3) Beim Verlassen des `with TestClient(app)` => Shutdown
        #    Jetzt sollte stop_check_status & shutdown aufgerufen worden sein.
        mock_stop_check.assert_called_once()
        mock_registry_shutdown.assert_called_once()
