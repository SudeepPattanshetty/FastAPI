import os
import requests
import streamlit as st

# ---------- Config ----------
API_BASE = os.getenv("API_URL", "http://localhost:8000").rstrip("/")
API_URL = API_BASE + "/predict"

st.set_page_config(
    page_title="Insurance Premium Predictor",
    page_icon="🛡️",
    layout="centered",
)

# ---------- Styling ----------
CATEGORY_STYLE = {
    "Low":    {"color": "#16a34a", "bg": "#dcfce7", "icon": "🟢", "note": "Lower risk profile"},
    "Medium": {"color": "#d97706", "bg": "#fef3c7", "icon": "🟡", "note": "Moderate risk profile"},
    "High":   {"color": "#dc2626", "bg": "#fee2e2", "icon": "🔴", "note": "Higher risk profile"},
}
DEFAULT_STYLE = {"color": "#2563eb", "bg": "#dbeafe", "icon": "🔵", "note": ""}

st.markdown(
    """
    <style>
    .block-container { padding-top: 2rem; max-width: 760px; }
    .hero {
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
        padding: 1.6rem 1.8rem; border-radius: 16px; color: white;
        margin-bottom: 1.5rem;
    }
    .hero h1 { margin: 0; font-size: 1.8rem; color: white; }
    .hero p  { margin: .3rem 0 0 0; opacity: .9; }
    .result-card {
        border-radius: 16px; padding: 1.5rem; text-align: center;
        margin: 1rem 0 1.2rem 0; border: 2px solid;
    }
    .result-label { font-size: .85rem; text-transform: uppercase;
                    letter-spacing: .08em; opacity: .75; }
    .result-value { font-size: 2.6rem; font-weight: 800; margin: .2rem 0; }
    .result-note  { font-size: .95rem; opacity: .85; }
    .prob-row { margin-bottom: .8rem; }
    .prob-head { display: flex; justify-content: space-between;
                 font-weight: 600; margin-bottom: .25rem; }
    .prob-track { background: rgba(128,128,128,.2); border-radius: 999px;
                  height: 12px; overflow: hidden; }
    .prob-fill { height: 100%; border-radius: 999px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>🛡️ Insurance Premium Predictor</h1>
        <p>Fill in your details to estimate your premium category.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- Input form ----------
with st.form("predict_form"):
    st.subheader("Your details")

    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age", min_value=1, max_value=119, value=30)
        weight = st.number_input("Weight (kg)", min_value=1.0, value=65.0)
        income_lpa = st.number_input("Annual income (LPA)", min_value=0.1, value=10.0)
        smoker = st.selectbox("Are you a smoker?", options=[True, False],
                              format_func=lambda x: "Yes" if x else "No")
    with col2:
        height = st.number_input("Height (m)", min_value=0.5, max_value=2.5, value=1.7)
        city = st.text_input("City", value="Mumbai")
        occupation = st.selectbox(
            "Occupation",
            options=["private_job", "freelancer", "retired",
                     "business_owner", "government_job"],
            format_func=lambda x: x.replace("_", " ").title(),
        )

    submitted = st.form_submit_button("Predict premium category",
                                      use_container_width=True, type="primary")

# ---------- Call API ----------
if submitted:
    payload = {
        "age": age,
        "weight": weight,
        "height": height,
        "income_lpa": income_lpa,
        "smoker": smoker,
        "city": city,
        "occupation": occupation,
    }

    try:
        with st.spinner("Calculating..."):
            response = requests.post(API_URL, json=payload, timeout=30)

        if response.status_code == 200:
            result = response.json()
            data = result.get("response", result)  # works nested or flat

            category = data.get("predicted_category")
            confidence = data.get("confidence")
            probs = data.get("class_probabilities", {})

            if not category:
                st.error(f"Unexpected API response: {result}")
            else:
                style = CATEGORY_STYLE.get(category, DEFAULT_STYLE)

                # Main result card
                st.markdown(
                    f"""
                    <div class="result-card"
                         style="background:{style['bg']}; border-color:{style['color']}; color:{style['color']};">
                        <div class="result-label">Predicted premium category</div>
                        <div class="result-value">{style['icon']} {category}</div>
                        <div class="result-note">{style['note']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Metrics row
                m1, m2 = st.columns(2)
                if confidence is not None:
                    m1.metric("Model confidence", f"{confidence * 100:.1f}%")
                m2.metric("Categories evaluated", len(probs))

                # Probability bars (highest first)
                if probs:
                    st.subheader("Class probabilities")
                    for name, p in sorted(probs.items(), key=lambda kv: kv[1], reverse=True):
                        s = CATEGORY_STYLE.get(name, DEFAULT_STYLE)
                        st.markdown(
                            f"""
                            <div class="prob-row">
                                <div class="prob-head">
                                    <span>{s['icon']} {name}</span>
                                    <span>{p * 100:.1f}%</span>
                                </div>
                                <div class="prob-track">
                                    <div class="prob-fill"
                                         style="width:{p * 100:.1f}%; background:{s['color']};"></div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                with st.expander("View raw API response"):
                    st.json(result)
        else:
            st.error(f"API error {response.status_code}: {response.text}")

    except requests.exceptions.ConnectionError:
        st.error(f"Could not connect to the API at {API_BASE}. "
                 "Check that the backend is running and API_URL is set correctly.")
    except requests.exceptions.Timeout:
        st.error("The API took too long to respond. Please try again.")