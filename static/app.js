// Antigravity WhatsApp Co-Pilot State & Controller
// Dual-Mode: Connects to local FastAPI if online, or runs seamlessly 100% offline/static on Cloudflare Pages
let allLeads = [];
let staticRawLeads = [];
let selectedLead = null;

document.addEventListener('DOMContentLoaded', () => {
  initApp();
});

async function initApp() {
  await loadStats();
  await loadLeads();
  setupEventListeners();
}

async function loadStats() {
  try {
    const res = await fetch('/api/stats');
    if (!res.ok) throw new Error('API unavailable');
    const data = await res.json();
    updateStatsUI(data);
  } catch (err) {
    try {
      const res = await fetch('stats.json');
      const data = await res.json();
      updateStatsUI(data);
    } catch (e) {
      console.warn('Using default static stats');
    }
  }
}

function updateStatsUI(data) {
  document.getElementById('stat-total').textContent = data.total_leads || 65;
  document.getElementById('stat-contacted').textContent = data.contacted || 0;
  if (document.getElementById('stat-morning')) {
    document.getElementById('stat-morning').textContent = data.morning_leads || 24;
  }
  if (document.getElementById('stat-evening')) {
    document.getElementById('stat-evening').textContent = data.evening_leads || 41;
  }
}

async function loadLeads() {
  const city = document.getElementById('city-filter').value;
  const status = document.getElementById('status-filter').value;
  const timing = document.getElementById('timing-filter') ? document.getElementById('timing-filter').value : 'all';
  const search = (document.getElementById('lead-search').value || '').toLowerCase().trim();

  try {
    const params = new URLSearchParams();
    if (city) params.append('city', city);
    if (status) params.append('status', status);
    if (timing && timing !== 'all') params.append('timing', timing);
    if (search) params.append('search', search);

    const res = await fetch(`/api/leads?${params.toString()}`);
    if (!res.ok) throw new Error('Backend API not responding');
    allLeads = await res.json();
  } catch (err) {
    // Static Fallback Mode (Cloudflare Pages / Offline)
    if (staticRawLeads.length === 0) {
      try {
        const res = await fetch('leads.json');
        staticRawLeads = await res.json();
      } catch (e) {
        console.error('Failed to load static leads.json', e);
      }
    }

    allLeads = staticRawLeads.map(l => {
      const savedStatus = localStorage.getItem('lead_status_' + l.id);
      return savedStatus ? { ...l, status: savedStatus } : l;
    }).filter(lead => {
      if (city && lead.city !== city) return false;
      if (status && lead.status !== status) return false;
      if (timing && timing !== 'all') {
        const isMorning = (lead.batch_code || '').toLowerCase().includes('morning');
        if (timing === 'morning' && !isMorning) return false;
        if (timing === 'evening' && isMorning) return false;
      }
      if (search) {
        const match = [lead.name, lead.city, lead.area, lead.phone, lead.clean_wa]
          .some(f => (f || '').toLowerCase().includes(search));
        if (!match) return false;
      }
      return true;
    });
  }

  renderLeadsList(allLeads);
  
  // Select first lead by default if not set
  if (!selectedLead && allLeads.length > 0) {
    selectLead(allLeads[0]);
  } else if (selectedLead) {
    const match = allLeads.find(l => l.id === selectedLead.id);
    if (match) selectLead(match);
  }
}

function renderLeadsList(leads) {
  const container = document.getElementById('leads-list-container');
  if (!leads || leads.length === 0) {
    container.innerHTML = '<div class="loading-state">No matching leads found.</div>';
    return;
  }

  container.innerHTML = '';
  leads.forEach(lead => {
    const card = document.createElement('div');
    card.className = `lead-card-item ${selectedLead && selectedLead.id === lead.id ? 'selected' : ''}`;
    card.onclick = () => selectLead(lead);

    const statusClass = getStatusClass(lead.status);
    const isMorning = (lead.batch_code || '').toLowerCase().includes('morning');
    const timingBadgeClass = isMorning ? 'timing-badge-morning' : 'timing-badge-evening';
    const timingBadgeText = isMorning ? '🌅 Morning' : '🌆 Evening';

    card.innerHTML = `
      <div class="lead-item-top">
        <span class="lead-item-title">${escapeHtml(lead.name)}</span>
        <div>
          <span class="city-pill">${escapeHtml(lead.city)}</span>
          <span class="timing-badge ${timingBadgeClass}">${timingBadgeText}</span>
        </div>
      </div>
      <div class="lead-item-meta">
        <span>📍 ${escapeHtml(lead.area || lead.city)}</span>
        <span>•</span>
        <span>👤 ${escapeHtml(lead.contact || 'Office')}</span>
      </div>
      <div class="lead-item-footer">
        <span class="status-tag ${statusClass}">${escapeHtml(lead.status || 'Not Contacted')}</span>
        <span style="color: #64748B; font-family: monospace;">+${lead.clean_wa}</span>
      </div>
    `;
    container.appendChild(card);
  });
}

