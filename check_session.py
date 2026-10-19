import os
from playwright.sync_api import sync_playwright

profile = os.path.abspath('whatsapp_user_profile')
with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(profile, headless=True)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto('https://web.whatsapp.com', wait_until='networkidle')
    page.screenshot(path='whatsapp_headless_test.png')
    print("Screenshot saved! URL:", page.url)
    print("Title:", page.title())
    ctx.close()
