import sys
if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.on("console", lambda msg: print("CONSOLE:", msg.type, msg.text))
    page.add_init_script("""
        window.addEventListener('error', function(e) {
            console.log('UNCAUGHT_ERR:', e.message, 'LINE:', e.lineno, 'COL:', e.colno, 'STACK:', e.error ? e.error.stack : 'none');
        });
    """)
    page.goto("http://127.0.0.1:8050/demo?agency=DHA+Prime+Estates&city=Lahore&mode=agency&theme=light")
    page.wait_for_timeout(1000)
    browser.close()