function selectLead(lead) {
  selectedLead = lead;

  // Update card highlights
  document.querySelectorAll('.lead-card-item').forEach(el => {
    el.classList.remove('selected');
  });
  
  const isMorning = (lead.batch_code || '').toLowerCase().includes('morning');
  const badgeEl = document.getElementById('lead-timing-badge');
  if (badgeEl) {
    badgeEl.className = `timing-badge ${isMorning ? 'timing-badge-morning' : 'timing-badge-evening'}`;
    badgeEl.textContent = lead.timing_window || (isMorning ? '🌅 Morning Batch (11:30 AM – 1:30 PM)' : '🌆 Evening Baithak (6:30 PM – 9:00 PM)');
  }

  if (document.getElementById('lead-display-timing')) {
    document.getElementById('lead-display-timing').textContent = lead.timing_window || (isMorning ? '🌅 11:30 AM – 1:30 PM' : '🌆 6:30 PM – 9:00 PM');
  }
  if (document.getElementById('lead-display-days')) {
    document.getElementById('lead-display-days').textContent = lead.timing_days || 'Tue – Thu (Peak) | Sat';
  }
  if (document.getElementById('lead-display-timing-note')) {
    document.getElementById('lead-display-timing-note').textContent = lead.timing_note || 'Ground-level Pakistani real estate schedule.';
  }

  // Update target detail card
  document.getElementById('lead-city-tag').textContent = lead.city;
  document.getElementById('lead-display-name').textContent = lead.name;
  document.getElementById('lead-display-sub').textContent = `${lead.area || lead.city} • Contact: ${lead.contact || 'Listed Office Mobile'}`;
  document.getElementById('lead-display-phone').textContent = `${lead.phone} (${lead.clean_wa})`;
  document.getElementById('lead-display-web').textContent = lead.opportunity ? lead.opportunity.split('—')[0].trim() : 'No Website Listed';
  document.getElementById('lead-display-opp').textContent = lead.opportunity || 'High Priority outreach lead';

  // Update outbound launch links
  document.getElementById('lead-outbound-btn').href = lead.pitch_url;
  document.getElementById('lead-quick-btn').href = lead.quick_url;

  const demoBtn = document.getElementById('lead-demo-btn');
  if (demoBtn) {
    const demoUrl = `/demo?id=${lead.id}`;
    demoBtn.href = demoUrl;
  }

  // Sync status dropdown
  document.getElementById('crm-status-select').value = lead.status || 'Not Contacted';

  // Auto-generate initial response preview (Step 2 Value Drop)
  generateReply("Sure, send it. Show me what you built.");
}

async function generateReply(overrideQuery = null) {
  if (!selectedLead) return;

  const inputEl = document.getElementById('client-message-input');
  const message = overrideQuery || inputEl.value.trim() || "Bhai charges aur details kya hain?";
  inputEl.value = message;

  const btn = document.getElementById('generate-reply-btn');
  btn.innerHTML = '<span>⏳ Generating Sales Response...</span>';
  btn.disabled = true;

  try {
    const res = await fetch('/api/generate-reply', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        lead_id: selectedLead.id,
        incoming_message: message
      })
    });

    if (!res.ok) throw new Error('API reply unavailable');
    const data = await res.json();
    renderGeneratedOutput(data);
  } catch (err) {
    // Offline / Cloudflare Pages Expert Reply Fallback
    const localBundle = generateLocalExpertReply(selectedLead, message);
    renderGeneratedOutput(localBundle);
  } finally {
    btn.innerHTML = '<span class="btn-icon">⚡</span><span>Generate Co-Pilot Sales Reply</span>';
    btn.disabled = false;
  }
}

