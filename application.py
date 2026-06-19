import streamlit as st
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt

# =====================================================

# PAGE SETTINGS

# =====================================================

st.set_page_config(
page_title="천식 맞춤형 흡입기 추천 시스템",
page_icon="🫁",
layout="wide"
)

# =====================================================

# CUSTOM CSS

# =====================================================

st.markdown("""

<style>

.stApp{
    background-color:#f8fafc;
}

.main-title{
    font-size:42px;
    font-weight:800;
    color:#15803d;
}

.sub-title{
    font-size:18px;
    color:#64748b;
    margin-bottom:25px;
}

[data-testid="stSidebar"]{
    background-color:white;
    border-right:2px solid #dcfce7;
}

div[data-testid="metric-container"]{
    background:white;
    border-radius:18px;
    border:2px solid #dcfce7;
    padding:15px;
    box-shadow:0 3px 10px rgba(0,0,0,0.05);
}

.recommend-card{
    background:white;
    padding:20px;
    border-radius:20px;
    border-left:8px solid #22C55E;
    margin-bottom:15px;
    box-shadow:0 3px 10px rgba(0,0,0,0.05);
}

.result-box{
    background:white;
    padding:20px;
    border-radius:20px;
    box-shadow:0 3px 10px rgba(0,0,0,0.05);
}

</style>

""", unsafe_allow_html=True)

# =====================================================

# TITLE

# =====================================================

st.markdown("""

<div class='main-title'>
🫁 천식 맞춤형 흡입기 추천 시스템
</div>

<div class='sub-title'>
천식 진행 정도를 분석하고,
수학적 모델을 이용하여
가장 적합한 흡입기를 추천합니다.
</div>
""", unsafe_allow_html=True)

st.info(
"""
본 시스템은 탐구 과정에서 구축한 수학적 모델을 기반으로 제작되었습니다.

• 천식 진행도 평가
• 기도 재형성 및 점액 증가 예측
• 최적 입자 크기 계산
• 흡입기 적합도 비교
• 개인 맞춤형 흡입기 추천
"""
)

# =====================================================

# DATABASE

# =====================================================

inhalers = [

{
"name":"Ventolin Evohaler",
"type":"MDI",
"mmad":2.75,
"drug":"Salbutamol"
},

{
"name":"QVAR RediHaler",
"type":"MDI",
"mmad":1.10,
"drug":"Beclomethasone"
},

{
"name":"Symbicort Turbuhaler",
"type":"DPI",
"mmad":2.40,
"drug":"Budesonide + Formoterol"
},

{
"name":"Seretide Diskus",
"type":"DPI",
"mmad":3.75,
"drug":"Fluticasone + Salmeterol"
},

{
"name":"Spiriva Respimat",
"type":"SMI",
"mmad":3.10,
"drug":"Tiotropium"
},

{
"name":"Combivent Respimat",
"type":"SMI",
"mmad":3.00,
"drug":"Ipratropium + Salbutamol"
}

]

# =====================================================

# SIDEBAR

# =====================================================

st.sidebar.header("📋 증상 평가")

q1 = st.sidebar.slider(
"낮 동안 기침 또는 천명음 빈도",
0,4,2
)

q2 = st.sidebar.slider(
"밤에 기침으로 잠에서 깨는 빈도",
0,4,2
)

q3 = st.sidebar.slider(
"운동 시 호흡곤란 정도",
0,4,2
)

q4 = st.sidebar.slider(
"응급 흡입기 사용 빈도",
0,4,2
)

q5 = st.sidebar.slider(
"최근 천식 악화 경험",
0,4,2
)

pif = st.sidebar.radio(
"흡입 능력",
[
"약함",
"보통",
"좋음"
]
)

run = st.sidebar.button(
"🔍 결과 분석하기",
use_container_width=True
)

# =====================================================

# CALCULATION

# =====================================================

if run:


    score = q1 + q2 + q3 + q4 + q5

t = score / 20 * 10

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

# =====================================================
# 결과 요약
# =====================================================

st.header("📊 분석 결과")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "천식 진행도",
        f"{t:.2f}/10"
    )

with col2:
    st.metric(
        "기도 재형성",
        f"{R:.3f}"
    )

with col3:
    st.metric(
        "점액량",
        f"{M:.3f}"
    )

with col4:
    st.metric(
        "기도 반경",
        f"{r:.3f}"
    )

st.subheader("📈 천식 진행도")

st.progress(
    min(t/10,1.0)
)

st.success(
    f"예측 최적 입자 크기 : {xopt:.3f} μm"
)

