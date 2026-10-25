import os
import re
import json
import base64
import urllib.parse
from io import BytesIO
from PIL import Image
import streamlit as st

try:
    import google.generativeai as genai
except ImportError:
    genai = None

# ---------- Page Configuration ----------
st.set_page_config(
    page_title="Multimodal Construction Intelligence Platform",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Modern CSS Styling ----------
st.markdown(
    """
    <style>
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    }
    .status-pill {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .pill-safe, .pill-low { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #10b981; }
    .pill-medium { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid #f59e0b; }
    .pill-unsafe, .pill-high, .pill-critical { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #ef4444; }
    .download-btn {
        display: inline-block;
        background: linear-gradient(90deg, #2563eb, #1d4ed8);
        color: white !important;
        padding: 8px 16px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 600;
        margin-top: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Helper Functions ----------
def format_inr(amount):
    """Format INR currency dynamically into Lakhs or Crores."""
    if amount >= 1e7:
        return f"₹ {amount / 1e7:.2f} Cr"
    elif amount >= 1e5:
        return f"₹ {amount / 1e5:.2f} Lakhs"
    return f"₹ {amount:,.0f}"

def get_status_pill(label):
    """Return HTML status pill based on status or severity string."""
    norm = str(label).strip().lower()
    if norm in ["safe", "low"]:
        cls = "pill-safe"
    elif norm in ["medium", "moderate"]:
        cls = "pill-medium"
    else:
        cls = "pill-unsafe"
    return f"<span class='status-pill {cls}'>{label}</span>"

def init_gemini(active_key):
    """Initialize Gemini model safely."""
    if not genai or not active_key:
        return None
    try:
        genai.configure(api_key=active_key)
        return genai.GenerativeModel("gemini-2.5-flash")
    except Exception as e:
        st.error(f"Failed to configure Gemini API: {e}")
        return None

def parse_json_safely(raw_text):
    """Extract and parse JSON from model response."""
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_text.strip(), flags=re.MULTILINE)
    return json.loads(cleaned)

def gemini_vision_call(model, prompt, image_bytes):
    """Call Gemini Multimodal API with exception handling."""
    try:
        img = Image.open(BytesIO(image_bytes))
        response = model.generate_content([prompt, img])
        if hasattr(response, "text") and response.text:
            return response.text
        return None
    except Exception as e:
        st.error(f"Gemini vision call error: {e}")
        return None

def download_json(data, filename="report.json"):
    """Render styled JSON download button."""
    json_str = json.dumps(data, indent=2)
    b64 = base64.b64encode(json_str.encode()).decode()
    href = f"data:application/json;base64,{b64}"
    st.markdown(f"<a class='download-btn' href='{href}' download='{filename}'>📥 Download JSON Report ({filename})</a>", unsafe_allow_html=True)

# ---------- Sidebar: API Key, Navigation & Architecture ----------
st.sidebar.title("🔧 Control Center")
user_api_key = st.sidebar.text_input("🔑 Google Gemini API Key", type="password", help="Leave blank to run in Demonstration Mode")
api_key = user_api_key or os.getenv("GEMINI_API_KEY")

if api_key:
    st.sidebar.success("✅ Live Gemini AI Mode Active")
else:
    st.sidebar.info("🧪 Demo Mode Active (No API Key Supplied)")

st.sidebar.markdown("---")
st.sidebar.subheader("🧭 Feature Navigation Guide")
nav_focus = st.sidebar.radio(
    "Quick Module Reference:",
    [
        "1. Site Safety & PPE Audit (Epic 2)",
        "2. Crack Diagnostics (Epic 2)",
        "3. Planning & Valuation (Epic 3)",
        "4. Weather & Site Assistant (Epic 5)",
    ],
)

st.sidebar.markdown("---")
st.sidebar.subheader("🏛️ Architecture Overview")
st.sidebar.caption(
    "- **Vision Layer:** Google Gemini 2.5 Flash Multimodal Engine (OSHA & IS 456 compliance).\n"
    "- **Valuation Engine:** Parametric CAPEX, INR Lakhs/Crores & BoQ calculator.\n"
    "- **Generative CAD:** Pollinations AI 3D Render Pipeline.\n"
    "- **Deployment:** Stateless in-memory architecture for 1-click Streamlit Cloud hosting."
)

# ---------- Main Header & Tabs ----------
st.title("🏗️ Multimodal Construction Intelligence Platform")
st.caption("Skill Wallet Capstone Project 1 | AI-Driven Site Safety, Structural Diagnostics, Valuation & Advisory")

tab1, tab2, tab3, tab4 = st.tabs([
    "🦺 Tab 1: Site Safety & PPE Audit",
    "🔍 Tab 2: Crack Diagnostics & Integrity",
    "📈 Tab 3: Planning & Real Estate Valuation",
    "🌦️ Tab 4: Site Assistant & Weather Advisory",
])

# ==========================================================
# TAB 1: SITE SAFETY & PPE AUDIT (EPIC 2)
# ==========================================================
with tab1:
    st.header("📸 Site Safety & PPE Audit (OSHA & IS 456)")
    uploaded_ppe = st.file_uploader("Upload construction site photo (JPG/PNG)", type=["jpg", "jpeg", "png"], key="ppe_file")

    if uploaded_ppe:
        img_bytes = uploaded_ppe.read()
        st.image(img_bytes, caption="Uploaded Construction Site Image", use_container_width=True)

        model = init_gemini(api_key)
        report = None

        if model:
            with st.spinner("Analyzing worker PPE compliance & site hazards under OSHA and IS 456..."):
                prompt = (
                    "You are an expert construction safety inspector. Analyze the image for worker PPE compliance "
                    "(helmets, high-vis vests, steel-toe boots, safety harnesses) under OSHA and IS 456 standards. "
                    "Return ONLY a valid JSON object with the exact keys: "
                    "'safety_score' (integer 0-100), 'overall_status' ('Safe' or 'Unsafe'), "
                    "'ppe_detection' (list of strings showing detected/missing PPE items), and "
                    "'hazards' (list of objects with keys 'name', 'severity' [Low, Medium, High, Critical], and 'corrective_remedy')."
                )
                raw = gemini_vision_call(model, prompt, img_bytes)
                if raw:
                    try:
                        report = parse_json_safely(raw)
                    except Exception:
                        st.error("Could not parse AI output as JSON. Falling back to structured demo report.")

        if not report:
            st.info("ℹ️ Displaying Demonstration Audit Report (Supply a Gemini API key in the sidebar for live image analysis).")
            report = {
                "safety_score": 82,
                "overall_status": "Safe",
                "ppe_detection": [
                    "Hard Hats / Helmets: Detected (Compliant)",
                    "High-Visibility Vests: Detected (Compliant)",
                    "Steel-Toe Boots: Detected (Compliant)",
                    "Safety Harnesses: Missing on elevated platform (Violation)",
                ],
                "hazards": [
                    {
                        "name": "Unsecured Scaffolding Perimeter at >2m Height",
                        "severity": "High",
                        "corrective_remedy": "Install standard OSHA guardrails, toe-boards, and enforce full-body harness tie-offs per IS 3696.",
                    },
                    {
                        "name": "Exposed Rebar Ends Near Walkway",
                        "severity": "Medium",
                        "corrective_remedy": "Fit high-visibility mushroom rebar safety caps immediately to prevent impalement hazards.",
                    },
                ],
            }

        # Render Metric Cards & Status Pills
        c1, c2 = st.columns(2)
        c1.metric("Site Safety Score", f"{report.get('safety_score', 0)} / 100")
        with c2:
            st.markdown("**Overall Compliance Status**")
            st.markdown(get_status_pill(report.get("overall_status", "Safe")), unsafe_allow_html=True)

        st.subheader("✅ PPE Detection Checklist")
        for item in report.get("ppe_detection", []):
            st.success(f"✔️ {item}")

        st.subheader("⚠️ Identified Site Hazards & Corrective Remedies")
        for h in report.get("hazards", []):
            pill = get_status_pill(h.get("severity", "Medium"))
            st.markdown(
                f"<div class='metric-card'><b>{h.get('name')}</b> &nbsp; {pill}<br>"
                f"<small><b>Corrective Remedy:</b> {h.get('corrective_remedy')}</small></div>",
                unsafe_allow_html=True,
            )

        with st.expander("View Raw Structured JSON"):
            st.json(report)
        download_json(report, "ppe_safety_audit.json")

# ==========================================================
# TAB 2: CRACK DIAGNOSTICS & STRUCTURAL INTEGRITY (EPIC 2)
# ==========================================================
with tab2:
    st.header("🔍 Crack Diagnostics & Structural Integrity")
    uploaded_crack = st.file_uploader("Upload concrete or wall surface photo (JPG/PNG)", type=["jpg", "jpeg", "png"], key="crack_file")

    if uploaded_crack:
        crack_bytes = uploaded_crack.read()
        st.image(crack_bytes, caption="Uploaded Structural Surface", use_container_width=True)

        model = init_gemini(api_key)
        diag = None

        if model:
            with st.spinner("Running structural defect classification..."):
                prompt = (
                    "You are a senior structural engineer. Analyze the concrete/wall surface image and classify the defect type "
                    "(choose from: Hairline, Settlement, Structural Shear, Thermal Expansion, Spalling). "
                    "Return ONLY a valid JSON object with keys: "
                    "'defect_type' (string), 'crack_width_mm' (number), 'root_causes' (list of strings), "
                    "'recommended_repairs' (list of strings, e.g., epoxy injection, structural re-grouting), and "
                    "'urgency' (Low, Medium, High, or Critical)."
                )
                raw = gemini_vision_call(model, prompt, crack_bytes)
                if raw:
                    try:
                        diag = parse_json_safely(raw)
                    except Exception:
                        st.error("Failed to parse JSON. Showing demonstration diagnostic report.")

        if not diag:
            st.info("ℹ️ Displaying Demonstration Structural Diagnostics Report.")
            diag = {
                "defect_type": "Structural Shear",
                "crack_width_mm": 2.4,
                "root_causes": [
                    "Differential foundation settlement exceeding permissible IS 1904 limits",
                    "Inadequate shear stirrup spacing near beam-column joint",
                ],
                "recommended_repairs": [
                    "Low-viscosity structural epoxy injection under pressure",
                    "Structural re-grouting with non-shrink cementitious grout and CFRP wrapping",
                ],
                "urgency": "High",
            }

        k1, k2, k3 = st.columns(3)
        k1.metric("Classified Defect Type", diag.get("defect_type", "N/A"))
        k2.metric("Estimated Crack Width", f"{diag.get('crack_width_mm', 0)} mm")
        with k3:
            st.markdown("**Repair Urgency**")
            st.markdown(get_status_pill(diag.get("urgency", "Medium")), unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("🔎 Probable Root Causes")
            for cause in diag.get("root_causes", []):
                st.warning(f"• {cause}")
        with col_b:
            st.subheader("🛠️ Recommended Engineering Repairs")
            for rep in diag.get("recommended_repairs", []):
                st.success(f"• {rep}")

        with st.expander("View Raw Diagnostic JSON"):
            st.json(diag)
        download_json(diag, "crack_diagnostics_report.json")

# ==========================================================
# TAB 3: PLANNING & REAL ESTATE VALUATION (EPIC 3)
# ==========================================================
with tab3:
    st.header("📈 Planning, BoQ & Real Estate Valuation")
    c1, c2, c3, c4 = st.columns(4)
    structure_type = c1.selectbox("Structure Type", ["Residential", "Commercial", "Industrial", "Infrastructure"])
    built_up_sqft = c2.number_input("Built-up Area (Sq.Ft.)", min_value=500, max_value=1000000, value=10000, step=500)
    location_tier = c3.selectbox("Indian City Location Tier", ["Tier 1 (Metro)", "Tier 2 (Growing Hub)", "Tier 3 (Developing)"])
    completion_pct = c4.slider("Project Completion (%)", 0, 100, 45, 5)

    base_rates = {"Tier 1 (Metro)": 2400, "Tier 2 (Growing Hub)": 1750, "Tier 3 (Developing)": 1300}
    type_multipliers = {"Residential": 1.0, "Commercial": 1.25, "Industrial": 1.4, "Infrastructure": 1.65}
    appreciation_factors = {"Tier 1 (Metro)": 1.45, "Tier 2 (Growing Hub)": 1.25, "Tier 3 (Developing)": 1.12}

    total_budget = built_up_sqft * base_rates[location_tier] * type_multipliers[structure_type]
    capex_incurred = total_budget * (completion_pct / 100.0)
    current_valuation = (total_budget * (0.4 + 0.6 * (completion_pct / 100.0))) * appreciation_factors[location_tier]

    steel_tonnes = (built_up_sqft * 4.8) / 1000.0
    cement_bags = built_up_sqft * 0.42

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Project Budget", format_inr(total_budget))
    m2.metric("Capital Expenditure Incurred", format_inr(capex_incurred), f"{completion_pct}% Disbursed")
    m3.metric("Current Market Asset Valuation", format_inr(current_valuation))

    st.subheader("🧱 Estimated Material Requirements (IS 456 Norms)")
    b1, b2 = st.columns(2)
    b1.metric("Structural Steel (Fe 500D)", f"{steel_tonnes:,.2f} Metric Tonnes ({steel_tonnes*1000:,.0f} kg)")
    b2.metric("OPC 53 Grade Cement", f"{cement_bags:,.0f} Bags ({cement_bags*0.05:,.2f} Metric Tonnes)")

    st.subheader(f"📊 Milestone Progress ({completion_pct}% Complete)")
    st.progress(completion_pct / 100.0)

    st.markdown("---")
    st.subheader("🎨 Conceptual 3D Architectural Rendering (Pollinations AI)")
    default_render_prompt = (
        f"Architectural 3D isometric photorealistic render of a modern {structure_type.lower()} building "
        f"in an Indian {location_tier.split()[0]} {location_tier.split()[1]} city, {built_up_sqft} sqft scale, glass and concrete facade, daylight, 8k"
    )
    custom_render_prompt = st.text_input("Customize 3D Render Prompt:", value=default_render_prompt)
    if st.button("🚀 Generate Conceptual 3D Render"):
        encoded = urllib.parse.quote(custom_render_prompt)
        pollinations_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=576&nologo=true"
        st.image(pollinations_url, caption="Generated via Pollinations AI Engine", use_container_width=True)

# ==========================================================
# TAB 4: DAILY SITE ASSISTANT & WEATHER-AWARE ADVISORY (EPIC 5)
# ==========================================================
with tab4:
    st.header("🌦️ Daily Site Assistant & Weather-Aware Advisory")
    weather = st.selectbox("Select Active Site Weather Condition:", ["Normal", "High Wind", "Heavy Rain", "Extreme Heat"])

    advisories = {
        "Normal": {
            "level": "Low",
            "protocol": "All crane, excavation, and concreting operations cleared. Maintain standard 7-to-14 day wet curing protocol per IS 456.",
        },
        "High Wind": {
            "level": "Critical",
            "protocol": "SUSPEND tower crane lifting operations immediately (>32 km/h wind gusts). Secure loose scaffolding sheets, formwork panels, and perimeter fencing.",
        },
        "Heavy Rain": {
            "level": "High",
            "protocol": "ELECTRICAL HAZARD MITIGATION: Isolate outdoor distribution boards, inspect RCCBs, and elevate cables off wet ground. Pause exposed slab concreting and cover fresh pours with tarpaulins.",
        },
        "Extreme Heat": {
            "level": "High",
            "protocol": "CONCRETE CURING PROTOCOL: Apply continuous ponding or wet hessian cloth immediately after surface thumb-hardening and use evaporation retarders to prevent plastic shrinkage cracks. Enforce 15-min hourly worker hydration breaks.",
        },
    }

    active_adv = advisories[weather]
    st.markdown(
        f"<div class='metric-card'><b>Active Weather Protocol: {weather}</b> &nbsp; "
        f"{get_status_pill(active_adv['level'])}<br><br>{active_adv['protocol']}</div>",
        unsafe_allow_html=True,
    )

    st.subheader("🤖 Interactive Multi-Turn Construction Engineering Assistant")
    if "assistant_history" not in st.session_state:
        st.session_state.assistant_history = [
            {
                "role": "assistant",
                "content": "Hello Engineer! Ask me anything about IS 456 standards, structural curing, BoQ estimation, or site safety.",
            }
        ]

    for msg in st.session_state.assistant_history:
        st.chat_message(msg["role"]).write(msg["content"])

    user_query = st.chat_input("Ask a construction engineering question (e.g., M25 mix ratio, rebar lap length)...")
    if user_query:
        st.session_state.assistant_history.append({"role": "user", "content": user_query})
        st.chat_message("user").write(user_query)

        with st.spinner("Consulting engineering knowledge base..."):
            model = init_gemini(api_key)
            if model:
                history_text = f"System: You are an expert civil and structural construction engineering assistant. Current site weather is {weather}. Cite IS 456 / OSHA standards where relevant.\n"
                for turn in st.session_state.assistant_history:
                    history_text += f"{turn['role'].capitalize()}: {turn['content']}\n"
                try:
                    res = model.generate_content(history_text)
                    reply = getattr(res, "text", None) or "Please verify site parameters and IS 456 guidelines."
                except Exception as e:
                    reply = f"API Error ({e}). Fallback Advisory: Under {weather} conditions, adhere strictly to IS 456 curing and OSHA PPE rules."
            else:
                reply = (
                    f"**[Demo Mode Advisory | Weather: {weather}]** For *{user_query}*, ensure compliance with **IS 456:2000** "
                    f"(minimum grade M20 for RCC, water-cement ratio ≤ 0.50, cover blocks in place) and verify 100% PPE compliance before execution."
                )

            st.session_state.assistant_history.append({"role": "assistant", "content": reply})
            st.chat_message("assistant").write(reply)

st.markdown("---")
st.caption("© 2026 Multimodal Construction Intelligence Platform | Skill Wallet Capstone Project 1")
