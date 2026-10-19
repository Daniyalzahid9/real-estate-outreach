"""
whatsapp_playwright_runner.py
Antigravity Automated WhatsApp Outreach Engine using Persistent Browser Session.

Architecture:
1. Persistent Chrome Session: Uses a dedicated user data folder ('./whatsapp_user_profile')
   so you only scan the WhatsApp QR code once.
2. Scheduled Batch Execution:
   - Morning Window (11:30 AM - 1:30 PM PKT): Builders & Developers (Corporate English / Roman Urdu)
   - Evening Window (6:30 PM - 9:00 PM PKT): Real Estate Agencies & Brokers (Respectful Roman Urdu)
3. Anti-Ban Guardrails:
   - 65-110s randomized human delay between sends
   - Max 12-15 messages per batch
   - Custom dynamic messaging per lead
4. First-Touch Handoff:
   - Sends Message #1 only.
   - Leaves chat immediately so you handle all live replies on your phone.
"""

import os
import sys
import time
import random
import urllib.parse
from datetime import datetime

# Windows UTF-8 stdout configuration
if sys.stdout:
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from whatsapp_auto_outreach import load_leads_from_excel, get_message_for_lead, EXCEL_FILE

PROFILE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "whatsapp_user_profile"))

def check_playwright():
    try:
        from playwright.sync_api import sync_playwright
        return True
    except ImportError:
        return False

def setup_login_session():
    """
    Launches a visible Chromium window so the user can scan the WhatsApp Web QR code once.
    The session is saved in PROFILE_DIR.
    """
    if not check_playwright():
        print("❌ Playwright is not installed. Please run: pip install playwright && playwright install chromium")
        return False

    from playwright.sync_api import sync_playwright
    print(f"\n=======================================================")
    print(f"📱 WHATSAPP WEB ONE-TIME QR AUTHENTICATION")
    print(f"📁 Session Storage: {PROFILE_DIR}")
    print(f"=======================================================\n")
    print("Opening browser window... Please scan the QR code with your WhatsApp app.")
    print("Settings -> Linked Devices -> Link a Device\n")

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            viewport={"width": 1280, "height": 800},
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.goto("https://web.whatsapp.com")

        print("Waiting for WhatsApp Web to load...")
        try:
            # Wait until the chats pane / search box is visible (meaning user is logged in)
            page.wait_for_selector('div[role="textbox"], #side', timeout=120000)
            print("\n✅ WhatsApp Web authenticated successfully! Session permanently saved.")
            time.sleep(3)
        except Exception as e:
            print("⚠️ Timeout or window closed before QR scan was verified.")
        finally:
            browser.close()

    return True

