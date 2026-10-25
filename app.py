import os
import json
import re
import streamlit as st
from io import BytesIO
from PIL import Image
import base64

os.environ.setdefault("STREAMLIT_CONFIG_DIR", os.path.join(os.path.dirname(__file__), ".streamlit"))

try:
    import google.generativeai as genai
except ImportError:
    genai = None

st.set_page_config(page_title="Multimodal Construction Intelligence", layout="wide")

# ---------- Sidebar & Configuration ----------
st.sidebar.title("🔧 Configuration")
input_key = st.sidebar.text_input("Google Gemini API Key", type="password", key="gemini_api_key_input")
api_key = input_key or os.getenv("GEMINI_API_KEY")

st.sidebar.markdown("---")
st.sidebar.header("📚 Architecture Overview")
st.sidebar.write("* **Tab 1 – Site Safety & PPE Audit** – Upload site photos, analyse PPE compliance, generate safety report.")
st.sidebar.write("* **Tab 2 – Crack Diagnostics & Structural Integrity** – Upload concrete images, classify defects and suggest repairs.")
st.sidebar.write("* **Tab 3 – Planning & Real‑Estate Valuation** – Input project parameters, compute budget, valuation and material needs.")
st.sidebar.write("* **Tab 4 – Daily Site Assistant & Weather‑Aware Advisory** – Select weather, receive safety alerts, chat with an engineering assistant.")

# ---------- Helper Functions ----------
def init_gemini(active_key):
    """Initialize Gemini client if key is present."""
    if not genai:
        st.warning("google-generativeai package not installed. Multimodal features will be unavailable.")
        return None
    if not active_key:
        st.info("Running in demonstration mode – no Gemini calls will be made.")
        return None
    try:
        genai.configure(api_key=active_key)
        return genai.GenerativeModel('gemini-2.5-flash')
    except Exception as e:
        st.error(f"Failed to configure Gemini: {e}")
        return None

def clean_json_response(text):
    """Strip markdown code fences if Gemini wraps JSON in ```json ... ```."""
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.MULTILINE)
    return json.loads(cleaned)

def gemini_vision_call(model, prompt, image_bytes):
    """Make a Gemini multimodal request."""
    try:
        img = Image.open(BytesIO(image_bytes))
        response = model.generate_content([prompt, img])
        if hasattr(response, "text") and response.text:
            return response.text
        st.error("Gemini returned an empty response.")
        return None
    except Exception as e:
        st.error(f"Gemini request failed: {e}")
        return None

def download_json(data, filename="report.json"):
    json_str = json.dumps(data, indent=2)
    b64 = base64.b64encode(json_str.encode()).decode()
    href = f"data:application/json;base64,{b64}"
    st.markdown(f"<a href='{href}' download='{filename}'>📥 Download JSON Report</a>", unsafe_allow_html=True)

# ---------- Main App ----------
st.title("🏗️ Multimodal Construction Intelligence Platform")

tab1, tab2, tab3, tab4 = st.tabs([
    "Site Safety & PPE Audit",
    "Crack Diagnostics & Structural Integrity",
    "Planning & Real‑Estate Valuation",
    "Daily Site Assistant & Weather‑Aware Advisory",
])

