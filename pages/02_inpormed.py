import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# =========================
# UI 스타일 (유지)
# =========================
st.set_page_config(page_title="알고리즘 여행 게임", layout="wide")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #fff1f7, #f0f8ff);
}
.stButton>button {
    background: linear-gradient(135deg, #ffb6c1, #ffd1dc);
    color: white;
    border-radius: 15px;
    border: none;
    font-weight: bold;
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
# 상태 초기화
# =========================
def reset():
    st.session_state.current = "부산"
    st.session_state.cost = 0
    st.session_state.score = 0
    st.session_state.path = ["부산"]
    st.session_state.started = False
    st.session_state.selected_eval = None
    st.session_state.eval_detail = None

if "current" not in st.session_state:
    reset()

# =========================
# 제목
# =========================
st.title("🚗 알고리즘 여행 게임 (평가함수 학습 버전)")

algorithm = st.radio(
    "탐색 알고리즘",
    ["🌿 최상 우선 탐색", "⭐ A* 탐색"],
    horizontal=True
)

# =========================
# 시작 화면
# =========================
if not st.session_state.started:

    st.markdown("""
    <div style='text-align:center'>
    <h2>🧭 서울까지 여행하기</h2>
    <p>노드 선택마다 평가함수를 확인할 수 있어요</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚀 시작하기"):
        st.session_state.started = True
        st.rerun()

    st.stop()

# =========================
# 현재 상태
# =========================
current = st.session_state.current

col_graph, col_info = st.columns([3,1])

# =========================
# 후보 생성
# =========================
candidates = []

if current != "서울":
    for city, dist in graph[current].items():

        g = st.session_state.cost + dist
        hh = h[city]
        f = g + hh

        candidates.append({
            "도시": city,
            "g": g,
            "h": hh,
            "f": f
        })

# =========================
# 정답
# =========================
if current != "서울":
    if algorithm == "🌿 최상 우선 탐색":
        correct = min(candidates, key=lambda x: x["h"])["도시"]
    else:
        correct = min(candidates, key=lambda x: x["f"])["도시"]

# =========================
# 그래프 (❗ 라벨 제거 핵심)
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

# ✔ 핵심: labels 제거 → 글자 안 씀
nx.draw(
    G,
    pos,
    with_labels=False,
    node_color=colors,
    node_size=2200,
    ax=ax
)

nx.draw_networkx_edge_labels(
    G,
    pos,
    edge_labels=nx.get_edge_attributes(G, "weight"),
    ax=ax
)

with col_graph:
    st.pyplot(fig)

# =========================
# 정보 패널
# =========================
with col_info:

    st.markdown("### 🧭 현재 위치")
    st.info(current)

    st.markdown("### 📊 평가함수 설명")

    st.write("g(n): 지금까지 비용")
    st.write("h(n): 목표까지 예상 비용")
    st.write("f(n): g(n) + h(n)")

    if current != "서울":

        st.markdown("### 🌸 후보 노드")

        for c in candidates:

            if st.button(f"👉 {c['도시']}"):

                # =========================
                # 평가함수 즉시 출력
                # =========================
                st.session_state.selected_eval = c
                st.session_state.eval_detail = (
                    f"📍 {c['도시']}\n"
                    f"g(n) = {c['g']}\n"
                    f"h(n) = {c['h']}\n"
                    f"f(n) = {c['f']}"
                )

                if c["도시"] == correct:

                    st.session_state.current = c["도시"]
                    st.session_state.path.append(c["도시"])
                    st.session_state.cost += graph[current][c["도시"]]
                    st.session_state.score += 10

                    st.rerun()

                else:
                    st.session_state.popup = f"❌ 정답은 {correct} 입니다"
                    st.rerun()

    # =========================
    # 평가함수 표시 영역 (핵심 추가)
    # =========================
    if st.session_state.eval_detail:
        st.markdown("### 📌 선택한 노드 평가함수")
        st.info(st.session_state.eval_detail)

    st.markdown("### 🛤 이동 경로")
    st.write(" → ".join(st.session_state.path))

# =========================
# 팝업
# =========================
if st.session_state.get("popup"):
    st.error(st.session_state.popup)

    if st.button("다시 도전하기 💪"):
        reset()
        st.rerun()

# =========================
# 도착
# =========================
if current == "서울":

    st.success("🎉 서울 도착!")

    st.balloons()

    st.write("총 비용:", st.session_state.cost)
    st.write("점수:", st.session_state.score)
    st.write("경로:", " → ".join(st.session_state.path))

    if st.button("다시 시작"):
        reset()
        st.rerun()
