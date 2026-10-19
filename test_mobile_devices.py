import os
import sys

if sys.stdout:
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
from playwright.sync_api import sync_playwright

VIEWPORTS = [
    {"name": "iPhone_SE_375px", "width": 375, "height": 667},
    {"name": "iPhone_14_Pro_393px", "width": 393, "height": 852},
    {"name": "Galaxy_S20_412px", "width": 412, "height": 915},
    {"name": "iPad_Mini_768px", "width": 768, "height": 1024},
    {"name": "Desktop_1440px", "width": 1440, "height": 900}
]

os.makedirs("mobile_test_results", exist_ok=True)

def run_tests():
    print("=======================================================")
    print("📱 RUNNING DEEP MOBILE & DEVICE OPTIMIZATION AUDIT")
    print("=======================================================\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for vp in VIEWPORTS:
            ctx = browser.new_context(viewport={"width": vp["width"], "height": vp["height"]})
            page = ctx.new_page()
            url = "http://127.0.0.1:8050/demo?agency=Al-Haram+Real+Estate&city=Karachi&mode=builder&theme=light"
            page.goto(url, wait_until="networkidle")

            # Check horizontal overflow
            scroll_width = page.evaluate("() => document.documentElement.scrollWidth")
            client_width = page.evaluate("() => document.documentElement.clientWidth")
            has_overflow = scroll_width > client_width

            # Check settings panel minimized state
            is_collapsed = page.evaluate("() => document.getElementById('settings-panel').classList.contains('collapsed')")
            trigger_text = page.evaluate("() => document.getElementById('settings-trigger').innerText")

            # Check footer copyright
            foot_text = page.evaluate("() => document.getElementById('footer-all-rights').innerText")

            screenshot_path = f"mobile_test_results/{vp['name']}.png"
            page.screenshot(path=screenshot_path)

            status = "✅ PASS" if not has_overflow else "❌ FAIL (Overflow)"
            print(f"[{status}] {vp['name']} ({vp['width']}x{vp['height']}):")
            print(f"   • Scroll Width: {scroll_width}px | Client Width: {client_width}px (Overflow: {has_overflow})")
            print(f"   • Settings Bar Minimized by Default: {is_collapsed} (Label: '{trigger_text.strip()}')")
            print(f"   • Footer Text: '{foot_text.strip()}'")
            print(f"   • Screenshot: {screenshot_path}\n")

            # Test Toggle Click
            page.click("#settings-trigger")
            page.wait_for_timeout(400)
            is_open = page.evaluate("() => !document.getElementById('settings-panel').classList.contains('collapsed')")
            arrow_after = page.evaluate("() => document.getElementById('trigger-arrow').innerText")
            print(f"   [Toggle Test] Clicked trigger -> Opened: {is_open}, Arrow: '{arrow_after}'")

            ctx.close()

        browser.close()
    print("🎉 All device viewports tested successfully!")

if __name__ == '__main__':
    run_tests()
