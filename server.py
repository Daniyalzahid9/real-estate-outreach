import os
import re
import urllib.parse
import shutil
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import openpyxl

from whatsapp_auto_outreach import (
    get_message_for_lead, 
    get_step2_value_drop, 
    get_step3_close, 
    get_day3_nudge, 
    get_day7_breakup,
    get_blacklist
)

app = FastAPI(title="Antigravity WhatsApp Real Estate Co-Pilot")

EXCEL_FILE = "Pakistan_Real_Estate_WhatsApp_Outreach_Engine_Upgraded.xlsx"
FALLBACK_EXCEL = "Pakistan Real Estate Leads & Direct WhatsApp Outreach Engine (Updated with Timing).xlsx"

# In-memory storage for rapid searching and active state
LEADS_CACHE = []

def clean_phone(phone_str):
    digits = re.sub(r'\D', '', str(phone_str or ''))
    if digits.startswith('03') and len(digits) == 11:
        return '92' + digits[1:]
    elif digits.startswith('923') and len(digits) == 12:
        return digits
    elif digits.startswith('3') and len(digits) == 10:
        return '92' + digits
    return digits

def load_leads():
    global LEADS_CACHE
    target_file = EXCEL_FILE if os.path.exists(EXCEL_FILE) else FALLBACK_EXCEL
    
    # If locked by user in Excel, copy to temp file to read safely
    temp_file = "temp_server_read.xlsx"
    try:
        shutil.copy2(target_file, temp_file)
        wb = openpyxl.load_workbook(temp_file, data_only=True)
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception:
                pass
    except Exception:
        wb = openpyxl.load_workbook(target_file, data_only=True)
        
    ws = wb['WhatsApp Quick Outreach Table']
    leads = []
    
    # Detect header indexes
    headers = [str(ws.cell(1, c).value or '').strip() for c in range(1, ws.max_column + 1)]
    has_timing = 'Optimal Outreach Window' in headers
    
    for r in range(2, ws.max_row + 1):
        lid = str(ws.cell(r, 1).value or '')
        bname = str(ws.cell(r, 2).value or '')
        city = str(ws.cell(r, 3).value or '')
        area = str(ws.cell(r, 4).value or '')
        contact = str(ws.cell(r, 5).value or '')
        phone = str(ws.cell(r, 6).value or '')
        clean_wa = str(ws.cell(r, 7).value or clean_phone(phone))
        
        sheet_msg2 = ""
        sheet_msg3 = ""
        
        if has_timing:
            timing_window = str(ws.cell(r, 10).value or '')
            timing_note = str(ws.cell(r, 11).value or '')
            timing_days = str(ws.cell(r, 12).value or '')
            pitch_text = str(ws.cell(r, 13).value or '')
            pitch_url = str(ws.cell(r, 14).value or '')
            opportunity = str(ws.cell(r, 15).value or '')
            status = str(ws.cell(r, 16).value or 'Not Contacted')
            notes = str(ws.cell(r, 18).value or '')
            sheet_msg2 = str(ws.cell(r, 19).value or '')
            sheet_msg3 = str(ws.cell(r, 20).value or '')
        else:
            timing_window = "🌅 Morning Batch (11:30 AM – 1:30 PM)" if "builder" in bname.lower() or "developer" in bname.lower() else "🌆 Evening Baithak (6:30 PM – 9:00 PM)"
            timing_note = "Timing schedule"
            timing_days = "Tue – Thu | Sat"
            pitch_text = str(ws.cell(r, 10).value or '')
            pitch_url = str(ws.cell(r, 11).value or '')
            opportunity = str(ws.cell(r, 12).value or '')
            status = str(ws.cell(r, 13).value or 'Not Contacted')
            notes = str(ws.cell(r, 15).value or '')
            
        batch_code = "Morning Batch" if "morning" in timing_window.lower() else "Evening Baithak"
        
        # Check permanent blacklist
        blacklist = get_blacklist()
        if clean_wa in blacklist or lid in [b.get('id') for b in blacklist.values()]:
            status = 'Contacted'
        
        if lid and bname:
            lead_temp = {
                "id": lid,
                "name": bname,
                "city": city,
                "area": area,
                "contact": contact,
                "clean_wa": clean_wa,
                "opportunity": opportunity,
                "pitch_text": pitch_text
            }
            lang, msg1, angle_type = get_message_for_lead(lead_temp)
            
            demo_url = f"/demo?id={lid}"
            full_demo_url = f"https://real-estate-outreach.pages.dev{demo_url}"
            
            if sheet_msg2 and "[INSERT_YOUR_DEMO_LINK_HERE]" in sheet_msg2:
                msg2 = sheet_msg2.replace("[INSERT_YOUR_DEMO_LINK_HERE]", full_demo_url)
            else:
                msg2 = get_step2_value_drop(lead_temp, full_demo_url)
                
            msg3 = get_step3_close(lead_temp)
            msg_day3 = sheet_msg3 if sheet_msg3 else get_day3_nudge(lead_temp)
            msg_day7 = get_day7_breakup(lead_temp)
            
            pitch_text = msg1
            pitch_url = f"https://wa.me/{clean_wa}?text={urllib.parse.quote(msg1)}"
            
            leads.append({
                "id": lid,
                "name": bname,
                "city": city,
                "area": area,
                "contact": contact,
                "phone": phone,
                "clean_wa": clean_wa,
                "timing_window": timing_window,
                "timing_note": timing_note,
                "timing_days": timing_days,
                "batch_code": batch_code,
                "strategy_angle": angle_type,
                "language_mode": lang,
                "pitch_text": pitch_text,
                "pitch_url": pitch_url,
                "demo_url": demo_url,
                "step2_text": msg2,
                "step3_text": msg3,
                "day3_nudge": msg_day3,
                "day7_breakup": msg_day7,
                "quick_text": pitch_text,
                "quick_url": pitch_url,
                "opportunity": opportunity,
                "status": status,
                "notes": notes
            })
            
    LEADS_CACHE = leads
    print(f"Successfully loaded {len(LEADS_CACHE)} leads with timing schedule into memory.")

