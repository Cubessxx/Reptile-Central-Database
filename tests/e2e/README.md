# Playwright E2E Suite

This suite drives the real Streamlit UI in a real browser and verifies database outcomes with raw SQL.

## Prerequisites

Install test dependencies:

```powershell
py -3 -m pip install pytest playwright
py -3 -m playwright install chromium
```

## Run (visible browser)

Default behavior is headed mode with slow motion so you can watch it happen.

```powershell
py -3 -m pytest tests/e2e/test_full_site_playwright.py -s
```

## Useful options

- Faster / hidden browser:

```powershell
$env:E2E_HEADLESS='1'
$env:E2E_SLOW_MO='0'
py -3 -m pytest tests/e2e/test_full_site_playwright.py -s
```

- Use an already-running Streamlit app (instead of auto-start):

```powershell
$env:E2E_BASE_URL='http://127.0.0.1:8501'
py -3 -m pytest tests/e2e/test_full_site_playwright.py -s
```

## Notes

- The fixture auto-starts `streamlit run frontend/Home.py` if `E2E_BASE_URL` is not set.
- Tests intentionally write data via UI and validate outcomes via SQL, then clean up.
- The final reset test validates that baseline seed counts are restored.