# ---- Tab 1: Site Safety & PPE Audit ----
with tab1:
    st.header("📸 Site Safety & PPE Audit")
    uploaded_file = st.file_uploader("Upload construction site photo (JPG/PNG)", type=["jpg", "jpeg", "png"], key="ppe_upload")
    if uploaded_file:
        image_bytes = uploaded_file.read()
        st.image(image_bytes, caption="Uploaded Photo", use_container_width=True)
        model = init_gemini(api_key)
        if model:
            prompt = (
                "You are a construction safety inspector. Analyse the image for personal protective equipment (PPE) compliance. "
                "Identify helmets, high-visibility vests, steel-toe boots, safety harnesses and any violations according to OSHA and IS 456 standards. "
                "Return ONLY a raw JSON object with the following keys: "
                "safety_score (integer 0-100), overall_status ('Safe' or 'Unsafe'), "
                "ppe_detection (list of strings), and hazards (list of objects with keys: name, severity [Low/Medium/High/Critical], corrective_remedy)."
            )
            response = gemini_vision_call(model, prompt, image_bytes)
            if response:
                try:
                    report = clean_json_response(response)
                except Exception:
                    st.error("Failed to parse Gemini response as JSON. Showing raw output.")
                    st.text(response)
                    report = None
                if report:
                    col1, col2 = st.columns(2)
                    col1.metric("Safety Score", f"{report.get('safety_score', 'N/A')}/100")
                    col2.metric("Overall Status", report.get('overall_status', 'N/A'))
                    st.subheader("PPE Detection Checklist")
                    for item in report.get('ppe_detection', []):
                        st.success(f"✅ {item}")
                    st.subheader("Identified Site Hazards")
                    hazards = report.get('hazards', [])
                    if hazards:
                        for h in hazards:
                            st.markdown(f"- **{h.get('name', '')}** – Severity: `{h.get('severity', '')}` – Remedy: {h.get('corrective_remedy', '')}")
                    else:
                        st.info("No hazards identified.")
                    download_json(report, filename="safety_audit_report.json")
        else:
            st.info("Demo mode – generating a static example report.")
            example = {
                "safety_score": 82,
                "overall_status": "Safe",
                "ppe_detection": ["Helmet", "High‑vis vest", "Steel‑toe boots"],
                "hazards": [{"name": "Unsecured scaffolding", "severity": "High", "corrective_remedy": "Install guardrails and tie‑offs"}]
            }
            st.json(example)
            download_json(example, filename="safety_audit_demo.json")

# ---- Tab 2: Crack Diagnostics & Structural Integrity ----
with tab2:
    st.header("🔍 Crack Diagnostics & Structural Integrity")
    uploaded_file_2 = st.file_uploader("Upload concrete or wall surface image (JPG/PNG)", type=["jpg", "jpeg", "png"], key="crack_upload")
    if uploaded_file_2:
        image_bytes = uploaded_file_2.read()
        st.image(image_bytes, caption="Uploaded Image", use_container_width=True)
        model = init_gemini(api_key)
        if model:
            prompt = (
                "You are a structural engineer. Analyse the image for concrete cracks or defects. "
                "Classify the defect type (Hairline, Settlement, Structural Shear, Thermal Expansion, Spalling). "
                "Estimate the crack width in millimetres, suggest possible root causes, recommend repair methods "
                "(e.g., epoxy injection, structural re-grouting) and indicate urgency (Low/Medium/High/Critical). "
                "Return ONLY a raw JSON object with keys: defect_type, crack_width_mm, root_causes (list), recommended_repairs (list), urgency."
            )
            response = gemini_vision_call(model, prompt, image_bytes)
            if response:
                try:
                    report = clean_json_response(response)
                except Exception:
                    st.error("Failed to parse Gemini response as JSON.")
                    st.text(response)
                    report = None
                if report:
                    st.subheader("Diagnostic Report")
                    st.json(report)
                    download_json(report, filename="crack_diagnostics_report.json")
        else:
            st.info("Demo mode – static example report.")
            example = {
                "defect_type": "Hairline",
                "crack_width_mm": 0.8,
                "root_causes": ["Drying shrinkage"],
                "recommended_repairs": ["Epoxy injection"],
                "urgency": "Low"
            }
            st.json(example)
            download_json(example, filename="crack_diagnostics_demo.json")