load_leads()

# -------------------------------------------------------------
# Data Models
# -------------------------------------------------------------
class StatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None

class ReplyRequest(BaseModel):
    lead_id: str
    incoming_message: str
    api_key: Optional[str] = None

# -------------------------------------------------------------
# AI Response Generator (Offline Expert System + Optional LLM)
# -------------------------------------------------------------
def generate_expert_reply(lead: dict, incoming_msg: str) -> dict:
    msg_lower = incoming_msg.lower().strip()
    contact = lead.get('contact', '')
    c_clean = contact if (contact and not contact.lower().startswith('listed')) else ''
    name = lead.get('name', 'bhai')
    city = lead.get('city', 'Pakistan')
    area = lead.get('area', '')
    opp = lead.get('opportunity', '')
    clean_wa = lead.get('clean_wa', '')
    
    greeting = f"Assalam-o-Alaikum {c_clean} sahib!" if c_clean else "Assalam-o-Alaikum bhai!"
    demo_url = lead.get('demo_url') or f"/demo?id={lead.get('id', '1')}"
    if demo_url.startswith('/'):
        demo_url = f"https://real-estate-outreach.pages.dev{demo_url}"
    
    # 1. Affirmative / Permission Granted ("Sure", "Send", "Ji bhejain", "Show me", "Kaun bol rahe hain")
    # -> Message 2: Value-First Delivery + SPIN Selling Financial Implication
    if any(k in msg_lower for k in ['sure', 'send', 'bhej', 'dikhao', 'show', 'yes', 'ji', 'theek', 'share', 'kaun', 'who']):
        text_reply = (
            f"Here you go {c_clean or 'sahib'}: {demo_url}\n\n"
            f"Notice two key differences here:\n"
            f"1. Instead of forcing a buyer to download a 20MB PDF brochure, they see the floor plans and installment calculator on their phone in 2 seconds.\n"
            f"2. The moment they tap WhatsApp, it pre-qualifies whether they want commercial or residential and routes hot buyers straight to your top closer.\n\n"
            f"Right now, if even 2 or 3 serious buyers a month bounce off your current flow, that is easily 1–2 Crore in missed deal volume. "
            f"How is your team currently filtering the serious investors from the time-wasters?"
        )
        voice_script = (
            f"Assalam-o-Alaikum {c_clean or 'sahib'}, link maine bhej diya hai, aap apne mobile par tap karke check karein. "
            f"Speed aur floor plan ka layout dekhein—koi heavy brochure download karne ki zaroorat nahi parti. "
            f"Sab se bari baat ye ke WhatsApp button dabate hi buyer qualify ho kar direct aapke top sales closer ke paas aata hai. "
            f"Aap log abhi time-waster inquiries ko kaise filter kar rahe hain?"
        )
        strategy = (
            "Alex Hormozi Value-First Delivery + Neil Rackham SPIN Selling Implication. "
            "You deliver the promised Trojan Horse fix with zero friction, then ask a diagnostic question that makes them "
            "calculate the 1-2 Crore loss of missing overseas buyers."
        )

    # 2. Price / Rate Inquiry ("How much do you charge?")
    # -> Message 3: Low-Friction Close Anchored to Single Deal ROI
    elif any(k in msg_lower for k in ['rate', 'price', 'kitne', 'cost', 'charge', 'packages', 'pese', 'fee']):
        text_reply = (
            f"{greeting} It is significantly less than the commission on a single plot or unit booking. "
            f"Since we already built the base structure for {name} above, we can have the full live system deployed "
            f"and connected to your team's WhatsApp in 3 to 4 days—so you stop losing leads from this week's ad spend.\n\n"
            f"Do you have 7 minutes around 4:30 PM today, or does tomorrow first thing work better for a quick call to go over the exact rollout?"
        )
        voice_script = (
            f"Sahib charges ki baat karein to bhai ek single plot ya unit ke commission se bhi kafi kam hai. "
            f"Kyunke humne {name} ka basic portal setup pehle hi design kar liya hai, to hum 3 se 4 din ke andar "
            f"pura system aapke WhatsApp ke sath live connect kar denge taake is hafte ki marketing leads zaya na hon. "
            f"Aaj shaam 4:30 baje 7 minute nikal sakte hain, ya kal subah ka time behtar rahega?"
        )
        strategy = (
            "Anchoring to ROI: Never state cost as an expense; frame it against the commission of a single plot sale. "
            "The 7-minute call ask gives a binary choice (today 4:30 PM vs tomorrow morning) that maximizes bookings."
        )

    # 3. Zameen.com Objection ("Hamara Zameen se kaam chal raha hai")
    # -> The Challenger Sale (Re-frame the blind spot)
    elif any(k in msg_lower for k in ['zameen', 'facebook', 'fb', 'already', 'zarorat nahi']):
        text_reply = (
            f"{greeting} Bilkul sahib, Zameen aur Facebook to marketing ke liye behtareen hain. Lekin problem ye hai ke Zameen par "
            f"jab koi buyer aapki listing dekhta hai, to usi screen par aapke competitors ke saste plot bhi show ho jaate hain—yani paisa aap dete hain aur lead koi aur le jata hai! "
            f"Aapki apni website par 100% traffic sirf aapki hoti hai, na koi middleman na competitor ke ads. Kya mai ek 1-minute ka demo preview dikhaoon?"
        )
        voice_script = (
            f"Bhai aapki baat 100% theek hai ke Zameen aur FB se leads aati hain. Lekin Zameen par masla ye hai ke wo monthly lakho rupay lene ke bawajood "
            f"aapke listing ke barabar mein doosre dealers ke ads chalata hai. Jabki aapka apna portal banega to har Facebook ad se aane wala buyer "
            f"direct aapki inventory dekhega aur direct aapke WhatsApp par aayega. Ek dafa 30 second ka preview dekh lein, pasand aaye to baat karein."
        )
        strategy = (
            "The Challenger Sale: Teach them the leak in their existing model. They pay Zameen monthly, "
            "yet Zameen displays competitors' lower-priced plots on the same screen."
        )

    # 4. Maintenance / Upkeep Objection ("Listings update kaun karega?")
    elif any(k in msg_lower for k in ['update', 'maintain', 'kaun karega', 'time nahi', 'manage']):
        text_reply = (
            f"{greeting} Bilkul fikr na karein sahib! Aapko ya aapke staff ko koi technical kaam ya coding nahi karni paregi. "
            f"Hum aisi WhatsApp automation dete hain jahan aap sirf photo aur details WhatsApp group mein send karein, humari team 5 minute mein website par update kar deti hai. "
            f"Sab kuch 100% turnkey hum handle karte hain."
        )
        voice_script = (
            f"Bhai website maintenance ka 1% bhi jhanjhat aapke sar nahi hoga. Aapke paas jo bhi naya plot ya villa aaye, aap bas uski details aur tasweerein "
            f"WhatsApp par forward kar dein, humari technical team usko foran live kar deti hai. Aapka time sirf deals close karne mein lagega."
        )
        strategy = (
            "Removing friction: Traditional Pakistani dealers fear learning WordPress or hiring IT staff. "
            "Turnkey maintenance via WhatsApp eliminates this barrier completely."
        )

    # 5. Slow Market / Postponement ("Market thandi hai / agle mahine dekhte hain")
    elif any(k in msg_lower for k in ['slow', 'thandi', 'baad mein', 'next month', 'abhi nahi', 'masroof']):
        text_reply = (
            f"{greeting} Theek hai sahib, I completely understand. Lekin slow market mein hi un agencies ko fayda hota hai jo direct "
            f"overseas Pakistanis (UK, UAE, US) ko target karti hain jo foreign currency mein cash buy karte hain. "
            f"Aap jab bhi free hon, mai 2 minute ka concept link chhor deta hoon, jab fursat mile dekh lijiye ga!"
        )
        voice_script = (
            f"Bhai bilkul theek hai, market mein thora thehrao to zaroor hai. Lekin yahi time hota hai ke agle season ke liye apna brand digitalize kar lein "
            f"taake overseas clients aapke paas direct connect hon. Jab bhi aap office mein fursat mein hon batayiye ga, ek chai par baith lenge."
        )
        strategy = (
            "Polite detachment + planting the seed of overseas cash buyers."
        )

    # 6. General positive or curious reply
    else:
        text_reply = (
            f"{greeting} Ji bilkul sahib! Humne {name} ke liye ek interactive mobile preview tayyar kiya hai "
            f"jisme direct floor plans, installment calculator, aur 1-click WhatsApp lead routing shaamil hai.\n\n"
            f"Ye private link apne phone par check karein: {demo_url}\n\n"
            f"Aap bataiye ga, kya kal afternoon mein 7 minute ki short call munasib rahegi isko live connect karne ke liye?"
        )
        voice_script = (
            f"Assalam-o-Alaikum {c_clean or 'sahib'}, shukriya aapke reply ka. Humne khas tor par {city} ke real estate context mein "
            f"ek modern property portal ka concept banaya hai taake overseas buyers direct attract hon. "
            f"Aap link check karein aur batayein kal 7 minute nikal sakte hain live walkthrough ke liye?"
        )
        strategy = (
            "Value delivery followed by a low-friction 7-minute call commitment."
        )

    encoded_reply = urllib.parse.quote(text_reply)
    clean_wa = lead.get('clean_wa', '')
    wa_direct_url = f"https://wa.me/{clean_wa}?text={encoded_reply}"

    return {
        "text_reply": text_reply,
        "voice_script": voice_script,
        "strategy": strategy,
        "wa_direct_url": wa_direct_url,
        "clean_wa": clean_wa
    }