def run_automated_batch(batch_name="Morning Batch", max_leads=12, headless=False):
    """
    Executes automated outreach for a specific batch using the saved persistent session.
    """
    if not check_playwright():
        print("❌ Playwright is not installed. Please run: pip install playwright && playwright install chromium")
        return False

    if not os.path.exists(PROFILE_DIR):
        print(f"❌ No saved WhatsApp session found in {PROFILE_DIR}!")
        print("Please run first: python whatsapp_playwright_runner.py --login")
        return False

    from playwright.sync_api import sync_playwright
    import openpyxl

    leads = load_leads_from_excel()
    candidates = [l for l in leads if l['batch'] == batch_name and l['status'] == 'Not Contacted']

    if not candidates:
        print(f"ℹ️ No pending leads for {batch_name}!")
        return True

    batch = candidates[:max_leads]
    print(f"\n🚀 Launching outreach for {len(batch)} leads in {batch_name}...")

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=headless,
            viewport={"width": 1280, "height": 800},
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()

        for idx, lead in enumerate(batch, 1):
            lang, msg, angle_type = get_message_for_lead(lead)
            phone = lead['clean_wa']
            encoded_msg = urllib.parse.quote(msg)
            url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_msg}"

            print(f"\n[{idx}/{len(batch)}] Processing Lead #{lead['id']}: {lead['name']}")
            print(f"   📞 Phone: +{phone} | 🌐 Strategy: {angle_type} | Mode: {lang}")
            print(f"   💬 Message 1 (Zero-Link Opener):\n   {msg.replace(chr(10), chr(10)+'   ')}")

            try:
                page.goto(url, wait_until="domcontentloaded")
                
                # Wait for the send button or input box
                # WhatsApp Web send button selector
                send_btn_selector = 'button[aria-label="Send"], span[data-icon="send"]'
                page.wait_for_selector(send_btn_selector, timeout=35000)
                
                # Small human hesitation before clicking send
                time.sleep(random.uniform(2.5, 4.5))
                
                send_btn = page.locator(send_btn_selector).first
                send_btn.click()
                print(f"   ✅ First message sent successfully to {lead['name']}!")
                
                # 1. Update persistent JSON logs (100% immune to Excel file locks)
                try:
                    import json
                    # Update contacted_blacklist.json
                    bl_file = "contacted_blacklist.json"
                    bl = {}
                    if os.path.exists(bl_file):
                        try:
                            with open(bl_file, 'r', encoding='utf-8') as f:
                                bl = json.load(f)
                        except Exception:
                            bl = {}
                    bl[lead['clean_wa']] = {
                        "id": str(lead['id']),
                        "name": lead['name'],
                        "sent_at": datetime.now().isoformat(),
                        "language": lang,
                        "strategy": angle_type,
                        "batch": batch_name,
                        "status": "Contacted"
                    }
                    with open(bl_file, 'w', encoding='utf-8') as f:
                        json.dump(bl, f, indent=2, ensure_ascii=False)
                    print(f"   🔒 Added to permanent contacted_blacklist.json (Exclusion Guaranteed)")
                except Exception as bl_err:
                    print(f"   ⚠️ Could not update blacklist: {bl_err}")

                # 2. Update status in Excel file (both Quick Table & Master sheet)
                try:
                    wb = openpyxl.load_workbook(EXCEL_FILE)
                    for sname in ['WhatsApp Quick Outreach Table', 'Master Leads & WhatsApp']:
                        if sname in wb.sheetnames:
                            ws = wb[sname]
                            headers = [str(ws.cell(1, c).value or '').strip() for c in range(1, ws.max_column + 1)]
                            if 'Outreach Status' in headers:
                                status_col = headers.index('Outreach Status') + 1
                                ws.cell(lead['row_idx'], status_col, "Contacted")
                    wb.save(EXCEL_FILE)
                    print(f"   📝 Updated Excel row {lead['row_idx']} status -> 'Contacted' in both sheets")
                except Exception as ex_err:
                    print(f"   ⚠️ Could not update Excel status (File might be open in Excel): {ex_err}")

            except Exception as e:
                print(f"   ❌ Failed to send to {lead['name']}: {str(e)[:80]}")

            # Anti-ban human jitter delay before next lead
            if idx < len(batch):
                delay = random.randint(65, 105)
                print(f"   ⏳ Anti-ban safety: Pausing for {delay} seconds before next contact...")
                time.sleep(delay)

        browser.close()

    print(f"\n🎉 Batch {batch_name} complete! Antigravity has stepped back. All replies will appear on your phone.")
    return True

if __name__ == '__main__':
    args = sys.argv[1:]
    if '--login' in args:
        setup_login_session()
    elif '--batch' in args:
        b_idx = args.index('--batch') + 1
        b_val = args[b_idx] if b_idx < len(args) else 'morning'
        batch_type = "Morning Batch" if 'morn' in b_val.lower() else "Evening Baithak"
        run_automated_batch(batch_name=batch_type)
    else:
        print("Usage:")
        print("  1. One-time QR Login:  python whatsapp_playwright_runner.py --login")
        print("  2. Run Morning Batch:  python whatsapp_playwright_runner.py --batch morning")
        print("  3. Run Evening Batch:  python whatsapp_playwright_runner.py --batch evening")