function generateLocalExpertReply(lead, query) {
  const msgLower = (query || '').toLowerCase().trim();
  const contact = lead.contact || '';
  const cClean = (contact && !contact.toLowerCase().startsWith('listed')) ? contact : '';
  const name = lead.name || 'bhai';
  const city = lead.city || 'Pakistan';
  const cleanWa = lead.clean_wa || '';
  const isMorning = (lead.batch_code || '').toLowerCase().includes('morning');
  const mode = isMorning ? 'builder' : 'agency';
  const theme = isMorning ? 'dark' : 'light';
  const demoUrl = `${window.location.origin}/demo?id=${lead.id}`;
  const greeting = cClean ? `Assalam-o-Alaikum ${cClean} sahib!` : "Assalam-o-Alaikum bhai!";

  // 1. Affirmative / Permission Granted ("Sure", "Send", "Ji bhejain", "Show me")
  if (['sure', 'send', 'bhej', 'dikhao', 'show', 'yes', 'ji', 'theek', 'share', 'kaun', 'who'].some(k => msgLower.includes(k))) {
    return {
      text_reply: `Here you go ${cClean || 'sahib'}: ${demoUrl}\n\nNotice two key differences here:\n1. Instead of forcing a buyer to download a 20MB PDF brochure, they see the floor plans and installment calculator on their phone in 2 seconds.\n2. The moment they tap WhatsApp, it pre-qualifies whether they want commercial or residential and routes hot buyers straight to your top closer.\n\nRight now, if even 2 or 3 serious buyers a month bounce off your current flow, that is easily 1–2 Crore in missed deal volume. How is your team currently filtering the serious investors from the time-wasters?`,
      voice_script: `Assalam-o-Alaikum ${cClean || 'sahib'}, link maine bhej diya hai, aap apne mobile par tap karke check karein. Speed aur floor plan ka layout dekhein—koi heavy brochure download karne ki zaroorat nahi parti. Sab se bari baat ye ke WhatsApp button dabate hi buyer qualify ho kar direct aapke top sales closer ke paas aata hai. Aap log abhi time-waster inquiries ko kaise filter kar rahe hain?`,
      strategy: "Alex Hormozi Value-First Delivery + Neil Rackham SPIN Selling Implication. You deliver the promised Trojan Horse fix with zero friction, then ask a diagnostic question that makes them calculate the 1-2 Crore loss of missing overseas buyers.",
      wa_direct_url: `https://wa.me/${cleanWa}?text=${encodeURIComponent(`Here you go: ${demoUrl}`)}`
    };
  }

  // 2. Price / Rate Inquiry ("How much do you charge?")
  if (['rate', 'price', 'kitne', 'cost', 'charge', 'packages', 'pese', 'fee'].some(k => msgLower.includes(k))) {
    return {
      text_reply: `${greeting} It is significantly less than the commission on a single plot or unit booking. Since we already built the base structure for ${name} above, we can have the full live system deployed and connected to your team's WhatsApp in 3 to 4 days—so you stop losing leads from this week's ad spend.\n\nDo you have 7 minutes around 4:30 PM today, or does tomorrow first thing work better for a quick call to go over the exact rollout?`,
      voice_script: `Sahib charges ki baat karein to bhai ek single plot ya unit ke commission se bhi kafi kam hai. Kyunke humne ${name} ka basic portal setup pehle hi design kar liya hai, to hum 3 se 4 din ke andar pura system aapke WhatsApp ke sath live connect kar denge taake is hafte ki marketing leads zaya na hon. Aaj shaam 4:30 baje 7 minute nikal sakte hain, ya kal subah ka time behtar rahega?`,
      strategy: "Anchoring to ROI: Never state cost as an expense; frame it against the commission of a single plot sale. The 7-minute call ask gives a binary choice that maximizes bookings.",
      wa_direct_url: `https://wa.me/${cleanWa}?text=${encodeURIComponent(`${greeting} It is significantly less than the commission on a single unit booking.`)}`
    };
  }

  // 3. Zameen.com Objection / Challenger Reframe
  return {
    text_reply: `${greeting} Bilkul sahib, Zameen aur Facebook to marketing ke liye behtareen hain. Lekin problem ye hai ke Zameen par jab koi buyer aapki listing dekhta hai, to usi screen par aapke competitors ke saste plot bhi show ho jaate hain—yani paisa aap dete hain aur lead koi aur le jata hai! Aapki apni website par 100% traffic sirf aapki hoti hai, na koi middleman na competitor ke ads. Kya mai ek 1-minute ka demo preview dikhaoon?`,
    voice_script: `Bhai aapki baat 100% theek hai ke Zameen aur FB se leads aati hain. Lekin Zameen par masla ye hai ke wo monthly lakho rupay lene ke bawajood aapke listing ke barabar mein doosre dealers ke ads chalata hai. Jabki aapka apna portal banega to har Facebook ad se aane wala buyer direct aapki inventory dekhega aur direct aapke WhatsApp par aayega. Ek dafa 30 second ka preview dekh lein, pasand aaye to baat karein.`,
    strategy: "The Challenger Sale (Re-frame the blind spot): Acknowledge Zameen's reach, then expose the hidden leak where competitors steal their buyers right next to their listing.",
    wa_direct_url: `https://wa.me/${cleanWa}?text=${encodeURIComponent(`${greeting} Bilkul sahib, Zameen is great for ads, but your own portal guarantees zero competitor ads.`)}`
  };
}