# -------------------------------------------------------------
# REST API Endpoints
# -------------------------------------------------------------
@app.get("/api/leads")
def get_leads(
    city: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    timing: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    results = LEADS_CACHE
    if city and city.lower() != 'all':
        results = [l for l in results if l['city'].lower() == city.lower()]
    if status and status.lower() != 'all':
        results = [l for l in results if l['status'].lower() == status.lower()]
    if timing and timing.lower() != 'all':
        if 'morning' in timing.lower():
            results = [l for l in results if 'morning' in l.get('batch_code', '').lower()]
        elif 'evening' in timing.lower() or 'baithak' in timing.lower():
            results = [l for l in results if 'evening' in l.get('batch_code', '').lower()]
    if search:
        s = search.lower()
        results = [l for l in results if s in l['name'].lower() or s in l['area'].lower() or s in l['city'].lower() or s in l['contact'].lower()]
    return results

@app.get("/api/stats")
def get_stats():
    total = len(LEADS_CACHE)
    contacted = sum(1 for l in LEADS_CACHE if l['status'] != 'Not Contacted')
    demos = sum(1 for l in LEADS_CACHE if 'demo' in l['status'].lower() or 'proposal' in l['status'].lower())
    closed = sum(1 for l in LEADS_CACHE if 'closed' in l['status'].lower() or 'won' in l['status'].lower())
    morning_leads = sum(1 for l in LEADS_CACHE if 'morning' in l.get('batch_code', '').lower())
    evening_leads = sum(1 for l in LEADS_CACHE if 'evening' in l.get('batch_code', '').lower())
    
    cities = {}
    for l in LEADS_CACHE:
        c = l['city']
        cities[c] = cities.get(c, 0) + 1
        
    return {
        "total_leads": total,
        "contacted": contacted,
        "demos_sent": demos,
        "closed": closed,
        "morning_leads": morning_leads,
        "evening_leads": evening_leads,
        "city_breakdown": cities
    }

@app.post("/api/leads/{lead_id}/status")
def update_status(lead_id: str, payload: StatusUpdate):
    for l in LEADS_CACHE:
        if l['id'] == lead_id:
            l['status'] = payload.status
            if payload.notes is not None:
                l['notes'] = payload.notes
            return {"status": "success", "lead": l}
    raise HTTPException(status_code=404, detail="Lead not found")

@app.post("/api/generate-reply")
def generate_reply(req: ReplyRequest):
    lead = next((l for l in LEADS_CACHE if l['id'] == req.lead_id), None)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    reply_bundle = generate_expert_reply(lead, req.incoming_message)
    return reply_bundle

# -------------------------------------------------------------
# Static Files & SPA Route
# -------------------------------------------------------------
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_index():
    return FileResponse("static/index.html")

@app.get("/style.css")
def serve_style():
    return FileResponse("static/style.css")

@app.get("/app.js")
def serve_js():
    return FileResponse("static/app.js")

@app.get("/leads.json")
def serve_leads_json():
    return FileResponse("static/leads.json")

@app.get("/stats.json")
def serve_stats_json():
    return FileResponse("static/stats.json")

@app.get("/demo")
@app.get("/demo/")
def serve_demo():
    return FileResponse("static/demo/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8050, reload=True)
