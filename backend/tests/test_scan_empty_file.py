# file: test_scan_empty_file.py

import os
import tempfile
import pytest
from backend.server import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_scan_valid_python_file(client):
    code = "def hello():\n    print('Hello')"

    with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w") as f:
        f.write(code)
        filepath = f.name

    try:
        with open(filepath, "rb") as file:
            data = {"file": (file, "hello.py")}
            response = client.post("/scan", content_type="multipart/form-data", data=data)

        print("Response status:", response.status_code)
        print("Response JSON:", response.json)

        assert response.status_code == 200

        response_data = response.json
        assert isinstance(response_data, dict)
        assert "vulnerabilities" in response_data
        assert isinstance(response_data["vulnerabilities"], list)
        assert len(response_data["vulnerabilities"]) > 0

    finally:
        if os.path.exists(filepath):
            os.unlink(filepath)

def test_scan_empty_file(client):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w") as f:
        filepath = f.name

    try:
        with open(filepath, "rb") as file:
            data = {"file": (file, "empty.py")}
            response = client.post("/scan", content_type="multipart/form-data", data=data)

        print("🧪 Empty file response:", response.json)

        response_data = response.json
        assert response.status_code == 200
        assert isinstance(response_data, dict)
        assert "vulnerabilities" in response_data
        assert isinstance(response_data["vulnerabilities"], list)
        assert len(response_data["vulnerabilities"]) > 0

    finally:
        if os.path.exists(filepath):
            os.unlink(filepath)

def test_scan_unsupported_file(client):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".exe", mode="w") as f:
        f.write("This is not code.")
        filepath = f.name

    try:
        with open(filepath, "rb") as file:
            data = {"file": (file, "not_code.exe")}
            response = client.post("/scan", content_type="multipart/form-data", data=data)

        print("🧪 Unsupported file response:", response.json)

        response_data = response.json
        assert response.status_code == 200
        assert isinstance(response_data, dict)
        assert "vulnerabilities" in response_data
        assert isinstance(response_data["vulnerabilities"], list)
        assert len(response_data["vulnerabilities"]) > 0

    finally:
        if os.path.exists(filepath):
            os.unlink(filepath)

def test_scan_insecure_python_code(client):
    insecure_code = "user_input = '1 + 1'\neval(user_input)"
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w") as f:
        f.write(insecure_code)
        filepath = f.name

    try:
        with open(filepath, "rb") as file:
            data = {"file": (file, "insecure.py")}
            response = client.post("/scan", content_type="multipart/form-data", data=data)

        print("🛡️ Insecure code response:", response.json)

        response_data = response.json
        assert response.status_code == 200
        assert isinstance(response_data, dict)
        assert "vulnerabilities" in response_data
        assert isinstance(response_data["vulnerabilities"], list)
        assert len(response_data["vulnerabilities"]) > 0

        # Check for detection of "eval" usage
        vulns = response_data["vulnerabilities"]
        assert any("eval" in ((v.get("title", "") + v.get("description", "") + v.get("recommendation", "")).lower()) for v in vulns)

    finally:
        if os.path.exists(filepath):
            os.unlink(filepath)
