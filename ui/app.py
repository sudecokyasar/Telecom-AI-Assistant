import streamlit as st
import requests
import os
import time
import base64
import json
from pathlib import Path
import sys
from pathlib import Path

# Proje kök dizinini Python yoluna ekle
root_path = Path(__file__).resolve().parent.parent
sys.path.append(str(root_path))
# ==============================================================================
# 1. SAYFA YAPILANDIRMASI & API URL
# ==============================================================================
st.set_page_config(
    page_title="Canlı Telekom Asistanı",

    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

# ==============================================================================
# 2. SESSION STATE
# ==============================================================================
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "dark"

if "messages" not in st.session_state:
    st.session_state.messages = []


# ==============================================================================
# 3. DİNAMİK TEMA VE CSS YÖNETİMİ
# ==============================================================================
if st.session_state.theme_mode == "dark":
    THEME_CSS = """
    :root {
        --bg-main: #070B14;
        --bg-panel: rgba(15, 23, 42, 0.75);
        --sidebar-bg: rgba(10, 15, 29, 0.95);
        --border-color: rgba(255, 255, 255, 0.1);
        --text-primary: #F1F5F9;
        --text-secondary: #94A3B8;
        --card-border: rgba(255, 255, 255, 0.1);
        --chat-ai-bg: linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(30, 41, 59, 0.75) 100%);
        --chat-ai-text: #F8FAFC;
        --chat-user-bg: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%);
        --chat-user-text: #FFFFFF;
        --chat-input-bg: #0F172A;
        --chat-input-border: rgba(0, 210, 255, 0.3);
        --chat-input-text: #FFFFFF;
        --bottom-bar-bg: #070B14;
        --bottom-bar-border: rgba(255, 255, 255, 0.08);
        --btn-bg: rgba(30, 41, 59, 0.6);
        --btn-text: #E2E8F0;
        --btn-border: rgba(255, 255, 255, 0.1);
        --meter-empty: rgba(255, 255, 255, 0.08);
        --header-bg: linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(30, 41, 59, 0.7) 100%);
    }
    .stApp {
        background-image: 
            radial-gradient(at 0% 0%, rgba(59, 130, 246, 0.18) 0px, transparent 45%),
            radial-gradient(at 100% 0%, rgba(168, 85, 247, 0.15) 0px, transparent 40%),
            radial-gradient(at 50% 100%, rgba(236, 72, 153, 0.12) 0px, transparent 50%) !important;
    }
    """
else:
    THEME_CSS = """
    :root {
        --bg-main: #F8FAFC;
        --bg-panel: #FFFFFF;
        --sidebar-bg: #FFFFFF;
        --border-color: #E2E8F0;
        --text-primary: #0F172A;
        --text-secondary: #64748B;
        --card-border: #E2E8F0;
        --chat-ai-bg: #FFFFFF;
        --chat-ai-text: #1E293B;
        --chat-user-bg: linear-gradient(135deg, #0066FF, #0052CC);
        --chat-user-text: #FFFFFF;
        --chat-input-bg: #FFFFFF;
        --chat-input-border: #CBD5E1;
        --chat-input-text: #0F172A;
        --bottom-bar-bg: #F8FAFC;
        --bottom-bar-border: #E2E8F0;
        --btn-bg: #FFFFFF;
        --btn-text: #334155;
        --btn-border: #E2E8F0;
        --meter-empty: #E2E8F0;
        --header-bg: #FFFFFF;
    }
    .stApp {
        background-image: 
            radial-gradient(at 0% 0%, rgba(0, 102, 255, 0.06) 0px, transparent 45%),
            radial-gradient(at 100% 100%, rgba(0, 210, 255, 0.06) 0px, transparent 45%) !important;
    }
    """

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600;700&display=swap');

{THEME_CSS}

html, body, [class*="css"], .stApp {{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background-color: var(--bg-main) !important;
    color: var(--text-primary) !important;
}}

#MainMenu, footer {{ visibility: hidden !important; height: 0px !important; }}
header {{ background: transparent !important; }}

/* Sidebar Butonu */
[data-testid="stSidebarCollapsedControl"] {{
    display: block !important;
    color: #00D2FF !important;
    background: var(--bg-panel) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
    box-shadow: 0 0 12px rgba(0, 210, 255, 0.15) !important;
    margin: 8px !important;
}}

.block-container {{
    padding-top: 1.4rem !important;
    padding-bottom: 7rem !important;
    max-width: 1080px !important;
}}

/* Sidebar */
[data-testid="stSidebar"] {{
    background: var(--sidebar-bg) !important;
    backdrop-filter: blur(20px) !important;
    border-right: 1px solid var(--border-color) !important;
}}

[data-testid="stSidebar"] section[data-testid="stSidebarContent"] > div {{
    gap: 12px !important;
    padding-top: 1.0rem !important;
}}

/* Kartlar */
[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {{
    background: var(--bg-panel) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 16px !important;
    padding: 16px !important;
    margin-bottom: 4px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04) !important;
}}

/* Header */
.header-container {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 24px;
    background: var(--header-bg);
    border: 1px solid var(--border-color);
    border-radius: 18px;
    margin-bottom: 20px;
    box-shadow: 0 8px 30px rgba(0, 102, 255, 0.08);
}}

