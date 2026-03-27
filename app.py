
"""
AI Business Copilot — Streamlit UI
Upload panel · Extraction · Comparison · Executive Summary
"""

import streamlit as st
import tempfile
import os
import re
import plotly.graph_objects as go

# ── page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="AI Business Copilot",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── custom CSS ────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');
html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
h1, h2, h3 { font-family: 'IBM Plex Mono', monospace; letter-spacing: -0.5px; }
</style>
""", unsafe_allow_html=True)

# ── load workflow ─────────────────────────────────────────────────────────────

@st.cache_resource
def load_graph():
    from workflow import run_analysis
    return run_analysis

# ── session state ─────────────────────────────────────────────────────────────

if "analyses" not in st.session_state:
    st.session_state.analyses = {}
if "file_order" not in st.session_state:
    st.session_state.file_order = []

# ── helpers ───────────────────────────────────────────────────────────────────

def save_uploaded_file(uploaded_file) -> str:
    suffix = os.path.splitext(uploaded_file.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read())
        return tmp.name


def safe_get(d: dict, *keys, default="N/A"):
    for k in keys:
        if not isinstance(d, dict):
            return default
        d = d.get(k, default)
    return d if d not in (None, "", []) else default


def parse_numeric(val) -> float | None:
    if not val or val == "N/A":
        return None
    cleaned = re.sub(r"[^\d.\-]", "", str(val))
    try:
        return float(cleaned)
    except ValueError:
        return None


def format_revenue(val) -> str:
    """Format raw number in millions into readable string e.g. $716.9B."""
    if val is None or val == "N/A":
        return "N/A"
    try:
        n = float(val)
        if n >= 1_000_000:
            return f"${n/1_000_000:.2f}T"
        elif n >= 1_000:
            return f"${n/1_000:.1f}B"
        else:
            return f"${n:.0f}M"
    except (ValueError, TypeError):
        return str(val)


def sentiment_label(field) -> str:
    """Extract score + label from a sentiment dict. Returns plain string."""
    if not isinstance(field, dict):
        return "N/A"
    label = field.get("label", "N/A")
    score = field.get("score", "")
    return f"{label} ({score}/5)" if score else label


def sentiment_quote(field) -> str:
    """Extract the supporting quote from a sentiment dict."""
    if not isinstance(field, dict):
        return ""
    return field.get("quote", "")


# ── sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 📊 AI Business Copilot")
    st.markdown("*Earnings analysis powered by Claude*")
    st.divider()

    uploaded_files = st.file_uploader(
        "Upload earnings transcripts",
        type=["pdf", "txt"],
        accept_multiple_files=True,
        help="1 file → single-company analysis. 2+ files → comparison view enabled.",
    )

    run_btn = st.button(
        "▶  Run Analysis",
        type="primary",
        disabled=not uploaded_files,
        use_container_width=True,
    )

    if run_btn and uploaded_files:
        run_analysis = load_graph()
        temp_paths = []
        for f in uploaded_files:
            temp_paths.append(save_uploaded_file(f))

        with st.spinner("Running workflow… this may take a minute."):
            try:
                result = run_analysis(temp_paths)
                error = None
            except Exception as e:
                result = None
                error = str(e)

        for p in temp_paths:
            try:
                os.unlink(p)
            except Exception:
                pass

        if error:
            st.error(f"Workflow error: {error}")
        elif result:
            extracted = result.get("extracted_data", [])
            sentiment = result.get("sentiment_data", [])

            for i, f in enumerate(uploaded_files):
                st.session_state.analyses[f.name] = {
                    "extracted":  extracted[i] if i < len(extracted) else {},
                    "sentiment":  sentiment[i]  if i < len(sentiment)  else {},
                    "comparison": result.get("comparison", []),
                    "summary":    result.get("summary", ""),
                }
                if f.name not in st.session_state.file_order:
                    st.session_state.file_order.append(f.name)

            st.success(f"✓ Analysed {len(uploaded_files)} document(s)")

    if st.session_state.analyses:
        st.divider()
        st.markdown("**Loaded documents**")
        for name in st.session_state.file_order:
            st.markdown(f"· {name}")

        if st.button("🗑  Clear all", use_container_width=True):
            st.session_state.analyses = {}
            st.session_state.file_order = []
            st.rerun()

# ── main ──────────────────────────────────────────────────────────────────────

st.markdown("# AI Business Copilot")

if not st.session_state.analyses:
    st.info("Upload one or more earnings transcripts in the sidebar and click **Run Analysis** to begin.")
    st.stop()

tab_extract, tab_compare, tab_summary = st.tabs([
    "📈 Extraction", "⚖️ Comparison", "📄 Executive Summary"
])


# ── TAB 1: Extraction ─────────────────────────────────────────────────────────

with tab_extract:
    st.subheader("Financial Extraction")

    for filename in st.session_state.file_order:
        data = st.session_state.analyses.get(filename, {})
        fin  = data.get("extracted", {})
        sent = data.get("sentiment", {})

        with st.expander(f"**{filename}**", expanded=True):

            # ── top metrics row ──
            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Revenue", format_revenue(safe_get(fin, "revenue")))
            col2.metric(
                "Revenue Growth",
                f"{safe_get(fin, 'revenue_growth')}%"
                if safe_get(fin, "revenue_growth") != "N/A" else "N/A"
            )
            col3.metric("Net Income", format_revenue(safe_get(fin, "net_income")))
            col4.metric(
                "Net Margin",
                f"{round(fin['net_income'] / fin['revenue'] * 100, 1)}%"
                if isinstance(fin.get("net_income"), (int, float))
                and isinstance(fin.get("revenue"), (int, float))
                and fin["revenue"] != 0
                else "N/A"
            )

            st.divider()

            c1, c2 = st.columns(2)

            # ── sentiment — properly unpacked ──
            with c1:
                st.markdown("**Management Sentiment**")
                for label, key in [
                    ("Overall outlook",     "overall_outlook"),
                    ("Growth confidence",   "growth_confidence"),
                    ("Risk acknowledgment", "risk_acknowledgment"),
                ]:
                    field = sent.get(key)
                    st.markdown(f"**{label}:** {sentiment_label(field)}")
                    quote = sentiment_quote(field)
                    if quote:
                        st.caption(f'*"{quote}"*')

            # ── key risks — top 5 only ──
            with c2:
                st.markdown("**Key Risks**")
                risks = fin.get("key_risks", [])
                if isinstance(risks, list) and risks:
                    for r in risks[:5]:
                        st.markdown(f"- {r}")
                    if len(risks) > 5:
                        st.caption(f"+{len(risks) - 5} more risks in raw JSON below")
                else:
                    st.markdown("N/A")

            # ── forward guidance as readable text ──
            st.divider()
            st.markdown("**Forward Guidance**")
            guidance = fin.get("forward_guidance")
            if guidance:
                st.markdown(guidance)
            else:
                st.markdown("N/A")

            with st.expander("Raw extraction JSON"):
                st.json(fin)


# ── TAB 2: Comparison ─────────────────────────────────────────────────────────

with tab_compare:
    st.subheader("Company Comparison")

    names = st.session_state.file_order

    if len(names) < 2:
        st.info("Upload at least **2 documents** to enable comparison.")
    else:
        a_name, b_name = names[0], names[1]
        fin_a = st.session_state.analyses[a_name].get("extracted", {})
        fin_b = st.session_state.analyses[b_name].get("extracted", {})

        # ── Plotly chart: revenue + net income ──
        metric_keys   = ["revenue", "net_income"]
        metric_labels = ["Revenue ($M)", "Net Income ($M)"]

        vals_a = [parse_numeric(safe_get(fin_a, k)) for k in metric_keys]
        vals_b = [parse_numeric(safe_get(fin_b, k)) for k in metric_keys]

        plot_labels = [l for l, a, b in zip(metric_labels, vals_a, vals_b) if a is not None and b is not None]
        plot_a      = [a for a, b in zip(vals_a, vals_b) if a is not None and b is not None]
        plot_b      = [b for a, b in zip(vals_a, vals_b) if a is not None and b is not None]

        if plot_labels:
            fig = go.Figure(data=[
                go.Bar(name=a_name, x=plot_labels, y=plot_a, marker_color="#1a1a1a"),
                go.Bar(name=b_name, x=plot_labels, y=plot_b, marker_color="#888888"),
            ])
            fig.update_layout(
                barmode="group",
                title="Revenue & Net Income ($M)",
                font=dict(family="IBM Plex Sans"),
                plot_bgcolor="white",
                paper_bgcolor="white",
                yaxis=dict(tickformat=",.0f"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
            )
            st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # ── DuPont ratio table — rendered as metrics not raw JSON ──
        comparison_data = st.session_state.analyses[a_name].get("comparison", [])
        if comparison_data:
            comp = comparison_data[0] if isinstance(comparison_data, list) else comparison_data

            if isinstance(comp, dict):
                st.markdown("**Financial Ratio Analysis**")

                # map each ratio key → (display title, formula, value key inside company dict)
                ratio_map = {
                    "profitability":     ("Profitability",     "Net Income / Revenue"),
                    "asset_utilization": ("Asset Utilisation", "Revenue / Assets"),
                    "asset_multiplier":  ("Asset Multiplier",  "Assets / Equity"),
                }

                # extract company name from filename e.g. "costco.pdf" → "costco"
                key_a = os.path.splitext(a_name)[0].lower()
                key_b = os.path.splitext(b_name)[0].lower()

                for ratio_key, (title, formula) in ratio_map.items():
                    section = comp.get(ratio_key)
                    if not isinstance(section, dict):
                        continue

                    val_a      = section.get(key_a)
                    val_b      = section.get(key_b)
                    better     = section.get("better_performer", "")
                    commentary = section.get("commentary", "")

                    st.markdown(f"**{title}** &nbsp; *{formula}*")
                    col1, col2 = st.columns(2)

                    with col1:
                        badge = " ✅" if better == key_a else ""
                        st.metric(
                            f"{a_name}{badge}",
                            round(val_a, 4) if isinstance(val_a, (int, float)) else "N/A"
                        )

                    with col2:
                        badge = " ✅" if better == key_b else ""
                        st.metric(
                            f"{b_name}{badge}",
                            round(val_b, 4) if isinstance(val_b, (int, float)) else "N/A"
                        )

                    if commentary:
                        st.caption(commentary)

                    st.divider()


# ── TAB 3: Executive Summary ──────────────────────────────────────────────────

with tab_summary:
    st.subheader("Executive Summary")

    first_key = st.session_state.file_order[0]
    summary   = st.session_state.analyses[first_key].get("summary", "")

    if summary:
        st.markdown(summary)
        st.divider()
        st.download_button(
            label="⬇  Download Summary (.md)",
            data=summary,
            file_name="executive_summary.md",
            mime="text/markdown",
        )
    else:
        st.warning("No summary generated. Check your workflow output.")