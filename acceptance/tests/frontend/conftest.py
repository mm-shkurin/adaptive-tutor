import os
import socket
import subprocess
import tempfile
import time
from pathlib import Path

import httpx
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

pytest.register_assert_rewrite("statements.document_library_statements")
pytest.register_assert_rewrite("statements.signed_in_browser_statements")

from statements.document_library_statements import DocumentLibraryStatements
from statements.signed_in_browser_statements import SignedInBrowserStatements
from support.acceptance_server import AcceptanceServer

FRONTEND = Path(__file__).resolve().parents[3] / "frontend"


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _chrome():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1400,1000")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1400, 1000)
    driver.set_page_load_timeout(30)
    return driver


def _start_vite(port: int, api_target: str, log_handle):
    env = os.environ.copy()
    env["VITE_API_PROXY_TARGET"] = api_target
    env["FRONTEND_PORT"] = str(port)
    env["BROWSER"] = "none"
    return subprocess.Popen(
        ["npm.cmd", "run", "dev"],
        cwd=FRONTEND,
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=log_handle,
        stderr=subprocess.STDOUT,
    )


def _wait_http(url: str, proc, log_path: str) -> None:
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(_log_tail(log_path))
        try:
            response = httpx.get(url, timeout=0.5)
            if response.status_code == 200:
                return
        except httpx.HTTPError:
            time.sleep(0.2)
            continue
        time.sleep(0.2)
    raise RuntimeError(_log_tail(log_path))


def _log_tail(log_path: str) -> str:
    with open(log_path, encoding="utf-8", errors="replace") as handle:
        return handle.read()[-2000:]


def _stop_process(proc) -> None:
    if proc.poll() is not None:
        return
    subprocess.run(
        ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


@pytest.fixture
def ui():
    server = AcceptanceServer()
    server.start()
    descriptor, log_path = tempfile.mkstemp(prefix="vite-documents-", suffix=".log")
    os.close(descriptor)
    log_handle = open(log_path, "w", encoding="utf-8")
    vite = None
    driver = None
    signed_in = None
    try:
        port = _free_port()
        vite = _start_vite(port, server.base_url, log_handle)
        app_url = f"http://127.0.0.1:{port}"
        _wait_http(app_url, vite, log_path)
        driver = _chrome()
        signed_in = SignedInBrowserStatements(driver, app_url, server.base_url, server.provider)
        library = DocumentLibraryStatements(driver)
        yield signed_in, library
    finally:
        if signed_in is not None:
            signed_in.close()
        if driver is not None:
            driver.quit()
        if vite is not None:
            _stop_process(vite)
        log_handle.close()
        server.stop()
        Path(log_path).unlink(missing_ok=True)


@pytest.fixture
def signed_in_browser(ui):
    return ui[0]


@pytest.fixture
def document_library(ui):
    return ui[1]