.brand-wrapper {{ display: flex; align-items: center; gap: 15px; }}

.logo-glow {{
    width: 48px; height: 48px;
    background: linear-gradient(135deg, rgba(0, 210, 255, 0.2), rgba(168, 85, 247, 0.2));
    border: 1px solid rgba(0, 210, 255, 0.4);
    border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 0 20px rgba(0, 210, 255, 0.25);
}}

.header-title {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.3rem; font-weight: 800;
    color: var(--text-primary);
    margin: 0;
}}

.status-badge {{
    display: flex; align-items: center; gap: 8px;
    padding: 6px 14px; border-radius: 9999px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.74rem; font-weight: 700;
}}
.badge-online {{
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.4);
    color: #10B981;
}}
.badge-offline {{
    background: rgba(239, 68, 68, 0.15);
    border: 1px solid rgba(239, 68, 68, 0.4);
    color: #EF4444;
}}

.pulse-dot {{
    width: 8px; height: 8px; border-radius: 50%; background: #10B981;
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
    animation: pulse 1.8s infinite;
}}
@keyframes pulse {{
    0% {{ box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }}
    70% {{ box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }}
    100% {{ box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }}
}}

/* Profil */
.profile-row {{ display: flex; align-items: center; gap: 12px; }}
.profile-avatar {{
    width: 42px; height: 42px;
    background: linear-gradient(135deg, #EC4899, #8B5CF6);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Space Grotesk', sans-serif; font-weight: 800; color: white;
}}
.tier-badge {{
    display: inline-block; padding: 3px 8px;
    background: linear-gradient(90deg, #F59E0B, #EF4444);
    border-radius: 6px; font-size: 0.65rem; font-weight: 800;
    color: #FFFFFF; font-family: 'Space Grotesk', sans-serif;
}}

/* Segmentli Ölçerler */
.meter-wrapper {{ margin-top: 14px; margin-bottom: 4px; }}
.meter-row {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }}
.meter-label {{ font-size: 0.82rem; font-weight: 600; color: var(--text-secondary); }}
.meter-value {{ font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; font-weight: 700; }}
.meter-bars {{ display: flex; gap: 5px; width: 100%; }}
.meter-seg {{ flex: 1; height: 7px; border-radius: 4px; background: var(--meter-empty); }}

.seg-cyan.on {{ background: linear-gradient(90deg, #00D2FF, #3B82F6); box-shadow: 0 0 8px rgba(0, 210, 255, 0.4); }}
.seg-green.on {{ background: linear-gradient(90deg, #10B981, #34D399); box-shadow: 0 0 8px rgba(16, 185, 129, 0.4); }}
.seg-purple.on {{ background: linear-gradient(90deg, #8B5CF6, #EC4899); box-shadow: 0 0 8px rgba(139, 92, 246, 0.4); }}

/* Fatura */
.bill-amount {{
    font-family: 'JetBrains Mono', monospace; font-size: 1.35rem; font-weight: 800;
    background: linear-gradient(90deg, #F59E0B, #FB923C);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}

/* Chat Balonları */
[data-testid="stChatMessage"] {{ background: transparent !important; padding: 0.7rem 0 !important; }}

[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarCustom"]) div[data-testid="stMarkdownContainer"],
[data-testid="stChatMessage"]:has(img[alt="assistant avatar"]) div[data-testid="stMarkdownContainer"] {{
    background: var(--chat-ai-bg) !important;
    border: 1px solid var(--border-color) !important;
    border-left: 4px solid #00D2FF !important;
    border-radius: 4px 16px 16px 16px !important;
    padding: 18px 22px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06) !important;
    color: var(--chat-ai-text) !important;
    line-height: 1.65 !important;
}}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) div[data-testid="stMarkdownContainer"],
[data-testid="stChatMessage"]:has(img[alt="user avatar"]) div[data-testid="stMarkdownContainer"] {{
    background: var(--chat-user-bg) !important;
    border-radius: 16px 4px 16px 16px !important;
    padding: 14px 18px !important;
    color: var(--chat-user-text) !important;
    box-shadow: 0 4px 15px rgba(37, 99, 235, 0.25) !important;
}}

/* Meta Rozetler */
.meta-strip {{
    display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px;
    padding-top: 12px; border-top: 1px solid var(--border-color);
}}
.meta-chip {{
    font-family: 'JetBrains Mono', monospace; font-size: 0.72rem;
    padding: 4px 10px; border-radius: 6px; font-weight: 600;
}}
.chip-cat {{ background: rgba(0, 210, 255, 0.15); border: 1px solid rgba(0, 210, 255, 0.4); color: #00D2FF; }}
.chip-conf {{ background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.4); color: #10B981; }}
.chip-doc {{ background: rgba(168, 85, 247, 0.15); border: 1px solid rgba(168, 85, 247, 0.4); color: #A855F7; }}

/* Butonlar */
.stButton > button {{
    background: var(--btn-bg) !important;
    border: 1px solid var(--btn-border) !important;
    color: var(--btn-text) !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    transition: all 0.2s ease !important;
}}

.stButton > button:hover {{
    border-color: #00D2FF !important;
    color: #00D2FF !important;
    transform: translateY(-1px) !important;
}}

/* Alt Sabit Çubuk */
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
.stChatFloatingInputContainer,
.stChatInputContainer {{
    background-color: var(--bottom-bar-bg) !important;
    background: var(--bottom-bar-bg) !important;
    border-top: 1px solid var(--bottom-bar-border) !important;
}}

/* Chat Input Dış Çerçevesi ve Tüm İç Katmanları */
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] div[data-baseweb="base-input"],
[data-testid="stChatInput"] div[data-baseweb="textarea"],
[data-testid="stChatInput"] textarea {{
    background-color: var(--chat-input-bg) !important;
    background: var(--chat-input-bg) !important;
    color: var(--chat-input-text) !important;
    -webkit-text-fill-color: var(--chat-input-text) !important;
}}

/* Dış Kenarlık & Yuvarlatma */
[data-testid="stChatInput"] {{
    border-radius: 14px !important;
    border: 1px solid var(--chat-input-border) !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05) !important;
}}

/* BaseWeb İç Kenarlıklarını Temizle */
[data-testid="stChatInput"] div[data-baseweb="base-input"],
[data-testid="stChatInput"] div[data-baseweb="textarea"] {{
    border: none !important;
    box-shadow: none !important;
}}

/* Placeholder (İpucu Metni) */
[data-testid="stChatInput"] textarea::placeholder {{
    color: var(--text-secondary) !important;
    opacity: 0.8 !important;
}}

/* Gönder Butonu */
[data-testid="stChatInput"] button {{
    background: transparent !important;
    color: var(--text-secondary) !important;
    border: none !important;
}}

[data-testid="stChatInput"] button:hover {{
    color: #00D2FF !important;
}}
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# 4. SİNYAL SİMGESİ & AVATARLAR
# ==============================================================================
def signal_mark_svg():
    return '''<svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="3" y="18" width="4" height="7" rx="1.5" fill="#00D2FF"/>
        <rect x="9.5" y="13" width="4" height="12" rx="1.5" fill="#3B82F6"/>
        <rect x="16" y="8" width="4" height="17" rx="1.5" fill="#8B5CF6"/>
        <rect x="22.5" y="3" width="4" height="22" rx="1.5" fill="#EC4899"/>
    </svg>'''


def svg_avatar(kind="assistant"):
    if kind == "assistant":
        svg = '''<svg width="34" height="34" viewBox="0 0 34 34" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="avatar-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#00D2FF" />
                    <stop offset="50%" stop-color="#3B82F6" />
                    <stop offset="100%" stop-color="#8B5CF6" />
                </linearGradient>
            </defs>
            <rect width="34" height="34" rx="10" fill="url(#avatar-grad)" />
            <path d="M17 8V11M11 15H23M13 15V22C13 23.1 13.9 24 15 24H19C20.1 24 21 23.1 21 22V15M14 18H14.01M20 18H20.01" stroke="white" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
    else:
        svg = '''<svg width="34" height="34" viewBox="0 0 34 34" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="u-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#EC4899" />
                    <stop offset="100%" stop-color="#F43F5E" />
                </linearGradient>
            </defs>
            <rect width="34" height="34" rx="10" fill="url(#u-grad)" />
            <text x="17" y="23" font-family="'Space Grotesk', sans-serif" font-size="16" font-weight="800" fill="white" text-anchor="middle"></text>
        </svg>'''
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


ASSISTANT_AVATAR = svg_avatar("assistant")
USER_AVATAR = svg_avatar("user")


# ==============================================================================
# 5. BACKEND İLETİŞİMİ
# ==============================================================================
def call_backend_api(query: str, history: list = None):
    try:
        payload = {
            "ticket_text": query,
            "chat_history": history if history else []
        }
        response = requests.post(
            f"{API_BASE_URL}/resolve-ticket",
            json=payload,
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            sources = data.get("retrieved_sources", [])
            source_tags = "".join([f'<span class="meta-chip chip-doc"> REF: {s}</span>' for s in sources]) \
                if sources else '<span class="meta-chip chip-doc"> Genel Kılavuz</span>'

            formatted_res = (
                f"{data.get('ai_resolution')}\n\n"
                f'<div class="meta-strip">'
                f'<span class="meta-chip chip-cat"> Kategori: <b>{data.get("category")}</b></span>'
                f'<span class="meta-chip chip-conf"> Güven: <b>%{data.get("confidence_score")}</b></span>'
                f'{source_tags}'
                f'</div>'
            )
            return formatted_res
        else:
            return f" Sunucu Hatası ({response.status_code}): {response.text}"
    except Exception as e:
        return f" Bir hata oluştu: {str(e)}"


# ==============================================================================
# 6. YARDIMCI: SEGMENTLİ ÖLÇER
# ==============================================================================
def render_colorful_meter(label, used_display, total_display, pct, seg_class, text_color):
    segments = 10
    filled = round(max(0, min(1, pct)) * segments)
    bars_html = "".join(
        f'<div class="meter-seg {seg_class if i < filled else ""}"></div>' for i in range(segments)
    )
    st.markdown(
        f'<div class="meter-wrapper">'
        f'  <div class="meter-row">'
        f'    <span class="meter-label">{label}</span>'
        f'    <span class="meter-value" style="color:{text_color};">{used_display} / {total_display}</span>'
        f'  </div>'
        f'  <div class="meter-bars">{bars_html}</div>'
        f'</div>',
        unsafe_allow_html=True
    )



# ==============================================================================
# 7. SIDEBAR (TAMAMEN DİNAMİK JSON ENTEGRASYONU)
# ==============================================================================
CAMARA_FILE_PATH = Path("data/camara_registry.json")
api_online = False
# 1. JSON dosyasını oku
registry_data = {}
if CAMARA_FILE_PATH.exists():
    try:
        with open(CAMARA_FILE_PATH, "r", encoding="utf-8") as f:
            registry_data = json.load(f)
    except Exception as e:
        st.sidebar.error(f"Veritabanı Okuma Hatası: {e}")

# 2. JSON'daki telefon numaraları listesi
phone_numbers = list(registry_data.keys())

with st.sidebar:
    # Tema Değiştirme Butonu
    current_theme = st.session_state.theme_mode
    theme_btn_label = " Aydınlık Mod" if current_theme == "dark" else " Karanlık Mod"
    
    if st.button(theme_btn_label, use_container_width=True):
        st.session_state.theme_mode = "light" if current_theme == "dark" else "dark"
        st.rerun()

    if not phone_numbers:
        st.warning("`data/camara_registry.json` içinde abone kaydı bulunamadı.")
    else:
        # JSON'daki kayıtlar arasından aktif hattı seç
        selected_phone = st.selectbox(
            " Aktif Abone Hattı:",
            options=phone_numbers,
            index=0
        )
        
        # Seçilen abonenin ham verilerini çek
        subscriber = registry_data.get(selected_phone, {})
        device = subscriber.get("device_status", {})
        sim = subscriber.get("sim_status", {})
        bill = subscriber.get("billing_summary", {})

        # Alanları JSON'dan doğrudan haritala
        net_used = float(bill.get("internet_used_gb", 0))
        net_total = float(bill.get("internet_total_gb", 0))
        min_left = int(bill.get("min_left", 0))
        sms_left = int(bill.get("sms_left", 0))
        current_bill = float(bill.get("current_bill_tl", 0.0))
        sim_type = sim.get("sim_type", "SIM")
        roaming_enabled = sim.get("roaming_enabled", False)
        net_type = device.get("network_type", "4G/5G")
        
        # Kalan dakika/SMS oranları
        min_total = 2000
        min_used = max(0, min_total - min_left)
        sms_total = 1000
        sms_used = max(0, sms_total - sms_left)

        # 7.1 Profil Kartı
        roaming_html = (
            '<span style="color:#10B981; font-size:0.72rem; font-weight:700;">● Roaming Aktif</span>' 
            if roaming_enabled 
            else '<span style="color:#EF4444; font-size:0.72rem; font-weight:700;">● Roaming Kapalı</span>'
        )

        with st.container(border=True):
            st.markdown(f"""
            <div class="profile-row">
                <div class="profile-avatar">M</div>
                <div>
                    <div style="font-weight: 700; color: var(--text-primary); font-size: 0.95rem; line-height: 1.2;">Müşteri</div>
                </div>
            </div>
            <div style="font-size: 0.78rem; color: var(--text-secondary); margin-top: 12px; margin-bottom: 6px; line-height: 1.4;">
                Hat: <span style="color: #00D2FF; font-family:'JetBrains Mono',monospace; font-weight:600;">{selected_phone}</span> 
                <span style="font-size:0.7rem; background:rgba(255,255,255,0.08); padding:2px 6px; border-radius:4px; margin-left:4px;">{sim_type}</span>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-top: 4px;">
                {roaming_html}
                <span style="font-family:'JetBrains Mono',monospace; font-size:0.70rem; color:var(--text-secondary);">{net_type}</span>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<div style='padding-bottom: 6px;'></div>", unsafe_allow_html=True)

        # 7.2 Paket Kullanımı
        net_pct = net_used / net_total if net_total > 0 else 0
        min_pct = min_used / min_total if min_total > 0 else 0
        sms_pct = sms_used / sms_total if sms_total > 0 else 0

        with st.container(border=True):
            st.markdown(
                '<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">'
                '<span style="font-weight:700; font-size:0.88rem; color:var(--text-primary);"> Paket Kullanımı</span>'
                '<span style="font-size:0.72rem; color:#00D2FF; font-weight:700; background:rgba(0,210,255,0.12); padding:3px 8px; border-radius:6px;">Canlı Veri</span>'
                '</div>',
                unsafe_allow_html=True
            )
            render_colorful_meter(" İnternet", f"{net_used} GB", f"{net_total} GB", net_pct, "seg-cyan on", "#00D2FF")
            render_colorful_meter(" Dakika", f"{min_used} DK", f"{min_total} DK", min_pct, "seg-green on", "#10B981")
            render_colorful_meter(" SMS", f"{sms_used} SMS", f"{sms_total} SMS", sms_pct, "seg-purple on", "#A855F7")
            st.markdown("<div style='padding-bottom: 6px;'></div>", unsafe_allow_html=True)

        # 7.3 Fatura
        with st.container(border=True):
            c_f1, c_f2 = st.columns([1.8, 1.2])
            with c_f1:
                st.caption("Güncel Fatura Tutarı")
                st.markdown(f'<div class="bill-amount" style="margin-top:2px; margin-bottom:6px; line-height:1.2;">{current_bill:.2f} TL</div>', unsafe_allow_html=True)
            with c_f2:
                st.markdown('<div style="margin-top:10px; margin-bottom:6px; font-size:0.72rem; background:rgba(245,158,11,0.15); color:#F59E0B; border:1px solid rgba(245,158,11,0.4); font-weight:700; padding:5px 8px; border-radius:6px; text-align:center;">Güncel Dönem</div>', unsafe_allow_html=True)
            st.markdown("<div style='padding-bottom: 6px;'></div>", unsafe_allow_html=True)

    # 7.4 Hızlı Aksiyonlar
    st.markdown("<div style='font-size:0.78rem; font-weight:800; color:var(--text-secondary); margin: 0 0 10px 2px; letter-spacing:0.5px;'> HIZLI İŞLEMLER</div>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button(" Fatura İncele", use_container_width=True):
            st.session_state.pending_prompt = "Faturamda fazla kullanım bedeli var, detayları inceleyip açıklar mısınız?"
        if st.button(" Hız Testi", use_container_width=True):
            st.session_state.pending_prompt = "İnternet hızım çok yavaşladı, hız problemi yaşıyorum."
    with col_b:
        if st.button(" Tarife Değiştir", use_container_width=True):
            st.session_state.pending_prompt = "Tarifemi değiştirmek veya sözleşmemi iptal etmek istiyorum."
        if st.button(" Arıza Kaydı", use_container_width=True):
            st.session_state.pending_prompt = "Modemimde kırmızı ışık yanıyor ve internet tamamen kesildi, arıza kaydı açar mısınız?"

    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    if st.button(" Sohbeti Temizle", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ==============================================================================
# 8. HEADER
# ==============================================================================
if api_online:
    status_html = '<div class="status-badge badge-online"><span class="pulse-dot"></span><span>BAĞLANTI AKTİF</span></div>'
else:
    status_html = '<div class="status-badge badge-offline"><span> SUNUCU KAPALI</span></div>'

st.markdown(f"""
<div class="header-container">
    <div class="brand-wrapper">
        <div class="logo-glow">{signal_mark_svg()}</div>
        <div>
            <div class="header-title">Telekom AI Destek Asistanı</div>
            <div style="font-size:0.8rem; color:var(--text-secondary);">ML Kategori Tahmini & RAG Kılavuz Çözüm Operatörü</div>
        </div>
    </div>
    {status_html}
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# 9. KARŞILAMA EKRANI & HIZLI KARTLAR
# ==============================================================================
if len(st.session_state.messages) == 0:
    st.markdown("""
    <div style='text-align:center; padding: 20px 0 16px 0;'>
        <h2 style='font-family:"Space Grotesk", sans-serif; font-size:1.8rem; font-weight:800; background:linear-gradient(90deg, #00D2FF, #3B82F6, #EC4899); -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin-bottom:6px;'>
            Nasıl yardımcı olabilirim?
        </h2>
        <p style='color:var(--text-secondary); font-size:0.95rem;'>
            Hattınız, faturanız, hız probleminiz veya teknik arızalarla ilgili talebinizi iletebilirsiniz.
        </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button(" Modemdeki İnternet Işığı Kırmızı Yanıyor", use_container_width=True):
            st.session_state.pending_prompt = "Modem üzerindeki internet ışığı kırmızı yanıp sönüyor ve bağlantım 2 saattir tamamen kesik. Acil destek rica ediyorum."
        if st.button(" Bu Ay Gelen Faturam Neden Yüksek?", use_container_width=True):
            st.session_state.pending_prompt = "Bu ay gelen faturamda 150 TL fazladan kullanım bedeli yansıtılmış. Faturama itiraz edip iade talep ediyorum."
    with c2:
        if st.button(" Yeni Telefon İçin eSIM Nasıl Alınır?", use_container_width=True):
            st.session_state.pending_prompt = "Yeni telefonuma eSIM QR kodunu okuttum ancak 'Geçersiz SIM / Servis Yok' hatası veriyor, nasıl aktif edebilirim?"
        if st.button(" Taahhüt & Cayma Bedeli Hesaplama", use_container_width=True):
            st.session_state.pending_prompt = "Taahhüt süremi ve sözleşmemi sonlandırmak istiyorum, cayma bedeli hesaplaması hakkında bilgi alabilir miyim?"


# ==============================================================================
# 10. MESAJ GEÇMİŞİ
# ==============================================================================
for msg in st.session_state.messages:
    avatar = USER_AVATAR if msg["role"] == "user" else ASSISTANT_AVATAR
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"], unsafe_allow_html=True)


# ==============================================================================
# 11. GİRDİ YÖNETİMİ & RAG ÇALIŞTIRMA
# ==============================================================================
prompt_input = st.chat_input("Talebinizi buraya yazın (Örn: 'İnternetim çok yavaş', 'Faturam yüksek')...")
active_prompt = None

if "pending_prompt" in st.session_state and st.session_state.pending_prompt:
    active_prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None
elif prompt_input:
    active_prompt = prompt_input

if active_prompt:
    st.session_state.messages.append({"role": "user", "content": active_prompt})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(active_prompt)

    with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
        with st.spinner(" Kılavuzlar taranıyor ve çözüm üretiliyor..."):
            full_response = call_backend_api(active_prompt, history=st.session_state.messages)

            placeholder = st.empty()
            displayed_text = ""
            for word in full_response.split(" "):
                displayed_text += word + " "
                placeholder.markdown(displayed_text, unsafe_allow_html=True)
                time.sleep(0.012)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.rerun()
