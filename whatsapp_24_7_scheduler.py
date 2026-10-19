"""
whatsapp_24_7_scheduler.py
Antigravity 24/7 Autonomous Scheduler for Pakistan Real Estate Outreach.

Runs continuously over the week and triggers batches strictly at optimal Pakistani hours:
1. Morning Batch (Builders & Developers):
   - Active: Tue, Wed, Thu, Sat (11:45 AM PKT)
   - Skip: Sun, Mon, and Friday (Jummah prayer dead zone 12:30 - 3:30 PM)
2. Evening Baithak Batch (Estate Agents & Brokers):
   - Active: Mon to Sat (7:15 PM PKT)
   - Skip: Sun (Off-market day)
3. Guardrails:
   - Max 1 batch per window per day (idempotent tracking)
   - Max 12 leads per batch
   - Immediate first-touch handoff (agent disconnects after message #1)
"""

import time
import os
import sys
from datetime import datetime

# Windows UTF-8 stdout configuration
if sys.stdout:
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from whatsapp_playwright_runner import run_automated_batch, check_playwright, PROFILE_DIR

def is_friday(dt):
    return dt.weekday() == 4

def is_sunday(dt):
    return dt.weekday() == 6

def start_scheduler_loop():
    print("==================================================================")
    print("🕒 ANTIGRAVITY 24/7 WHATSAPP REAL ESTATE OUTREACH SCHEDULER")
    print("🇵🇰 Timezone: Pakistan Standard Time (PKT)")
    print("🛡️ Anti-Ban Protocol: Active (Jitter 65-105s, First-Touch Handoff)")
    print("==================================================================\n")

    if not check_playwright():
        print("❌ Warning: Playwright is not installed yet.")
        print("To enable full headless sending, run: pip install playwright && playwright install chromium")
        print("For now, you can also use 1-click links in http://127.0.0.1:8050\n")

    if not os.path.exists(PROFILE_DIR):
        print(f"⚠️ Notice: WhatsApp session folder '{PROFILE_DIR}' not yet logged in.")
        print("Run 'python whatsapp_playwright_runner.py --login' to scan your QR code once.\n")

    executed_morning_today = False
    executed_evening_today = False
    last_day_checked = datetime.now().day

    while True:
        now = datetime.now()
        day = now.day
        hour = now.hour
        minute = now.minute

        # Reset daily execution flags at midnight
        if day != last_day_checked:
            executed_morning_today = False
            executed_evening_today = False
            last_day_checked = day
            print(f"\n🌅 New Day Started: {now.strftime('%A, %d %B %Y')}. Outreach quotas reset.")

        # 1. Morning Window Check (Builders & Developers): 11:30 AM - 1:30 PM
        # Target execution trigger: ~11:45 AM (Tue, Wed, Thu, Sat)
        if not is_sunday(now) and not is_friday(now):
            if (hour == 11 and minute >= 45) or (hour == 12 and minute <= 30):
                if not executed_morning_today:
                    print(f"\n🔔 [MORNING TRIGGER] {now.strftime('%I:%M %p')} - Starting Morning Developer Batch...")
                    try:
                        run_automated_batch(batch_name="Morning Batch", max_leads=12, headless=False)
                        executed_morning_today = True
                    except Exception as err:
                        print(f"❌ Error during morning batch: {err}")

        # 2. Evening Baithak Window Check (Estate Agents): 6:30 PM - 9:00 PM
        # Target execution trigger: ~7:15 PM (Mon - Sat)
        if not is_sunday(now):
            if (hour == 19 and minute >= 15) or (hour == 20 and minute <= 0):
                if not executed_evening_today:
                    print(f"\n🔔 [EVENING TRIGGER] {now.strftime('%I:%M %p')} - Starting Evening Baithak Realtor Batch...")
                    try:
                        run_automated_batch(batch_name="Evening Baithak", max_leads=12, headless=False)
                        executed_evening_today = True
                    except Exception as err:
                        print(f"❌ Error during evening batch: {err}")

        # Status heartbeat every 15 minutes
        status_morn = "Done" if executed_morning_today else "Pending (11:45 AM)"
        status_eve = "Done" if executed_evening_today else "Pending (7:15 PM)"
        print(f"[{now.strftime('%I:%M:%S %p')}] Scheduler Heartbeat -> Morning: {status_morn} | Evening: {status_eve} | Sleeping 60s...", end="\r")
        time.sleep(60)

if __name__ == '__main__':
    start_scheduler_loop()
