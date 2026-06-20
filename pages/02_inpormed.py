import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# =========================
# 스타일 (핵심: 귀여운 UI)
# =========================
st.set_page_config(
    page_title="🐻 알고리즘 여행 게임",
    layout="wide"
)

st.markdown("""
<style>
/* 전체 배경 */
.stApp {
    background: linear-gradient(135deg, #fff1f7, #f0f8ff);
}

/* 제목 */
h1, h2, h3 {
    color: #ff6fa9;
    font-family: 'Arial Rounded MT Bold', sans-serif;
}

/* 버튼 */
.stButton>button {
    background: linear-gradient(135deg, #ffb6c1, #ffd1dc);
    color: white;
    border-radius: 15px;
    border: none;
    padding: 0.6em 1em;
    font-size: 16px;
    font-weight: bold;
}

.stButton>button:hover {
    transform: scale(1.05);
    transition: 0.2s;
}

/* 카드 느낌 */
.card {
    background: white;
    padding: 20px;
    border-radius: 20px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.08);
}
</style>
""", unsafe_allow_html=True)

# =========================
# 그래프
# =========================
graph = {
    "서울": {"홍천":50, "천안":100, "음성":100},
    "홍천": {"서울":50, "음성":80, "제천":60},
    "천안": {"서울":100, "음성":40, "대전":50},
    "음성": {"서울":100,"홍천":80,"천안":40,"상주":100,"의성":200},
    "제천": {"홍천":60,"안동":60},
    "안동": {"제천":60,"의성":50},
    "상주": {"음성":100,"부산":110},
    "의성": {"음성":200,"안동":50,"울산":120},
    "대전": {"천안":50,"대구":90},
    "대구": {"대전":90,"부산":60},
    "울산": {"의성":120,"부산":40},
    "부산": {"상주":110,"대구":60,"울산":40}
}

# =========================
# 휴리스틱
# =========================
h = {
    "서울":0,"홍천":50,"천안":100,"음성":100,"제천":110,
    "안동":120,"대전":150,"상주":200,"의성":220,
    "대구":240,"울산":340,"부산":999
}

# =========================
# 초기화
# =========================
def reset():
    st.session_state.current = "부산"
    st.session_state.cost = 0
    st.session_state.score = 0
    st.session_state.path = ["부산"]
    st.session_state.started = False
    st.session_state.popup = ""

if "current" not in st.session_state:
    reset()

# =========================
# 타이틀
# =========================
st.markdown("<h1 style='text-align:center'>🚗 알고리즘 여행 게임 🧭</h1>", unsafe_allow_html=True)

algorithm = st.radio(
    "✨ 어떤 여행 방법으로 갈까요?",
    ["🌿 최상 우선 탐색", "⭐ A* 탐색"],
    horizontal=True
)

# =========================
# 시작 화면
# =========================
if not st.session_state.started:

    st.markdown("""
    <div class="card" style="text-align:center">
        <h2>🐻 여행 준비 완료!</h2>
        <p>서울까지 가장 좋은 길을 찾아보세요!</p>
        <p>하지만 알고리즘이 다르면 길이 달라져요 😲</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚀 여행 시작하기"):
        st.session_state.started = True
        st.rerun()

    st.stop()

# =========================
# 팝업
# =========================
if st.session_state.popup:
    st.error(st.session_state.popup)

    if st.button("다시 도전하기 💪"):
        reset()
        st.rerun()

# =========================
# 상태
# =========================
current = st.session_state.current

col1, col2 = st.columns([3,1])

# =========================
# 후보
# =========================
candidates = []

if current != "서울":
    for city, dist in graph[current].items():
        g = st.session_state.cost + dist
        hh = h[city]
        f = g + hh

        candidates.append({"도시": city, "g": g, "h": hh, "f": f})

# =========================
# 정답
# =========================
if current != "서울":
    if algorithm == "🌿 최상 우선 탐색":
        correct = min(candidates, key=lambda x:x["h"])["도시"]
    else:
        correct = min(candidates, key=lambda x:x["f"])["도시"]

# =========================
# 그래프
# =========================
G = nx.Graph()

for c in graph:
    for n, w in graph[c].items():
        G.add_edge(c, n, weight=w)

pos = nx.spring_layout(G, seed=7)

colors = []
for node in G.nodes():
    if node == current:
        colors.append("#ff69b4")
    elif node == "서울":
        colors.append("#ff4d4d")
    elif node in st.session_state.path:
        colors.append("#87cefa")
    else:
        colors.append("#ffd1dc")

fig, ax = plt.subplots(figsize=(7,6))

nx.draw(
    G,
    pos,
    with_labels=True,
    node_color=colors,
    node_size=2200,
    font_size=10,
    font_weight="bold",
    ax=ax
)

nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, "weight"), ax=ax)

with col1:
    st.pyplot(fig)

# =========================
# 정보 패널
# =========================
with col2:

    st.markdown("### 🧭 현재 상태")
    st.info(f"📍 {current}")
    st.success(f"💰 비용: {st.session_state.cost}")
    st.warning(f"⭐ 점수: {st.session_state.score}")

    st.markdown("### 📍 이동 경로")
    st.write(" → ".join(st.session_state.path))

    if current != "서울":

        st.markdown("### 🌸 다음 선택")

        for city in graph[current]:

            if st.button(f"👉 {city}"):

                if city == correct:

                    st.session_state.current = city
                    st.session_state.path.append(city)
                    st.session_state.cost += graph[current][city]
                    st.session_state.score += 10

                    st.rerun()

                else:

                    st.session_state.popup = f"❌ 여기 아니야! 정답은 {correct}였어요 😭"
                    st.rerun()

# =========================
# 종료
# =========================
if current == "서울":

    st.balloons()

    st.markdown("""
    <div class="card" style="text-align:center">
        <h2>🎉 서울 도착!</h2>
        <p>정말 잘했어요 🐻✨</p>
    </div>
    """, unsafe_allow_html=True)

    st.write(f"총 비용: {st.session_state.cost}")
    st.write(f"점수: {st.session_state.score}")

    if st.button("🔄 다시 여행하기"):
        reset()
        st.rerun()
