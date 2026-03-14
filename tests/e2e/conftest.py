import os
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen

import pytest
from playwright.sync_api import sync_playwright

from backend.db import get_engine


REPO_ROOT = Path(__file__).resolve().parents[2]


def _wait_for_server(base_url: str, timeout_seconds: int = 90) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            req = Request(base_url, method="GET")
            with urlopen(req, timeout=2) as response:
                if 200 <= response.status < 500:
                    return
        except Exception:
            time.sleep(0.5)
    raise TimeoutError(f"Timed out waiting for Streamlit server at {base_url}")


@pytest.fixture(scope="session")
def streamlit_base_url():
    external_url = os.getenv("E2E_BASE_URL")
    if external_url:
        _wait_for_server(external_url)
        yield external_url
        return

    port = int(os.getenv("E2E_PORT", "8501"))
    base_url = f"http://127.0.0.1:{port}"
    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "frontend/Home.py",
        "--server.port",
        str(port),
        "--server.headless",
        "true",
        "--browser.gatherUsageStats",
        "false",
    ]
    process = subprocess.Popen(
        command,
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        _wait_for_server(base_url)
        yield base_url
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except Exception:
            process.kill()


@pytest.fixture(scope="session")
def browser():
    headless = os.getenv("E2E_HEADLESS", "0") == "1"
    slow_mo = int(os.getenv("E2E_SLOW_MO", "250"))

    with sync_playwright() as playwright:
        chromium = playwright.chromium
        browser = chromium.launch(headless=headless, slow_mo=slow_mo)
        try:
            yield browser
        finally:
            browser.close()


@pytest.fixture()
def page(browser, streamlit_base_url):
    context = browser.new_context(viewport={"width": 1600, "height": 1000})
    page = context.new_page()
    page.goto(streamlit_base_url, wait_until="networkidle")
    yield page
    context.close()


@pytest.fixture(scope="session")
def db_engine():
    return get_engine()
