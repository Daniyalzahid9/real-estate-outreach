"""
test_send_to_user.py
Direct verification script to send a test pitch to +923218218521.
"""

import sys
import os
import time
import urllib.parse

# Windows UTF-8 console output
if sys.stdout:
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from whatsapp_auto_outreach import get_message_for_lead

TEST_PHONE = "923218218521"
PROFILE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "whatsapp_user_profile"))

# Sample test lead data
SAMPLE_LEAD_URDU = {
    "name": "Al-Haram Real Estate & Builders",
    "contact": "Daniyaal",
    "city": "Karachi",
    "area": "Gulshan-e-Iqbal",
    "opportunity": "No official website, relying on Facebook page",
    "clean_wa": TEST_PHONE
}

SAMPLE_LEAD_ENGLISH = {
    "name": "Elysium Towers & International Developers Pvt Ltd",
    "contact": "Director Sales",
    "city": "Karachi",
    "area": "Clifton",
    "opportunity": "Commercial & Residential High-Rise Developer",
    "clean_wa": TEST_PHONE
}

def generate_test_links():
    lang_u, msg_u = get_message_for_lead(SAMPLE_LEAD_URDU)
    lang_e, msg_e = get_message_for_lead(SAMPLE_LEAD_ENGLISH)

    link_u = f"https://wa.me/{TEST_PHONE}?text={urllib.parse.quote(msg_u)}"
    link_e = f"https://wa.me/{TEST_PHONE}?text={urllib.parse.quote(msg_e)}"

    print(f"\n=======================================================")
    print(f"📱 TEST OUTREACH FOR NUMBER: +{TEST_PHONE}")
    print(f"=======================================================\n")
    
    print(f"Option 1: [Respectful Roman Urdu Pitch]")
    print(f"-------------------------------------------------------")
    print(f"{msg_u}\n")
    print(f"👉 Direct 1-Click Link:\n{link_u}\n")

    print(f"Option 2: [Corporate English Pitch]")
    print(f"-------------------------------------------------------")
    print(f"{msg_e}\n")
    print(f"👉 Direct 1-Click Link:\n{link_e}\n")

def send_via_playwright():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ Playwright not installed. Run: pip install playwright && playwright install chromium")
        return

    lang, msg = get_message_for_lead(SAMPLE_LEAD_URDU)
    encoded = urllib.parse.quote(msg)
    url = f"https://web.whatsapp.com/send?phone={TEST_PHONE}&text={encoded}"

    print(f"🚀 Opening Chrome to send live test message to +{TEST_PHONE}...")
    print(f"If this is your first time, WhatsApp Web will show a QR code to link once.\n")

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            viewport={"width": 1280, "height": 800},
            args=["--no-sandbox"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.goto(url, wait_until="domcontentloaded")

        print("Waiting for WhatsApp Web chat to load...")
        try:
            send_btn_selector = 'button[aria-label="Send"], span[data-icon="send"]'
            page.wait_for_selector(send_btn_selector, timeout=60000)
            time.sleep(3) # Human pause
            page.locator(send_btn_selector).first.click()
            print(f"\n✅ Message sent successfully to +{TEST_PHONE}!")
            time.sleep(5)
        except Exception as e:
            print(f"\n⚠️ Status: WhatsApp Web is waiting for QR login or chat load: {e}")
            print("Please scan the QR code on screen if prompted.")
            # Keep browser open for 30s to allow manual scan
            time.sleep(30)
        finally:
            browser.close()

if __name__ == '__main__':
    if '--send' in sys.argv:
        send_via_playwright()
    else:
        generate_test_links()