function renderGeneratedOutput(bundle) {
  // Tab 1: Text
  document.getElementById('output-text-content').textContent = bundle.text_reply;
  document.getElementById('output-wa-link').href = bundle.wa_direct_url;

  // Tab 2: Voice
  document.getElementById('output-voice-content').textContent = bundle.voice_script;

  // Tab 3: Strategy
  document.getElementById('output-strategy-content').textContent = bundle.strategy;
}

function setupEventListeners() {
  // Search & Filter
  document.getElementById('lead-search').addEventListener('input', debounce(loadLeads, 250));
  document.getElementById('city-filter').addEventListener('change', loadLeads);
  if (document.getElementById('timing-filter')) {
    document.getElementById('timing-filter').addEventListener('change', loadLeads);
  }
  document.getElementById('status-filter').addEventListener('change', loadLeads);

  // Generate Button
  document.getElementById('generate-reply-btn').addEventListener('click', () => generateReply());

  // Quick Preset Chips
  document.querySelectorAll('.chip-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const query = btn.getAttribute('data-query');
      generateReply(query);
    });
  });

  // Tab Switching
  document.querySelectorAll('.tab-btn').forEach(tabBtn => {
    tabBtn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

      tabBtn.classList.add('active');
      const targetId = tabBtn.getAttribute('data-tab');
      document.getElementById(targetId).classList.add('active');
    });
  });

  // Copy Buttons
  document.getElementById('copy-text-btn').addEventListener('click', () => {
    const text = document.getElementById('output-text-content').textContent;
    navigator.clipboard.writeText(text);
    flashButton('copy-text-btn', '✓ Copied to Clipboard!');
  });

  document.getElementById('copy-voice-btn').addEventListener('click', () => {
    const text = document.getElementById('output-voice-content').textContent;
    navigator.clipboard.writeText(text);
    flashButton('copy-voice-btn', '✓ Script Copied!');
  });

  // Status Change
  document.getElementById('crm-status-select').addEventListener('change', async (e) => {
    if (!selectedLead) return;
    const newStatus = e.target.value;
    try {
      await fetch(`/api/leads/${selectedLead.id}/status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      });
    } catch (err) {
      console.log('Status saved to local storage for offline / Cloudflare mode');
    }
    localStorage.setItem('lead_status_' + selectedLead.id, newStatus);
    selectedLead.status = newStatus;
    const leadInAll = allLeads.find(l => l.id === selectedLead.id);
    if (leadInAll) leadInAll.status = newStatus;
    renderLeadsList(allLeads);
  });
}

function flashButton(btnId, text) {
  const btn = document.getElementById(btnId);
  const orig = btn.innerHTML;
  btn.innerHTML = `<span>${text}</span>`;
  setTimeout(() => {
    btn.innerHTML = orig;
  }, 1800);
}

function getStatusClass(status) {
  if (!status) return 'status-not-contacted';
  const s = status.toLowerCase();
  if (s.includes('chat') || s.includes('initiated')) return 'status-chat-initiated';
  if (s.includes('demo') || s.includes('proposal')) return 'status-demo-sent';
  if (s.includes('closed') || s.includes('won')) return 'status-closed';
  return 'status-not-contacted';
}

function debounce(fn, ms) {
  let timer;
  return function(...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), ms);
  };
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/[&<>"']/g, function(m) {
    return {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;'
    }[m];
  });
}
