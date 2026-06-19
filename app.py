import streamlit as st
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt

# =====================================================
# PAGE SETTINGS
# =====================================================

st.set_page_config(
    page_title="Asthma Inhaler Recommendation System",
    page_icon="🫁",
    layout="wide"
)

# =====================================================
# TITLE
# =====================================================

st.title("🫁 Asthma Progression-Based Inhaler Recommendation System")
st.markdown(
"""
This web application was developed based on a mathematical model
constructed during the research project.

The system:

1. Estimates asthma progression level
2. Predicts airway remodeling and mucus accumulation
3. Calculates optimal aerosol particle size
4. Compares real inhaler MMAD values
5. Recommends the most suitable inhalers
"""
)

# =====================================================
# INHALER DATABASE
# =====================================================

inhalers = [

    {
        "name": "Ventolin Evohaler",
        "type": "MDI",
        "mmad": 2.75,
        "drug": "Salbutamol"
    },

    {
        "name": "QVAR RediHaler",
        "type": "MDI",
        "mmad": 1.10,
        "drug": "Beclomethasone"
    },

    {
        "name": "Symbicort Turbuhaler",
        "type": "DPI",
        "mmad": 2.40,
        "drug": "Budesonide + Formoterol"
    },

    {
        "name": "Seretide Diskus",
        "type": "DPI",
        "mmad": 3.75,
        "drug": "Fluticasone + Salmeterol"
    },

    {
        "name": "Spiriva Respimat",
        "type": "SMI",
        "mmad": 3.10,
        "drug": "Tiotropium"
    },

    {
        "name": "Combivent Respimat",
        "type": "SMI",
        "mmad": 3.00,
        "drug": "Ipratropium + Salbutamol"
    }

]

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.header("Patient Assessment")

q1 = st.sidebar.slider(
    "Daytime cough/wheezing frequency",
    0, 4, 2
)

q2 = st.sidebar.slider(
    "Night-time cough frequency",
    0, 4, 2
)

q3 = st.sidebar.slider(
    "Exercise-induced dyspnea",
    0, 4, 2
)

q4 = st.sidebar.slider(
    "Rescue inhaler use",
    0, 4, 2
)

q5 = st.sidebar.slider(
    "Recent asthma exacerbation",
    0, 4, 2
)

pif = st.sidebar.radio(
    "Inspiratory ability",
    [
        "Weak",
        "Moderate",
        "Strong"
    ]
)

# =====================================================
# CALCULATE BUTTON
# =====================================================

if st.sidebar.button("Calculate Recommendation"):

    # =================================================
    # ASTHMA PROGRESSION
    # =================================================

    score = q1 + q2 + q3 + q4 + q5

    t = score / 20 * 10

    # =================================================
    # RESEARCH MODEL
    # =================================================

    R = 1 / (
        1 + math.exp(
            -0.8 * (t - 5)
        )
    )

    M = math.exp(
        0.12 * t
    )

    r = (
        1
        - 0.25 * R
        - 0.1 * math.log(M)
    )

    A = 1 / r

    xopt = (
        1.05 /
        math.sqrt(A)
    )

    # =================================================
    # DISPLAY MODEL RESULTS
    # =================================================

    st.header("Model Output")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Asthma Progression (t)",
        f"{t:.2f}"
    )

    c2.metric(
        "Airway Remodeling",
        f"{R:.3f}"
    )

    c3.metric(
        "Mucus Level",
        f"{M:.3f}"
    )

    c4.metric(
        "Airway Radius",
        f"{r:.3f}"
    )

    st.success(
        f"Predicted Optimal Particle Size = {xopt:.3f} μm"
    )

    # =================================================
    # RECOMMENDATION ALGORITHM
    # =================================================

    results = []

    for inhaler in inhalers:

        mmad = inhaler["mmad"]

        error = abs(
            mmad - xopt
        )

        relative_error = (
            error / xopt * 100
        )

        particle_score = max(
            0,
            100 - relative_error
        )

        if inhaler["type"] == "MDI":

            device_score = 80

        elif inhaler["type"] == "DPI":

            if pif == "Weak":
                device_score = 20

            elif pif == "Moderate":
                device_score = 70

            else:
                device_score = 100

        else:

            if pif == "Weak":
                device_score = 100

            elif pif == "Moderate":
                device_score = 90

            else:
                device_score = 80

        total_score = (
            particle_score * 0.5
            +
            device_score * 0.5
        )

        results.append({

            "Inhaler":
            inhaler["name"],

            "Type":
            inhaler["type"],

            "Drug":
            inhaler["drug"],

            "MMAD":
            inhaler["mmad"],

            "Particle Score":
            round(
                particle_score, 1
            ),

            "Device Score":
            round(
                device_score, 1
            ),

            "Total Score":
            round(
                total_score, 1
            )

        })

    df = pd.DataFrame(results)

    df = df.sort_values(
        "Total Score",
        ascending=False
    )

    # =================================================
    # TOP 2
    # =================================================

    st.header("Recommended Inhalers")

    st.subheader(
        f"🥇 1st: {df.iloc[0]['Inhaler']}"
    )

    st.write(
        f"Score: {df.iloc[0]['Total Score']}"
    )

    st.subheader(
        f"🥈 2nd: {df.iloc[1]['Inhaler']}"
    )

    st.write(
        f"Score: {df.iloc[1]['Total Score']}"
    )

    # =================================================
    # TABLE
    # =================================================

    st.header("Full Comparison")

    st.dataframe(
        df,
        use_container_width=True
    )

    # =================================================
    # GRAPH
    # =================================================

    st.header("Inhaler Ranking")

    fig, ax = plt.subplots(
        figsize=(8,4)
    )

    ax.bar(
        df["Inhaler"],
        df["Total Score"]
    )

    ax.set_ylabel(
        "Total Score"
    )

    ax.set_title(
        "Inhaler Recommendation Ranking"
    )

    plt.xticks(
        rotation=30,
        ha="right"
    )

    st.pyplot(fig)

    # =================================================
    # INTERPRETATION
    # =================================================

    st.header("Interpretation")

    if t < 3:

        st.info(
            "Mild asthma progression."
        )

    elif t < 7:

        st.warning(
            "Moderate asthma progression."
        )

    else:

        st.error(
            "Advanced asthma progression."
        )

    st.markdown(
    """
    **Note**

    This recommendation is based on the
    mathematical model developed during
    the research project.

    It is intended for educational and
    research purposes only and does not
    replace medical advice.
    """
    )
