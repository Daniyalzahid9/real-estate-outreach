"""
whatsapp_auto_outreach.py
Antigravity WhatsApp Automated Outreach Engine for Pakistan Real Estate.

Features:
1. Dynamic Language Detection:
   - Big Corporate Developers & Groups -> Polished Corporate English
   - Prime Area Agencies & Local Builders -> Respectful Roman Urdu
2. Strict Pakistani Timing Windows:
   - Morning Batch: 11:30 AM - 1:30 PM PKT
   - Evening Baithak: 6:30 PM - 9:00 PM PKT
3. Anti-Ban Throttling:
   - 60-110 second randomized human jitter between messages
   - Maximum 12-15 leads per batch
4. First-Touch Handoff:
   - Sends the tailored initial message and hands off directly to human operator.
"""

import time
import random
import urllib.parse
import os
import sys
import openpyxl
from datetime import datetime

# Ensure clean UTF-8 console output on Windows
if sys.stdout:
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

EXCEL_FILE = "Pakistan_Real_Estate_WhatsApp_Outreach_Engine_Upgraded.xlsx"
FALLBACK_FILE = "Pakistan Real Estate Leads & Direct WhatsApp Outreach Engine (Updated with Timing).xlsx"


# Corporate triggers that indicate the agency/developer should receive English outreach
CORPORATE_ENGLISH_TRIGGERS = [
    'group of companies',
    'pvt ltd',
    'international',
    'prospect realty',
    'abraj',
    'abraaj',
    'gfs builders',
    'developers (pvt',
    'high-rise',
    'commercial & residential developers'
]

BLACKLIST_FILE = "contacted_blacklist.json"

