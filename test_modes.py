import sys
if sys.stdout:
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
from playwright.sync_api import sync_playwright

def test_modes():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()

        # 1. Builder Dark
        page.goto("http://127.0.0.1:8050/demo?agency=Emaar+Crescent+Bay&city=Karachi&mode=builder&theme=dark", wait_until="networkidle")
        page.screenshot(path="mobile_test_results/Builder_Dark_1440px.png")
        print("✅ Captured Builder Dark 1440px")

        # 2. Agency Light
        page.goto("http://127.0.0.1:8050/demo?agency=DHA+Prime+Estates&city=Lahore&mode=agency&theme=light", wait_until="networkidle")
        page.screenshot(path="mobile_test_results/Agency_Light_1440px.png")
        print("✅ Captured Agency Light 1440px")

        # 3. Agency Dark
        page.goto("http://127.0.0.1:8050/demo?agency=DHA+Prime+Estates&city=Lahore&mode=agency&theme=dark", wait_until="networkidle")
        page.screenshot(path="mobile_test_results/Agency_Dark_1440px.png")
        print("✅ Captured Agency Dark 1440px")

        browser.close()
    print("All mode tests complete!")

if __name__ == '__main__':
    test_modes()
