import sys
if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("http://127.0.0.1:8050/demo?agency=DHA+Prime+Estates&city=Lahore&mode=agency&theme=light")
    page.wait_for_timeout(500)
    print("Logo Badge:", page.evaluate("() => document.getElementById('logo-badge-icon').innerText"))
    print("Header Company:", page.evaluate("() => document.getElementById('header-company-name').innerText"))
    print("Hero City:", page.evaluate("() => document.getElementById('hero-city-text').innerText"))
    print("Footer Copy:", page.evaluate("() => document.getElementById('footer-all-rights').innerText"))
    browser.close()