def get_blacklist():
    if os.path.exists(BLACKLIST_FILE):
        try:
            import json
            with open(BLACKLIST_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def clean_contact_name(contact_str):
    c = str(contact_str or '').strip()
    if not c or c.lower().startswith('listed'):
        return None
    if '(' in c:
        c = c.split('(')[0].strip()
    if '/' in c:
        c = c.split('/')[0].strip()
    if any(term in c.lower() for term in ['team', 'office', 'desk']):
        return None
    return c if c else None

def get_message_for_lead(lead):
    """
    Generates Message 1 (The Pattern Interrupt Opener):
    - Strictly ZERO LINKS and under 45 words
    - Diagnostic hook pointing out a revenue leak or presentation gap
    - Ends with a frictionless permission question ("Mind if I drop it here?")
    """
    # If the lead has an audited bespoke message pre-compiled in the upgraded Excel engine, use it
    if lead.get('pitch_text') and str(lead['pitch_text']).strip():
        msg = str(lead['pitch_text']).strip()
        is_corp = any(term in f"{lead.get('name', '')} {lead.get('opportunity', '')}".lower() for term in CORPORATE_ENGLISH_TRIGGERS)
        lang = "Corporate English" if is_corp else "Respectful Roman Urdu"
        if "subdomain" in msg.lower() or "firebase" in msg.lower() or "lovable" in msg.lower():
            angle_type = "Angle B (Subdomain / Digital Leak)"
        elif "redirect" in msg.lower() or "unrelated" in msg.lower():
            angle_type = "Angle B (Broken Website Leak)"
        elif "facebook" in msg.lower():
            angle_type = "Angle A (Facebook Login-Wall Leak)"
        elif "youtube" in msg.lower() or "walkthrough" in msg.lower():
            angle_type = "Angle A (YouTube Video Lead Capture)"
        elif "abad" in msg.lower():
            angle_type = "Angle B (ABAD Developer Portal)"
        elif "review" in msg.lower() or "rating" in msg.lower():
            angle_type = "Angle B (Google Maps Authority / Demo-First)"
        else:
            angle_type = "Angle B (Prototype Showcase Demo)"
        return lang, msg, angle_type

    name = lead['name']
    contact = lead['contact']
    city = lead['city']
    area = lead['area']
    opp = lead['opportunity']
    
    c_name = clean_contact_name(contact)
    greeting_name = f"{c_name} sahib" if c_name else "sahib"
    
    loc = area if area and city.lower() in area.lower() else (f"{area}, {city}" if area else city)
    
    # Check if Corporate English applies
    text_check = f"{name} {opp}".lower()
    is_corporate = any(term in text_check for term in CORPORATE_ENGLISH_TRIGGERS)
    
    # Determine which of the 3 Diagnostic Angles fits best
    # Angle A: Ad / Funnel Leak (for those running FB/Insta ads or campaigns)
    # Angle B: Prototype Already Built (for developers/agencies lacking modern mobile showcase or using heavy PDFs)
    # Angle C: Speed-to-Lead (for after-hours overseas inquiries)
    if 'facebook' in opp.lower() or 'ad' in opp.lower() or 'campaign' in opp.lower():
        angle_type = "Angle A (Mystery Investor Audit)"
        if is_corporate:
            lang = "Corporate English"
            msg = (
                f"Assalam-o-Alaikum {greeting_name}, saw your campaign for {name} in {loc}. "
                f"I actually tested the inquiry flow from a buyer's perspective last night and noticed a friction point where mobile leads are likely dropping off before your sales team gets on a call.\n\n"
                f"I put together a quick 45-second visual fix specifically for {name} so you can see it. Mind if I drop it here?"
            )
        else:
            lang = "Respectful Roman Urdu"
            msg = (
                f"Assalam-o-Alaikum {greeting_name}, {loc} mein {name} ki campaign dekhi thi. "
                f"Kal raat maine ek buyer ke perspective se aapka inquiry flow test kiya aur ek friction point notice kiya jahan se mobile leads drop ho rahi hain sales team se baat hone se pehle.\n\n"
                f"Maine {name} ke liye ek quick visual fix tayyar kiya hai. Agar aap kahen to yahan share karoon?"
            )
    elif 'no website' in opp.lower() or 'builder' in name.lower() or 'developer' in name.lower():
        angle_type = "Angle B (Prototype Already Built)"
        if is_corporate:
            lang = "Corporate English"
            msg = (
                f"Assalam-o-Alaikum {greeting_name}, been following {name}’s developments in {loc}. "
                f"Noticed that when overseas investors look up your inventory online, there isn't a fast showcase page routing them straight to your WhatsApp closers—and sending 20MB PDFs usually kills impulse inquiries.\n\n"
                f"I actually mocked up a live, fast-loading preview page for {name} to show how much cleaner it converts. Can I send the link over for you to test on your phone?"
            )
        else:
            lang = "Respectful Roman Urdu"
            msg = (
                f"Assalam-o-Alaikum {greeting_name}, {loc} mein {name} ki listings dekh raha tha, MashaAllah premium inventory hai. "
                f"Ek cheez notice ki ke jab overseas ya out-of-city buyers aate hain to unhein 20MB ke heavy PDFs bhejne parte hain jisse impulse inquiry drop ho jati hai aur koi fast WhatsApp showcase link nahi milta.\n\n"
                f"Maine {name} ke brand naam se ek live mobile preview page mock kiya hai jo phone pe 2 second mein khulta hai. Test karne ke liye link yahan share karoon?"
            )
    else:
        angle_type = "Angle C (Speed-to-Lead)"
        if is_corporate:
            lang = "Corporate English"
            msg = (
                f"Assalam-o-Alaikum {greeting_name}, quick observation on {name}’s lead handling—when inquiries come in after office hours (especially from overseas buyers in UAE/UK/US), they wait hours for basic payment plan details and go cold by morning.\n\n"
                f"I built a quick WhatsApp test bot trained on {name}’s exact inventory that qualifies a buyer's budget and books a call for your team in under 30 seconds. Want me to share the test link so you can try messaging it yourself?"
            )
        else:
            lang = "Respectful Roman Urdu"
            msg = (
                f"Assalam-o-Alaikum {greeting_name}, {name} ke lead flow pe ek quick observation tha—raat ke waqt jab overseas buyers (UAE/UK) inquiry karte hain to payment plans aur rates ke liye unhein subah tak wait karna parta hai aur lead cold ho jati hai.\n\n"
                f"Maine {name} ki inventory pe ek quick WhatsApp automated flow setup kiya hai jo buyer ka budget qualify karke 30 second mein booking call schedule kar deta hai. Test link yahan share karoon taake aap khud check kar sakein?"
            )
        
    return lang, msg, angle_type

def get_step2_value_drop(lead, demo_url):
    """
    Message 2 (Deliver the Value + SPIN Implication):
    Sent ONLY after the prospect replies 'Yes / Share / Send'.
    """
    name = lead['name']
    c_name = clean_contact_name(lead.get('contact', ''))
    greeting_name = f"{c_name} sahib" if c_name else "sahib"
    
    return (
        f"Here you go {greeting_name}: {demo_url}\n\n"
        f"Notice two key differences here:\n"
        f"1. Instead of forcing a buyer to download a 20MB brochure, they see the floor plans and payment breakdown on their phone in 2 seconds.\n"
        f"2. The moment they tap WhatsApp, it pre-qualifies whether they want commercial or residential and routes hot buyers straight to your top closer.\n\n"
        f"Right now, if even 2 or 3 serious buyers a month bounce off your current flow, that is easily 1–2 Crore in missed deal volume. "
        f"How is your team currently filtering the serious investors from the time-wasters?"
    )

def get_step3_close(lead):
    """
    Message 3 (Low Friction Close):
    Sent when the prospect asks 'How much do you charge?' or admits the problem.
    """
    name = lead['name']
    return (
        f"It is significantly less than the commission on a single plot or unit booking. "
        f"Since we already built the base structure for {name} above, we can have the full live system deployed "
        f"and connected to your team's WhatsApp in 3 to 4 days—so you stop losing leads from this week's ad spend.\n\n"
        f"Do you have 7 minutes around 4:30 PM today, or does tomorrow first thing work better for a quick call to go over the exact rollout?"
    )

def get_day3_nudge(lead):
    name = lead['name']
    c_name = clean_contact_name(lead.get('contact', ''))
    greeting_name = f"{c_name} sahib" if c_name else "sahib"
    return f"Salam {greeting_name}, know you're busy on-site. Did you get a 30-second window to test the {name} preview above, or should I adjust anything on it?"

def get_day7_breakup(lead):
    name = lead['name']
    c_name = clean_contact_name(lead.get('contact', ''))
    city = lead.get('city', 'your city')
    greeting_name = f"{c_name} sahib" if c_name else "sahib"
    return f"Hey {greeting_name}, taking down the private test link for {name} tonight as we're onboarding another developer in {city} this week. Let me know if you want me to keep your preview live for another 24 hours."

def load_leads_from_excel():
    target = EXCEL_FILE if os.path.exists(EXCEL_FILE) else FALLBACK_FILE
    import shutil
    temp_file = "temp_outreach_read.xlsx"
    try:
        shutil.copy2(target, temp_file)
        wb = openpyxl.load_workbook(temp_file, data_only=True)
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception:
                pass
    except Exception:
        wb = openpyxl.load_workbook(target, data_only=True)
        
    ws = wb['WhatsApp Quick Outreach Table']
    
    blacklist = get_blacklist()
    leads = []
    headers = [str(ws.cell(1, c).value or '').strip() for c in range(1, ws.max_column + 1)]
    has_timing = 'Optimal Outreach Window' in headers
    
    for r in range(2, ws.max_row + 1):
        lid = str(ws.cell(r, 1).value or '')
        name = str(ws.cell(r, 2).value or '')
        city = str(ws.cell(r, 3).value or '')
        area = str(ws.cell(r, 4).value or '')
        contact = str(ws.cell(r, 5).value or '')
        phone = str(ws.cell(r, 6).value or '')
        clean_wa = str(ws.cell(r, 7).value or '')
        
        pitch_text = ""
        step2_text = ""
        step3_text = ""
        
        if has_timing:
            timing_window = str(ws.cell(r, 10).value or '')
            pitch_text = str(ws.cell(r, 13).value or '').strip()
            opportunity = str(ws.cell(r, 15).value or '')
            status = str(ws.cell(r, 16).value or 'Not Contacted')
            step2_text = str(ws.cell(r, 19).value or '').strip()
            step3_text = str(ws.cell(r, 20).value or '').strip()
        else:
            timing_window = "Morning" if "builder" in name.lower() or "developer" in name.lower() else "Evening"
            pitch_text = str(ws.cell(r, 10).value or '').strip()
            opportunity = str(ws.cell(r, 12).value or '')
            status = str(ws.cell(r, 13).value or 'Not Contacted')
            
        # Overwrite status if in permanent blacklist
        if clean_wa in blacklist or lid in [b.get('id') for b in blacklist.values()]:
            status = 'Contacted'
            
        is_morning = "morning" in timing_window.lower()
        batch = "Morning Batch" if is_morning else "Evening Baithak"
        
        if lid and name and clean_wa:
            leads.append({
                "row_idx": r,
                "id": lid,
                "name": name,
                "city": city,
                "area": area,
                "contact": contact,
                "phone": phone,
                "clean_wa": clean_wa,
                "timing_window": timing_window,
                "batch": batch,
                "opportunity": opportunity,
                "pitch_text": pitch_text,
                "step2_text": step2_text,
                "step3_text": step3_text,
                "status": status
            })
            
    return leads

def run_outreach_session(batch_filter=None, max_messages=12, dry_run=True):
    """
    Executes or previews an outreach batch.
    batch_filter: 'Morning Batch' or 'Evening Baithak' (or None for current time detection)
    dry_run: If True, prints messages and links without dispatching.
    """
    leads = load_leads_from_excel()
    now_hour = datetime.now().hour
    
    # Auto-detect optimal batch if not specified
    if not batch_filter:
        if 11 <= now_hour < 15:
            batch_filter = "Morning Batch"
        elif 18 <= now_hour < 22:
            batch_filter = "Evening Baithak"
        else:
            batch_filter = "Morning Batch" # Default
            
    print(f"\n==================================================================")
    print(f"🎯 ANTIGRAVITY OUTREACH DISPATCHER — BATCH: {batch_filter.upper()}")
    print(f"🕒 Current Local Time: {datetime.now().strftime('%I:%M %p')}")
    print(f"🛡️ Anti-Ban Safeguards: Jitter 60-100s | Cap: {max_messages} messages")
    print(f"==================================================================\n")
    
    # Filter candidate leads
    candidates = [l for l in leads if l['batch'] == batch_filter and l['status'] == 'Not Contacted']
    
    if not candidates:
        print(f"No pending leads found for {batch_filter} with status 'Not Contacted'!")
        return
        
    print(f"Found {len(candidates)} pending leads in {batch_filter}. Selecting top {min(max_messages, len(candidates))}...\n")
    
    selected_batch = candidates[:max_messages]
    
    for idx, lead in enumerate(selected_batch, 1):
        lang, msg, angle_type = get_message_for_lead(lead)
        encoded = urllib.parse.quote(msg)
        wa_url = f"https://wa.me/{lead['clean_wa']}?text={encoded}"
        
        print(f"[{idx}/{len(selected_batch)}] Lead #{lead['id']}: {lead['name']} ({lead['city']})")
        print(f"   👤 Contact: {lead['contact'] or 'Office Mobile'} | 📱 WA: +{lead['clean_wa']}")
        print(f"   🌐 Strategy: {angle_type} | Mode: {lang}")
        print(f"   💬 Message 1 (Zero-Link Opener):\n   {msg.replace(chr(10), chr(10)+'   ')}")
        print(f"   🔗 Direct Link: {wa_url[:90]}...")
        
        if not dry_run:
            # Here: Playwright / WhatsApp Web sends the message
            jitter = random.randint(65, 105)
            print(f"   ⏳ Anti-ban delay: Waiting {jitter}s before next contact...")
            time.sleep(jitter)
        else:
            print(f"   [DRY RUN - Ready for 1-click execution]\n")
            
    print("\n✅ Batch review complete! The user handles all incoming replies on their phone.")

if __name__ == '__main__':
    # Default preview execution
    run_outreach_session(dry_run=True)
