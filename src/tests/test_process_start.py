import pytest
import subprocess
import sys
from src.app.llm_registry import start_model_instance

def test_start_model_instance():
    model = "test_model"
    model_type = "test_type"

    process = start_model_instance(model, model_type)
    assert process is not None
    assert isinstance(process, subprocess.Popen)

    process.terminate()
    process.wait()
