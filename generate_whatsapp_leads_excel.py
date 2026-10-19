import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo
import urllib.parse
import re
import os
import shutil

def clean_phone(phone_str):
    """Clean phone number into international Pakistan format (923XXXXXXXXX)."""
    digits = re.sub(r'\D', '', str(phone_str or ''))
    if digits.startswith('03') and len(digits) == 11:
        return '92' + digits[1:]
    elif digits.startswith('923') and len(digits) == 12:
        return digits
    elif digits.startswith('3') and len(digits) == 10:
        return '92' + digits
    return digits

def clean_contact_name(contact_str):
    """Extract a polite contact name if available."""
    c = str(contact_str or '').strip()
    if not c:
        return None
    # Strip parentheticals like (CEO)
    c = re.sub(r'\(.*?\)', '', c).strip()
    if '/' in c:
        c = c.split('/')[0].strip()
    lower_c = c.lower()
    if any(term in lower_c for term in ['listed', 'team', 'office', 'desk', 'mgmt', 'management']):
        return None
    return c if c else None

def get_outreach_timing(business_name, category, opportunity):
    """Classify the lead into Pakistan real estate specific timing windows and strategic batches."""
    text = f"{business_name} {category} {opportunity}".lower()
    
    # Check if corporate builder / developer / large construction company
    is_developer = any(w in text for w in ['developer', 'construction', 'builders & developers', 'enterprise', 'group of companies', 'constructors'])
    
    if is_developer:
        window = "🌅 Morning Batch (11:30 AM – 1:30 PM)"
        note = "Corporate builder/developer. Management in head office before Zuhr. Secondary: 4:30–6:30 PM. Avoid 2–4 PM."
        days = "Tue – Thu (Peak) | Sat"
        batch_code = "Morning Batch"
    else:
        window = "🌆 Evening Baithak (6:30 PM – 9:00 PM)"
        note = "Real estate agency/broker. Peak office chai & networking hours. Avoid 3:30–6:00 PM daylight visits."
        days = "Tue – Thu (Peak) | Sat (Good)"
        batch_code = "Evening Baithak"
        
    return window, note, days, batch_code

def generate_pitch_message(business_name, contact, city, area, web_status):
    """Generate a highly personalized Pakistani business pitch in professional English/Urdu tone."""
    name_clean = str(business_name or '').strip()
    contact_name = clean_contact_name(contact)
    
    if contact_name:
        greeting = f"Assalam-o-Alaikum {contact_name} sahib"
    else:
        greeting = "Assalam-o-Alaikum"
        
    area_str = str(area or '').strip()
    city_str = str(city or '').strip()
    
    if area_str and city_str.lower() in area_str.lower():
        loc = area_str
    elif area_str:
        loc = f"{area_str}, {city_str}"
    else:
        loc = city_str
        
    status_lower = str(web_status or '').lower()
    if 'facebook' in status_lower:
        angle = "is currently relying on a Facebook page without an official listings website"
    elif 'firebase' in status_lower or 'subdomain' in status_lower:
        angle = "is using a temporary subdomain rather than a branded corporate portal"
    elif 'no website' in status_lower:
        angle = "has great market reputation but no official modern website for listings"
    else:
        angle = "could attract significantly more overseas buyer leads with a modern digital portal"
        
    msg = (
        f"{greeting}! I noticed {name_clean} in {loc} {angle}. "
        f"We build premium, high-converting real estate websites with direct WhatsApp lead capture for top agencies & builders. "
        f"Would you be open to a quick 2-minute live demo customized for your projects?"
    )
    return msg

def generate_quick_message(business_name, contact):
    """Generate a shorter direct inquiry message."""
    contact_name = clean_contact_name(contact)
    greeting = f"Assalam-o-Alaikum {contact_name} sahib" if contact_name else "Assalam-o-Alaikum"
    return f"{greeting}! Reaching out regarding a modern property website & listings portal for {business_name}. Are you available for a brief chat?"

