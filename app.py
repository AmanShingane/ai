import streamlit as st
from workflow import process_documents
import os

# Set page configurations
st.set_page_config(
    page_title="AI Building DDR Generator",
    page_icon="🏢",
    layout="wide"
)

# Custom Premium Styling (CSS)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

/* Apply custom font */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* Glassmorphism containers */
.premium-card {
    background: rgba(255, 255, 255, 0.65);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.04);
    border: 1px solid rgba(226, 232, 240, 0.8);
    margin-bottom: 20px;
}

.premium-title {
    font-size: 2.4rem;
    font-weight: 700;
    background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 5px;
}

.premium-subtitle {
    font-size: 1.1rem;
    color: #475569;
    margin-bottom: 25px;
}

/* Severity Tag Styles */
.severity-tag {
    padding: 3px 12px;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
    display: inline-block;
}
.sev-critical { background-color: #FEE2E2; color: #EF4444; border: 1px solid #FCA5A5; }
.sev-high { background-color: #FFEDD5; color: #F97316; border: 1px solid #FED7AA; }
.sev-medium { background-color: #FEF9C3; color: #CA8A04; border: 1px solid #FDE047; }
.sev-low { background-color: #DCFCE7; color: #22C55E; border: 1px solid #86EFAC; }
.sev-unknown { background-color: #F1F5F9; color: #64748B; border: 1px solid #CBD5E1; }

.section-divider {
    height: 3px;
    background: linear-gradient(90deg, #3B82F6 0%, #E2E8F0 100%);
    border-radius: 2px;
    margin: 20px 0;
}

/* Upload area custom styling */
.uploadedFile {
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.markdown("## ⚙️ Report Settings")
    st.markdown("Customize your DDR generation variables.")
    
    model_opt = st.selectbox(
        "AI Reasoning Model",
        options=["llama-3.3-70b-versatile", "llama-3.1-8b-instant"],
        index=0,
        help="Select the model for logic & reasoning synthesis."
    )
    
    temp_slider = st.slider(
        "Synthesis Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.2,
        step=0.1,
        help="Lower values yield consistent facts; higher values increase text variety."
    )
    
    st.markdown("---")
    st.markdown("### 📝 About the Engine")
    st.info(
        "This app synthesizes building inspection details and thermal reports "
        "using a RAG vector index. It matches findings, evaluates root causes, "
        "assesses risk severity, and compiles a ready-to-download PDF report."
    )

# Main Screen Header
st.markdown('<h1 class="premium-title">🏢 Building Diagnostics AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="premium-subtitle">Detailed Diagnostic Report (DDR) Synthesis Engine</p>', unsafe_allow_html=True)

# Upload Section inside premium card
st.markdown('<div class="premium-card">', unsafe_allow_html=True)
st.markdown("### 📥 Document Uploads")

col1, col2 = st.columns(2)

with col1:
    inspection_pdf = st.file_uploader(
        "Upload Inspection Report PDF",
        type=["pdf"],
        help="Select the main physical inspection document."
    )

with col2:
    thermal_pdf = st.file_uploader(
        "Upload Thermal Report PDF",
        type=["pdf"],
        help="Select the thermal imaging and temperature log document."
    )
st.markdown('</div>', unsafe_allow_html=True)

# Action button
st.markdown("<br>", unsafe_allow_html=True)
generate_btn = st.button("🚀 Generate Detailed Diagnostic Report", use_container_width=True)

def get_severity_details(severity):
    sev = str(severity).strip().lower()
    if sev == "critical":
        return "🔴 CRITICAL", "sev-critical"
    elif sev == "high":
        return "🟠 HIGH", "sev-high"
    elif sev == "medium":
        return "🟡 MEDIUM", "sev-medium"
    elif sev == "low":
        return "🟢 LOW", "sev-low"
    return "⚪ UNKNOWN", "sev-unknown"

if generate_btn:
    if not inspection_pdf or not thermal_pdf:
        st.error("⚠️ Please upload both the Inspection Report and Thermal Report PDFs before proceeding.")
        st.stop()

    os.makedirs("temp", exist_ok=True)

    inspection_path = os.path.join("temp", inspection_pdf.name)
    thermal_path = os.path.join("temp", thermal_pdf.name)

    with open(inspection_path, "wb") as f:
        f.write(inspection_pdf.read())

    with open(thermal_path, "wb") as f:
        f.write(thermal_pdf.read())

    progress = st.progress(0)
    status = st.empty()

    try:
        status.info("Phase 1/4: Parsing documents & extracting images...")
        progress.progress(25)

        # The parsing is optimized to skip OCR if native text is available
        status.info("Phase 2/4: Building RAG vector store and index...")
        progress.progress(50)

        status.info("Phase 3/4: Generating diagnostic synthesis via LangChain Groq...")
        progress.progress(75)

        result = process_documents(
            inspection_path,
            thermal_path,
            model=model_opt,
            temperature=temp_slider
        )

        progress.progress(100)
        status.success("🎉 Detailed Diagnostic Report successfully synthesized!")

        # Layout summary dashboard
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown("## 📊 Executive Summary Dashboard")
        
        # Calculate statistics
        total_obs = len(result.get("area_observations", []))
        missing_count = len(result.get("missing_information", []))
        
        severity_ranks = {"critical": 4, "high": 3, "medium": 2, "low": 1, "unknown": 0}
        highest_sev = "unknown"
        highest_rank = 0
        for obs in result.get("area_observations", []):
            sev = str(obs.get("severity", "unknown")).lower().strip()
            rank = severity_ranks.get(sev, 0)
            if rank > highest_rank:
                highest_rank = rank
                highest_sev = sev.upper()

        if highest_sev == "unknown" or highest_rank == 0:
            highest_sev_display = "N/A"
        else:
            highest_sev_display = highest_sev

        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.metric("Total Observations", total_obs, help="Number of distinct architectural/structural findings identified.")
        with m_col2:
            st.metric("Highest Severity Level", highest_sev_display, help="The highest risk category detected across all observations.")
        with m_col3:
            st.metric("Missing Information Fields", missing_count, help="Items marked as missing or ambiguous in the source documents.")

        # Property Issue Summary
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.markdown("### 📝 Property Issue Summary")
        st.write(result["property_issue_summary"])
        st.markdown('</div>', unsafe_allow_html=True)

        # Observations Section
        st.markdown("### 🔍 Area-wise Observations")
        
        for obs in result.get("area_observations", []):
            area = obs.get("area", "Not Specified")
            severity = obs.get("severity", "unknown")
            sev_label, sev_class = get_severity_details(severity)
            
            # Use severity emoji and name in the expander header
            expander_title = f"{sev_label.split()[0]} {area} — Severity: {severity.upper()}"
            
            with st.expander(expander_title):
                st.markdown(f"**Observation:** {obs.get('observation', 'Not Available')}")
                st.markdown(f"**Thermal Finding:** {obs.get('thermal_finding', 'Not Available')}")
                st.markdown(f"**Root Cause:** {obs.get('root_cause', 'Not Available')}")
                st.markdown(f"**Severity Classification:** <span class='severity-tag {sev_class}'>{severity.upper()}</span>", unsafe_allow_html=True)
                st.markdown(f"**Recommendation:** {obs.get('recommendation', 'Not Available')}")

        # Bottom section: Notes & Missing Info
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        bot_col1, bot_col2 = st.columns(2)
        
        with bot_col1:
            st.markdown('<div class="premium-card" style="height: 100%;">', unsafe_allow_html=True)
            st.markdown("### 📋 Additional Notes")
            st.write(result.get("additional_notes", "No additional notes compiled."))
            st.markdown('</div>', unsafe_allow_html=True)
            
        with bot_col2:
            st.markdown('<div class="premium-card" style="height: 100%;">', unsafe_allow_html=True)
            st.markdown("### ⚠️ Missing Information")
            missing_info = result.get("missing_information", [])
            if not missing_info:
                st.write("✅ No missing information identified between the documents.")
            else:
                for item in missing_info:
                    st.write(f"• {item}")
            st.markdown('</div>', unsafe_allow_html=True)

        # Download Report Button
        st.markdown("<br>", unsafe_allow_html=True)
        pdf_path = result.get("pdf_path")
        
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as file:
                st.download_button(
                    label="📄 Download Premium DDR Report (PDF)",
                    data=file,
                    file_name=f"DDR_Report_{inspection_pdf.name.split('.')[0]}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        else:
            st.error("Could not locate the generated PDF report. Please verify report.py logs.")

    except Exception as e:
        st.error(f"An unexpected error occurred during synthesis: {str(e)}")
        import traceback
        st.code(traceback.format_exc())