# =====================================================
# 추천 알고리즘
# =====================================================

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

        if pif == "약함":
            device_score = 20

        elif pif == "보통":
            device_score = 70

        else:
            device_score = 100

    else:

        if pif == "약함":
            device_score = 100

        elif pif == "보통":
            device_score = 90

        else:
            device_score = 80

    total_score = (
        particle_score * 0.5
        +
        device_score * 0.5
    )

    results.append({

        "흡입기":
        inhaler["name"],

        "종류":
        inhaler["type"],

        "성분":
        inhaler["drug"],

        "MMAD":
        inhaler["mmad"],

        "입자 적합도":
        round(
            particle_score,1
        ),

        "기기 적합도":
        round(
            device_score,1
        ),

        "종합 점수":
        round(
            total_score,1
        )

    })

df = pd.DataFrame(
    results
)

df = df.sort_values(
    "종합 점수",
    ascending=False
)

# =====================================================
# 추천 흡입기
# =====================================================

st.header("🏆 추천 흡입기 TOP 2")

for i in range(2):

    h = df.iloc[i]

    medal = (
        "🥇"
        if i == 0
        else "🥈"
    )

    st.markdown(
        f"""
        <div class='recommend-card'>

        <h3>{medal} 추천 {i+1}순위</h3>

        <b>{h['흡입기']}</b><br><br>

        종류 : {h['종류']}<br>

        성분 : {h['성분']}<br>

        MMAD : {h['MMAD']} μm<br>

        종합 점수 : {h['종합 점수']}점

        </div>
        """,
        unsafe_allow_html=True
    )

# =====================================================
# 전체 비교 표
# =====================================================

st.header("📋 전체 흡입기 비교")

st.dataframe(
    df,
    use_container_width=True
)

# =====================================================
# 그래프
# =====================================================

st.header("📊 흡입기 적합도 비교")

fig, ax = plt.subplots(
    figsize=(10,5)
)

colors = [
    "#22C55E",
    "#84CC16",
    "#A3E635",
    "#FACC15",
    "#EAB308",
    "#65A30D"
]

ax.bar(
    df["흡입기"],
    df["종합 점수"],
    color=colors[:len(df)]
)

ax.set_ylabel(
    "종합 점수"
)

ax.set_title(
    "흡입기 추천 순위"
)

plt.xticks(
    rotation=25,
    ha="right"
)

st.pyplot(fig)

# =====================================================
# 결과 해석
# =====================================================

st.header("🩺 결과 해석")

if t < 3:

    st.success(
        "현재 천식 진행 정도는 비교적 낮은 수준으로 평가되었습니다."
    )

elif t < 7:

    st.warning(
        "현재 천식 진행 정도는 중등도 수준으로 평가되었습니다."
    )

else:

    st.error(
        "현재 천식 진행 정도는 높은 수준으로 평가되었습니다."
    )

best = df.iloc[0]["흡입기"]

st.info(
    f"""
    분석 결과 기도 재형성 정도는 {R:.2f},
    점액량은 정상 대비 약 {M:.2f}배로 예측되었습니다.

    수학적 모델에 의해 계산된 최적 입자 크기는
    약 {xopt:.2f} μm 입니다.

    현재 데이터베이스에 포함된 흡입기 중에서는
    **{best}** 가 가장 높은 적합도를 보였습니다.

    본 추천은 탐구 과정에서 구축한 수학적 모델을
    기반으로 계산된 결과이며,
    실제 의료적 진단이나 처방을 대체하지 않습니다.
    """
)

# =====================================================
# 연구 모델 정보
# =====================================================

with st.expander("📚 사용된 수학적 모델 보기"):

    st.markdown(f"""


### 1. 기도 재형성 모델

R(t)=1/(1+e^(-0.8(t-5)))

현재 값 : **{R:.3f}**

---

### 2. 점액 증가 모델

M(t)=e^(0.12t)

현재 값 : **{M:.3f}**

---

### 3. 기도 반경 모델

r(t)=1−0.25R(t)−0.1ln(M(t))

현재 값 : **{r:.3f}**

---

### 4. 최적 입자 크기 모델

x_opt = 1.05 / √A

현재 값 : **{xopt:.3f} μm**

""")

# =====================================================

# 첫 화면

# =====================================================

else:

st.markdown(
    """
    ## 👈 왼쪽 설문을 입력한 뒤

    **[결과 분석하기]** 버튼을 눌러주세요.

    시스템이 다음 항목을 자동 계산합니다.

    ✅ 천식 진행도

    ✅ 기도 재형성 정도

    ✅ 점액 증가량

    ✅ 최적 입자 크기

    ✅ 가장 적합한 흡입기 추천
    """
)