def build_workbook():
    src_filename = 'Pakistan Real Estate Agents & Builders Leads (Mobile Contacts & Website Prospects).xlsx'
    primary_out = 'Pakistan Real Estate Leads & Direct WhatsApp Outreach Engine.xlsx'
    alt_out = 'Pakistan Real Estate Leads & Direct WhatsApp Outreach Engine (Updated with Timing).xlsx'
    
    src_wb = openpyxl.load_workbook(src_filename, data_only=True)
    src_ws = src_wb['Leads']
    
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    
    # Fonts
    font_family = 'Segoe UI'
    title_font = Font(name=font_family, size=15, bold=True, color='FFFFFFFF')
    sub_font = Font(name=font_family, size=9, italic=True, color='FFE2E8F0')
    header_navy_font = Font(name=font_family, size=10, bold=True, color='FFFFFFFF')
    header_green_font = Font(name=font_family, size=10, bold=True, color='FFFFFFFF')
    header_purple_font = Font(name=font_family, size=10, bold=True, color='FFFFFFFF')
    header_amber_font = Font(name=font_family, size=10, bold=True, color='FFFFFFFF')
    
    regular_font = Font(name=font_family, size=9.5, color='FF1E293B')
    bold_font = Font(name=font_family, size=9.5, bold=True, color='FF1E293B')
    phone_font = Font(name=font_family, size=9.5, bold=True, color='FF0F172A')
    
    wa_pitch_link_font = Font(name=font_family, size=9.5, bold=True, color='FF047857', underline='single')
    wa_quick_link_font = Font(name=font_family, size=9.5, bold=True, color='FF0284C7', underline='single')
    map_link_font = Font(name=font_family, size=9.0, color='FF2563EB', underline='single')
    url_font = Font(name='Consolas', size=8.5, color='FF475569')
    
    timing_morning_font = Font(name=font_family, size=9.5, bold=True, color='FFB45309')
    timing_evening_font = Font(name=font_family, size=9.5, bold=True, color='FF6B21A8')
    
    # Fills
    fill_banner = PatternFill(start_color='FF0F172A', end_color='FF0F172A', fill_type='solid')
    fill_header_navy = PatternFill(start_color='FF1E3A8A', end_color='FF1E3A8A', fill_type='solid') # Deep Navy
    fill_header_green = PatternFill(start_color='FF065F46', end_color='FF065F46', fill_type='solid') # Emerald Green
    fill_header_purple = PatternFill(start_color='FF4C1D95', end_color='FF4C1D95', fill_type='solid') # Deep Indigo
    fill_header_amber = PatternFill(start_color='FFB45309', end_color='FFB45309', fill_type='solid') # Amber Gold
    
    fill_zebra = PatternFill(start_color='FFF8FAFC', end_color='FFF8FAFC', fill_type='solid')
    fill_white = PatternFill(start_color='FFFFFFFF', end_color='FFFFFFFF', fill_type='solid')
    fill_wa_btn = PatternFill(start_color='FFECFDF5', end_color='FFECFDF5', fill_type='solid')
    fill_quick_btn = PatternFill(start_color='FFF0F9FF', end_color='FFF0F9FF', fill_type='solid')
    fill_status_default = PatternFill(start_color='FFFEF3C7', end_color='FFFEF3C7', fill_type='solid')
    
    fill_timing_morning = PatternFill(start_color='FFFEF3C7', end_color='FFFEF3C7', fill_type='solid') # Amber
    fill_timing_evening = PatternFill(start_color='FFF3E8FF', end_color='FFF3E8FF', fill_type='solid') # Lavender
    
    # Borders
    border_subtle = Border(
        left=Side(style='thin', color='FFE2E8F0'),
        right=Side(style='thin', color='FFE2E8F0'),
        top=Side(style='thin', color='FFE2E8F0'),
        bottom=Side(style='thin', color='FFE2E8F0')
    )
    border_btn = Border(
        left=Side(style='thin', color='FFA7F3D0'),
        right=Side(style='thin', color='FFA7F3D0'),
        top=Side(style='thin', color='FFA7F3D0'),
        bottom=Side(style='thin', color='FFA7F3D0')
    )
    
    # Alignments
    align_center = Alignment(horizontal='center', vertical='center')
    align_left = Alignment(horizontal='left', vertical='center')
    align_wrap = Alignment(horizontal='left', vertical='top', wrap_text=True)
    align_header = Alignment(horizontal='center', vertical='center', wrap_text=True)
    
    # Extract source records
    leads_data = []
    for r in range(2, src_ws.max_row + 1):
        row_vals = [src_ws.cell(r, c).value for c in range(1, 13)]
        if any(row_vals):
            lid, bname, cat, city, area, phone, contact, web_status, pitch_opp, rating, address, src_url = row_vals
            clean_wa = clean_phone(phone)
            timing_window, timing_note, timing_days, batch_code = get_outreach_timing(bname, cat, pitch_opp)
            pitch_text = generate_pitch_message(bname, contact, city, area, web_status)
            quick_text = generate_quick_message(bname, contact)
            pitch_url = f"https://wa.me/{clean_wa}?text={urllib.parse.quote(pitch_text)}"
            quick_url = f"https://wa.me/{clean_wa}?text={urllib.parse.quote(quick_text)}"
            
            leads_data.append({
                'id': lid,
                'name': bname,
                'category': cat,
                'city': city,
                'area': area,
                'phone': phone,
                'contact': contact,
                'web_status': web_status,
                'pitch_opp': pitch_opp,
                'rating': rating,
                'address': address,
                'src_url': src_url,
                'clean_wa': clean_wa,
                'timing_window': timing_window,
                'timing_note': timing_note,
                'timing_days': timing_days,
                'batch_code': batch_code,
                'pitch_text': pitch_text,
                'quick_text': quick_text,
                'pitch_url': pitch_url,
                'quick_url': quick_url,
            })
            
    # -------------------------------------------------------------
    # SHEET 1: Master Leads & WhatsApp (Full Data + Timing)
    # -------------------------------------------------------------
    ws1 = wb.create_sheet(title='Master Leads & WhatsApp')
    ws1.views.sheetView[0].showGridLines = True
    
    headers_s1 = [
        'Lead ID',
        'Business Name',
        'Category',
        'City',
        'Area / Sector',
        'Contact / Director',
        'Mobile Phone',
        'WhatsApp Number',
        '💬 WhatsApp Direct Link',
        '⚡ Quick Chat Link',
        'Optimal Outreach Window',
        'Timing Strategy Rationale',
        'Recommended Days',
        'WhatsApp Pitch URL (Raw)',
        'Personalized Pitch Message',
        'Outreach Status',
        'Current Web Presence Status',
        'Website Pitch Opportunity',
        'Activity & Rating Proof',
        'Office Address',
        'Verified Google Maps URL',
        'Outreach Notes'
    ]
    
    for col_idx, h_text in enumerate(headers_s1, start=1):
        c = ws1.cell(1, col_idx, h_text)
        c.alignment = align_header
        
        if 'WhatsApp' in h_text or 'Quick' in h_text or 'Pitch' in h_text:
            c.fill = fill_header_green; c.font = header_green_font
        elif 'Timing' in h_text or 'Window' in h_text or 'Days' in h_text:
            c.fill = fill_header_amber; c.font = header_amber_font
        elif 'Status' in h_text or 'Notes' in h_text:
            c.fill = fill_header_purple; c.font = header_purple_font
        else:
            c.fill = fill_header_navy; c.font = header_navy_font
            
    ws1.row_dimensions[1].height = 32
    
    for row_idx, d in enumerate(leads_data, start=2):
        ws1.row_dimensions[row_idx].height = 28
        is_even = (row_idx % 2 == 0)
        row_fill = fill_white if is_even else fill_zebra
        
        is_morning = "Morning" in d['batch_code']
        timing_fill = fill_timing_morning if is_morning else fill_timing_evening
        timing_font = timing_morning_font if is_morning else timing_evening_font
        
        row_cells = [
            (1, d['id'], align_center, bold_font, row_fill, border_subtle),
            (2, d['name'], align_left, bold_font, row_fill, border_subtle),
            (3, d['category'], align_left, regular_font, row_fill, border_subtle),
            (4, d['city'], align_center, regular_font, row_fill, border_subtle),
            (5, d['area'], align_left, regular_font, row_fill, border_subtle),
            (6, d['contact'], align_left, regular_font, row_fill, border_subtle),
            (7, d['phone'], align_center, phone_font, row_fill, border_subtle),
            (8, d['clean_wa'], align_center, phone_font, row_fill, border_subtle),
            (9, '💬 Send WhatsApp Pitch', align_center, wa_pitch_link_font, fill_wa_btn, border_btn),
            (10, '⚡ Start Quick Chat', align_center, wa_quick_link_font, fill_quick_btn, border_btn),
            (11, d['timing_window'], align_center, timing_font, timing_fill, border_subtle),
            (12, d['timing_note'], align_wrap, regular_font, row_fill, border_subtle),
            (13, d['timing_days'], align_center, regular_font, row_fill, border_subtle),
            (14, d['pitch_url'], align_left, url_font, row_fill, border_subtle),
            (15, d['pitch_text'], align_wrap, regular_font, row_fill, border_subtle),
            (16, 'Not Contacted', align_center, regular_font, fill_status_default, border_subtle),
            (17, d['web_status'], align_left, regular_font, row_fill, border_subtle),
            (18, d['pitch_opp'], align_wrap, regular_font, row_fill, border_subtle),
            (19, d['rating'], align_left, regular_font, row_fill, border_subtle),
            (20, d['address'], align_wrap, regular_font, row_fill, border_subtle),
            (21, '📍 View on Maps', align_center, map_link_font, row_fill, border_subtle),
            (22, '', align_left, regular_font, row_fill, border_subtle)
        ]
        
        for col_num, val, align, font, fill, border in row_cells:
            cell = ws1.cell(row_idx, col_num, val)
            cell.alignment = align
            cell.font = font
            cell.fill = fill
            cell.border = border
            if col_num == 9:
                cell.hyperlink = d['pitch_url']
            elif col_num == 10:
                cell.hyperlink = d['quick_url']
            elif col_num == 21 and d['src_url']:
                cell.hyperlink = d['src_url']
                
    ws1.freeze_panes = 'C2'
    
    # -------------------------------------------------------------
    # SHEET 2: Dedicated WhatsApp Outreach CRM Table (With Timing)
    # -------------------------------------------------------------
    ws2 = wb.create_sheet(title='WhatsApp Quick Outreach Table')
    ws2.views.sheetView[0].showGridLines = True
    
    headers_s2 = [
        'Lead ID',
        'Business Name',
        'City',
        'Area / Sector',
        'Contact Person',
        'Mobile Number',
        'WhatsApp Number',
        '🚀 1-Click WhatsApp Pitch',
        '⚡ Quick Chat Link',
        'Optimal Outreach Window',
        'Timing Strategy Rationale',
        'Recommended Days',
        'Personalized Pitch Text (Auto-Filled on Click)',
        'Direct WhatsApp Link (URL)',
        'Website Pitch Opportunity',
        'Outreach Status',
        'Follow-Up Date',
        'Outreach Notes & Next Step'
    ]
    
    for col_idx, h_text in enumerate(headers_s2, start=1):
        c = ws2.cell(1, col_idx, h_text)
        c.alignment = align_header
        if 'WhatsApp' in h_text or 'Click' in h_text or 'Chat' in h_text or 'Pitch' in h_text:
            c.fill = fill_header_green; c.font = header_green_font
        elif 'Timing' in h_text or 'Window' in h_text or 'Days' in h_text:
            c.fill = fill_header_amber; c.font = header_amber_font
        elif 'Status' in h_text or 'Date' in h_text or 'Notes' in h_text:
            c.fill = fill_header_purple; c.font = header_purple_font
        else:
            c.fill = fill_header_navy; c.font = header_navy_font
            
    ws2.row_dimensions[1].height = 32
    
    for row_idx, d in enumerate(leads_data, start=2):
        ws2.row_dimensions[row_idx].height = 28
        is_even = (row_idx % 2 == 0)
        row_fill = fill_white if is_even else fill_zebra
        
        is_morning = "Morning" in d['batch_code']
        timing_fill = fill_timing_morning if is_morning else fill_timing_evening
        timing_font = timing_morning_font if is_morning else timing_evening_font
        
        row_cells2 = [
            (1, d['id'], align_center, bold_font, row_fill, border_subtle),
            (2, d['name'], align_left, bold_font, row_fill, border_subtle),
            (3, d['city'], align_center, regular_font, row_fill, border_subtle),
            (4, d['area'], align_left, regular_font, row_fill, border_subtle),
            (5, d['contact'], align_left, regular_font, row_fill, border_subtle),
            (6, d['phone'], align_center, phone_font, row_fill, border_subtle),
            (7, d['clean_wa'], align_center, phone_font, row_fill, border_subtle),
            (8, '💬 Send WhatsApp Pitch', align_center, wa_pitch_link_font, fill_wa_btn, border_btn),
            (9, '⚡ Quick Chat', align_center, wa_quick_link_font, fill_quick_btn, border_btn),
            (10, d['timing_window'], align_center, timing_font, timing_fill, border_subtle),
            (11, d['timing_note'], align_wrap, regular_font, row_fill, border_subtle),
            (12, d['timing_days'], align_center, regular_font, row_fill, border_subtle),
            (13, d['pitch_text'], align_wrap, regular_font, row_fill, border_subtle),
            (14, d['pitch_url'], align_left, url_font, row_fill, border_subtle),
            (15, d['pitch_opp'], align_wrap, regular_font, row_fill, border_subtle),
            (16, 'Not Contacted', align_center, regular_font, fill_status_default, border_subtle),
            (17, '', align_center, regular_font, row_fill, border_subtle),
            (18, '', align_left, regular_font, row_fill, border_subtle)
        ]
        
        for col_num, val, align, font, fill, border in row_cells2:
            cell = ws2.cell(row_idx, col_num, val)
            cell.alignment = align
            cell.font = font
            cell.fill = fill
            cell.border = border
            if col_num == 8:
                cell.hyperlink = d['pitch_url']
            elif col_num == 9:
                cell.hyperlink = d['quick_url']
                
    ws2.freeze_panes = 'C2'
    
    # -------------------------------------------------------------
    # SHEET 3: Executive Summary & Outreach Dashboard (With Timing Stats)
    # -------------------------------------------------------------
    ws3 = wb.create_sheet(title='Outreach KPIs & City Stats')
    ws3.views.sheetView[0].showGridLines = True
    
    # Header Banner
    ws3.merge_cells('A1:G1')
    b_cell = ws3.cell(1, 1, '🇵🇰 Pakistan Real Estate Lead Outreach & Direct WhatsApp Engine')
    b_cell.font = Font(name=font_family, size=15, bold=True, color='FFFFFFFF')
    b_cell.fill = fill_banner
    b_cell.alignment = Alignment(horizontal='center', vertical='center')
    ws3.row_dimensions[1].height = 42
    
    # Subtitle
    ws3.merge_cells('A2:G2')
    sub_cell = ws3.cell(2, 1, 'Verified Mobile Contacts, WhatsApp Direct Links, and Pakistan Business Timing Schedule')
    sub_cell.font = Font(name=font_family, size=9.5, italic=True, color='FF94A3B8')
    sub_cell.fill = fill_banner
    sub_cell.alignment = Alignment(horizontal='center', vertical='center')
    ws3.row_dimensions[2].height = 22
    
    # KPI Cards
    kpis = [
        ('Total Leads', '65', '100% Verified Agencies', 'A', 'B', 'FF1E3A8A'),
        ('🌅 Morning Batch', '22 Leads', '11:30 AM – 1:30 PM', 'C', 'D', 'FFB45309'),
        ('🌆 Evening Baithak', '43 Leads', '6:30 PM – 9:00 PM', 'E', 'E', 'FF6B21A8'),
        ('High-Priority Web Prospects', '65', 'No Website / Subdomain', 'F', 'G', 'FF065F46'),
    ]
    
    ws3.row_dimensions[4].height = 20
    ws3.row_dimensions[5].height = 36
    ws3.row_dimensions[6].height = 18
    
    for title, val, note, start_col, end_col, color in kpis:
        col1 = openpyxl.utils.column_index_from_string(start_col)
        col2 = openpyxl.utils.column_index_from_string(end_col)
        if col1 != col2:
            ws3.merge_cells(f'{start_col}4:{end_col}4')
            ws3.merge_cells(f'{start_col}5:{end_col}5')
            ws3.merge_cells(f'{start_col}6:{end_col}6')
            
        c_title = ws3.cell(4, col1, title)
        c_title.font = Font(name=font_family, size=9, bold=True, color='FF64748B')
        c_title.alignment = align_center; c_title.fill = fill_white; c_title.border = border_subtle
        
        c_val = ws3.cell(5, col1, val)
        c_val.font = Font(name=font_family, size=16, bold=True, color=color)
        c_val.alignment = align_center; c_val.fill = fill_white; c_val.border = border_subtle
        
        c_note = ws3.cell(6, col1, note)
        c_note.font = Font(name=font_family, size=8, color='FF94A3B8')
        c_note.alignment = align_center; c_note.fill = fill_white; c_note.border = border_subtle
        
    # City Breakdown Table
    ws3.cell(8, 1, 'City Breakdown & Target Markets').font = Font(name=font_family, size=11, bold=True, color='FF1E293B')
    city_headers = ['Target City', 'Leads Count', '% of Leads', 'Key Hub Locations']
    for idx, ch in enumerate(city_headers, start=1):
        cc = ws3.cell(9, idx, ch)
        cc.font = header_navy_font; cc.fill = fill_header_navy; cc.alignment = align_center; cc.border = border_subtle
    ws3.row_dimensions[9].height = 24
    
    city_stats = [
        ('Karachi', 27, '41.5%', 'DHA Phases 5/6/8, Bahria Town, Clifton, Scheme 33'),
        ('Lahore', 12, '18.5%', 'DHA Phases 5/6, Lake City, Gulberg, Johar Town'),
        ('Peshawar', 7, '10.8%', 'DHA Peshawar, Hayatabad, University Road'),
        ('Islamabad', 6, '9.2%', 'DHA Phase 2, G-11 Markaz, F-11 Markaz, B-17'),
        ('Faisalabad', 5, '7.7%', 'Citi Housing, Canal Road, Kohinoor City'),
        ('Gujranwala', 4, '6.2%', 'Citi Housing, DC Colony, Master City'),
        ('Rawalpindi', 3, '4.6%', 'Bahria Town Phases 7/8, Chaklala Scheme 3'),
        ('Hyderabad', 1, '1.5%', 'Qasimabad, Auto Bhan Road'),
    ]
    
    for r_idx, (cname, ccount, cperc, chub) in enumerate(city_stats, start=10):
        ws3.row_dimensions[r_idx].height = 20
        c_fill = fill_white if r_idx % 2 == 0 else fill_zebra
        ws3.cell(r_idx, 1, cname).font = bold_font; ws3.cell(r_idx, 1).alignment = align_left; ws3.cell(r_idx, 1).fill = c_fill; ws3.cell(r_idx, 1).border = border_subtle
        ws3.cell(r_idx, 2, ccount).font = bold_font; ws3.cell(r_idx, 2).alignment = align_center; ws3.cell(r_idx, 2).fill = c_fill; ws3.cell(r_idx, 2).border = border_subtle
        ws3.cell(r_idx, 3, cperc).font = regular_font; ws3.cell(r_idx, 3).alignment = align_center; ws3.cell(r_idx, 3).fill = c_fill; ws3.cell(r_idx, 3).border = border_subtle
        ws3.cell(r_idx, 4, chub).font = regular_font; ws3.cell(r_idx, 4).alignment = align_left; ws3.cell(r_idx, 4).fill = c_fill; ws3.cell(r_idx, 4).border = border_subtle
        
    tot_r = 18
    ws3.cell(tot_r, 1, 'Total Verified Leads').font = Font(name=font_family, size=10, bold=True, color='FF1E293B')
    ws3.cell(tot_r, 1).fill = fill_zebra; ws3.cell(tot_r, 1).border = border_subtle
    ws3.cell(tot_r, 2, 65).font = Font(name=font_family, size=10, bold=True, color='FF1E293B'); ws3.cell(tot_r, 2).alignment = align_center; ws3.cell(tot_r, 2).fill = fill_zebra; ws3.cell(tot_r, 2).border = border_subtle
    ws3.cell(tot_r, 3, '100.0%').font = Font(name=font_family, size=10, bold=True, color='FF1E293B'); ws3.cell(tot_r, 3).alignment = align_center; ws3.cell(tot_r, 3).fill = fill_zebra; ws3.cell(tot_r, 3).border = border_subtle
    ws3.cell(tot_r, 4, 'Nationwide Pakistan Coverage').font = Font(name=font_family, size=9.5, italic=True, color='FF64748B'); ws3.cell(tot_r, 4).fill = fill_zebra; ws3.cell(tot_r, 4).border = border_subtle

    # Timing Schedule Table (Cols F & G)
    ws3.cell(8, 6, 'Outreach Timing Schedule').font = Font(name=font_family, size=11, bold=True, color='FF1E293B')
    ws3.cell(9, 6, 'Target Batch Window').font = header_amber_font; ws3.cell(9, 6).fill = fill_header_amber; ws3.cell(9, 6).border = border_subtle; ws3.cell(9, 6).alignment = align_left
    ws3.cell(9, 7, 'Leads').font = header_amber_font; ws3.cell(9, 7).fill = fill_header_amber; ws3.cell(9, 7).border = border_subtle; ws3.cell(9, 7).alignment = align_center
    
    timing_stats = [
        ('🌅 Morning Batch (11:30 AM – 1:30 PM)', 22),
        ('🌆 Evening Baithak (6:30 PM – 9:00 PM)', 43),
    ]
    for s_idx, (stitle, scnt) in enumerate(timing_stats, start=10):
        s_fill = fill_white if s_idx % 2 == 0 else fill_zebra
        c_st = ws3.cell(s_idx, 6, stitle)
        c_st.font = regular_font; c_st.alignment = align_left; c_st.fill = s_fill; c_st.border = border_subtle
        c_sc = ws3.cell(s_idx, 7, scnt)
        c_sc.font = bold_font; c_sc.alignment = align_center; c_sc.fill = s_fill; c_sc.border = border_subtle
        
    # Strategic Timing Guidance
    ws3.cell(14, 6, 'Timing Ground Rules:').font = Font(name=font_family, size=10, bold=True, color='FF1E293B')
    rules = [
        ('1. Never text before 11:30 AM (dealers not in office yet)', 'FF64748B'),
        ('2. Avoid 2:00–4:00 PM (lunch, Zuhr, registry/NOC visits)', 'FF64748B'),
        ('3. Avoid 3:30–6:00 PM (daylight property showing visits)', 'FF64748B'),
        ('4. Jummah Rule: Strictly avoid 12:30–3:30 PM on Fridays', 'FFDC2626'),
    ]
    for r_offset, (rule_text, rule_color) in enumerate(rules, start=15):
        ws3.merge_cells(f'F{r_offset}:G{r_offset}')
        cr = ws3.cell(r_offset, 6, rule_text)
        cr.font = Font(name=font_family, size=8.5, color=rule_color)
        cr.alignment = Alignment(horizontal='left', vertical='center')
        ws3.row_dimensions[r_offset].height = 18

    # Column Widths
    col_widths_s1 = {
        'A': 8.0,   # Lead ID
        'B': 38.0,  # Business Name
        'C': 22.0,  # Category
        'D': 13.0,  # City
        'E': 28.0,  # Area / Sector
        'F': 22.0,  # Contact / Director
        'G': 17.0,  # Mobile Phone
        'H': 17.0,  # WhatsApp Number
        'I': 24.0,  # 💬 WhatsApp Direct Link
        'J': 20.0,  # ⚡ Quick Chat Link
        'K': 36.0,  # Optimal Outreach Window (NEW)
        'L': 48.0,  # Timing Strategy Rationale (NEW)
        'M': 26.0,  # Recommended Days (NEW)
        'N': 32.0,  # WhatsApp Pitch URL (Raw)
        'O': 55.0,  # Personalized Pitch Message
        'P': 16.0,  # Outreach Status
        'Q': 32.0,  # Current Web Presence Status
        'R': 50.0,  # Website Pitch Opportunity
        'P': 34.0,  # Activity & Rating Proof
        'T': 55.0,  # Office Address
        'U': 20.0,  # Verified Google Maps URL
        'V': 25.0,  # Outreach Notes
    }
    for col_letter, width in col_widths_s1.items():
        ws1.column_dimensions[col_letter].width = width
        
    col_widths_s2 = {
        'A': 8.0,   # Lead ID
        'B': 38.0,  # Business Name
        'C': 13.0,  # City
        'D': 28.0,  # Area / Sector
        'E': 22.0,  # Contact Person
        'F': 17.0,  # Mobile Number
        'G': 17.0,  # WhatsApp Number
        'H': 25.0,  # 🚀 1-Click WhatsApp Pitch
        'I': 20.0,  # ⚡ Quick Chat Link
        'J': 36.0,  # Optimal Outreach Window (NEW)
        'K': 48.0,  # Timing Strategy Rationale (NEW)
        'L': 26.0,  # Recommended Days (NEW)
        'M': 55.0,  # Personalized Pitch Text
        'N': 32.0,  # Direct WhatsApp Link (URL)
        'O': 50.0,  # Website Pitch Opportunity
        'P': 16.0,  # Outreach Status
        'Q': 16.0,  # Follow-Up Date
        'R': 30.0,  # Outreach Notes & Next Step
    }
    for col_letter, width in col_widths_s2.items():
        ws2.column_dimensions[col_letter].width = width
        
    col_widths_s3 = {
        'A': 16.0, 'B': 14.0, 'C': 12.0, 'D': 35.0, 'E': 14.0, 'F': 36.0, 'G': 12.0,
    }
    for col_letter, width in col_widths_s3.items():
        ws3.column_dimensions[col_letter].width = width

    # Add official Excel Tables
    tab_outreach = Table(displayName='WhatsApp_Outreach_CRM', ref=f'A1:R{len(leads_data) + 1}')
    tab_outreach.tableStyleInfo = TableStyleInfo(name='TableStyleLight9', showFirstColumn=False, showLastColumn=False, showRowStripes=True, showColumnStripes=False)
    ws2.add_table(tab_outreach)
    
    tab_master = Table(displayName='Real_Estate_Leads_Master', ref=f'A1:V{len(leads_data) + 1}')
    tab_master.tableStyleInfo = TableStyleInfo(name='TableStyleLight8', showFirstColumn=False, showLastColumn=False, showRowStripes=True, showColumnStripes=False)
    ws1.add_table(tab_master)

    # Save logic (handle Windows file lock if user has primary file open)
    saved_paths = []
    try:
        wb.save(primary_out)
        saved_paths.append(primary_out)
        print(f"Successfully updated primary file: {primary_out}")
    except PermissionError:
        print(f"Primary file '{primary_out}' is currently OPEN in Excel. Saving to alternate file...")
        wb.save(alt_out)
        saved_paths.append(alt_out)
        print(f"Successfully saved updated file: {alt_out}")
        
    return saved_paths

if __name__ == '__main__':
    build_workbook()