# ---- Tab 3: Planning & Real‑Estate Valuation ----
with tab3:
    st.header("🧩 Planning & Real‑Estate Valuation")
    structure_type = st.selectbox("Structure Type", ["Residential", "Commercial", "Industrial", "Infrastructure"])
    built_up_sqft = st.number_input("Built‑up Area (sqft)", min_value=100, max_value=1000000, value=2500, step=100)
    location_tier = st.selectbox("Location Tier (Indian cities)", ["Tier 1", "Tier 2", "Tier 3"])
    completion_pct = st.slider("Completion Percentage", 0, 100, 35, 5)

    cost_per_sqft = {"Tier 1": 1800, "Tier 2": 1300, "Tier 3": 950}
    material_factor = {"Residential": 1.0, "Commercial": 1.25, "Industrial": 1.4, "Infrastructure": 1.6}
    total_budget = built_up_sqft * cost_per_sqft[location_tier] * material_factor[structure_type]
    incurred_capex = total_budget * (completion_pct / 100)
    valuation_multiplier = {"Tier 1": 1.35, "Tier 2": 1.15, "Tier 3": 1.05}
    market_valuation = total_budget * valuation_multiplier[location_tier]

    steel_req = built_up_sqft * 4.5
    cement_req = built_up_sqft * 0.045

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Project Budget", f"₹ {total_budget/1e5:,.2f} Lakhs")
    col2.metric("Capex Incurred", f"₹ {incurred_capex/1e5:,.2f} Lakhs")
    col3.metric("Market Valuation", f"₹ {market_valuation/1e5:,.2f} Lakhs")

    st.subheader("Material Requirements")
    st.write(f"**Steel:** {steel_req:,.0f} kg | **Cement:** {cement_req:,.2f} metric tonnes")

    st.subheader("Milestone Progress")
    st.progress(completion_pct / 100)

    st.subheader("Conceptual 3D Rendering (Pollinations AI)")
    if st.button("Generate 3D Render"):
        render_prompt = f"Modern {structure_type.lower()} building architecture, 3d isometric construction render, photorealistic, 8k"
        pollinations_url = f"https://image.pollinations.ai/prompt/{render_prompt.replace(' ', '%20')}"
        st.image(pollinations_url, caption=f"Conceptual 3D Rendering ({structure_type})", use_container_width=True)

# ---- Tab 4: Daily Site Assistant & Weather‑Aware Advisory ----
with tab4:
    st.header("🤖 Daily Site Assistant & Weather‑Aware Advisory")
    weather = st.selectbox("Current Weather Condition", ["Normal", "High Wind", "Heavy Rain", "Extreme Heat"])
    alerts = {
        "Normal": "✅ All operations can continue as scheduled. Maintain standard IS 456 curing protocols.",
        "High Wind": "⚠️ ALERT: Suspend tower crane operations (>32 km/h gusts) and secure loose formwork/scaffolding.",
        "Heavy Rain": "🌧️ ALERT: Pause exposed concrete pouring, cover fresh slabs, and dewater excavations.",
        "Extreme Heat": "🌡️ ALERT: Apply ponding/wet gunny curing immediately to prevent plastic shrinkage cracking; enforce worker hydration breaks.",
    }
    st.info(alerts.get(weather, ""))

    st.subheader("Construction Engineering Assistant")
    if "assistant_history" not in st.session_state:
        st.session_state.assistant_history = []

    for turn in st.session_state.assistant_history:
        st.chat_message(turn["role"]).write(turn["content"])

    user_msg = st.chat_input("Ask a question about construction engineering…")
    if user_msg:
        st.session_state.assistant_history.append({"role": "user", "content": user_msg})
        st.chat_message("user").write(user_msg)
        with st.spinner("Thinking…"):
            model = init_gemini(api_key)
            if model:
                convo = f"You are a construction engineering assistant. Current site weather: {weather}. Answer concisely.\n"
                for turn in st.session_state.assistant_history:
                    role = "User" if turn["role"] == "user" else "Assistant"
                    convo += f"{role}: {turn['content']}\n"
                try:
                    resp_obj = model.generate_content(convo)
                    response = getattr(resp_obj, "text", None) or "Error: Empty response from model."
                except Exception as e:
                    st.error(f"Gemini assistant request failed: {e}")
                    response = "Demo fallback: Follow IS 456:2000 guidelines and ensure proper PPE at all times."
            else:
                response = f"[Demo Mode - Weather: {weather}] Ensure IS 456 curing compliance and verify all workers wear helmets and harnesses."
            st.session_state.assistant_history.append({"role": "assistant", "content": response})
            st.chat_message("assistant").write(response)

st.caption("© 2026 Multimodal Construction Intelligence Platform – Built with Streamlit and Google Gemini")