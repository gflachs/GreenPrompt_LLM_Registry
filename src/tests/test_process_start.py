import pytest
import subprocess
import sys
import os

# temporary solution to get the function start_model_instance
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(BASE_DIR, 'src'))
from app.llm_registry import start_model_instance


def test_start_model_instance():
    model = "test_model"
    model_type = "test_type"
    process = start_model_instance(model, model_type)
    assert process is not None
    assert isinstance(process, subprocess.Popen)

    process.terminate()
    process.wait()

test_start_model_instance()


