import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# =========================
# matplotlib (Cloud 안전 설정)
# =========================
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.unicode_minus"] = False

st.set_page_config(
    page_title="탐색 알고리즘 게임",
    layout="wide"
)

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
    "서울":0,
    "홍천":50,
    "천안":100,
    "음성":100,
    "제천":110,
    "안동":120,
    "대전":150,
    "상주":200,
    "의성":220,
    "대구":240,
    "울산":340,
    "부산":999
}

# =========================
# 게임 초기화
# =========================
def reset_game():
    st.session_state.current = "부산"
    st.session_state.cost = 0
    st.session_state.score = 0
    st.session_state.path = ["부산"]
    st.session_state.game_started = False
    st.session_state.popup = ""

# =========================
# 세션 초기화
# =========================
if "current" not in st.session_state:
    reset_game()

if "popup" not in st.session_state:
    st.session_state.popup = ""

# =========================
# UI
# =========================
st.title("🚗 탐색 알고리즘 게임 (Greedy vs A*)")

algorithm = st.radio(
    "탐색 알고리즘 선택",
    ["최상 우선 탐색", "A* 탐색"],
    horizontal=True
)

# =========================
# 시작 화면
# =========================
if not st.session_state.game_started:

    if algorithm == "최상 우선 탐색":
        st.markdown("""
        <div style='text-align:center'>
        <h2>최상 우선 탐색 (Greedy)</h2>
        <p>h(n)만 보고 가장 가까운 노드 선택</p>
        <h3>시작하시겠습니까?</h3>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown("""
        <div style='text-align:center'>
        <h2>A* 탐색</h2>
        <p>f(n)=g(n)+h(n)</p>
        <h3>시작하시겠습니까?</h3>
        </div>
        """, unsafe_allow_html=True)

    if st.button("시작하기"):
        st.session_state.game_started = True
        st.rerun()

    st.stop()

# =========================
# 팝업
# =========================
if st.session_state.popup:

    st.error(st.session_state.popup)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("확인"):
            st.session_state.popup = ""
            st.rerun()

    with col2:
        if st.button("🔄 다시 시작"):
            reset_game()
            st.rerun()

# =========================
# 현재 상태
# =========================
current = st.session_state.current

col_graph, col_info = st.columns([3, 1])

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
# 정답 선택
# =========================
if current != "서울":
    if algorithm == "최상 우선 탐색":
        correct_city = min(candidates, key=lambda x: x["h"])["도시"]
    else:
        correct_city = min(candidates, key=lambda x: x["f"])["도시"]

# =========================
# 그래프 생성
# =========================
G = nx.Graph()

for city in graph:
    for neighbor, cost in graph[city].items():
        G.add_edge(city, neighbor, weight=cost)

pos = {
    "서울": (0,10),
    "홍천": (2,9),
    "천안": (0,7),
    "음성": (2,7),
    "제천": (4,8),
    "안동": (6,7),
    "상주": (4,5),
    "의성": (6,5),
    "대전": (1,3),
    "대구": (4,2),
    "울산": (7,1),
    "부산": (6,-1)
}

colors = []
for node in G.nodes():
    if node == current:
        colors.append("green")
    elif node == "서울":
        colors.append("red")
    elif node in st.session_state.path:
        colors.append("skyblue")
    else:
        colors.append("orange")

fig, ax = plt.subplots(figsize=(8, 8))

nx.draw(
    G,
    pos,
    with_labels=True,
    node_color=colors,
    node_size=2500,
    font_size=11,
    font_weight="bold",
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

    st.metric("현재 위치", current)
    st.metric("누적 비용", st.session_state.cost)
    st.metric("점수", st.session_state.score)

    st.write("### 이동 경로")

    # ✔ TypeError 완전 방지
    st.write(" → ".join([str(x) for x in st.session_state.path]))

    if current != "서울":

        st.write("### 후보 노드")

        if algorithm == "최상 우선 탐색":
            st.dataframe(
                pd.DataFrame([
                    {"도시": x["도시"], "h(n)": x["h"]}
                    for x in candidates
                ]),
                hide_index=True
            )
        else:
            st.dataframe(
                pd.DataFrame([
                    {
                        "도시": x["도시"],
                        "g(n)": x["g"],
                        "h(n)": x["h"],
                        "f(n)": x["f"]
                    }
                    for x in candidates
                ]),
                hide_index=True
            )

        st.write("### 이동 선택")

        for city in graph[current]:

            if st.button(city, use_container_width=True):

                if city == correct_city:

                    st.session_state.current = city
                    st.session_state.path.append(city)
                    st.session_state.cost += graph[current][city]
                    st.session_state.score += 10

                    st.rerun()

                else:

                    st.session_state.popup = f"{algorithm}에서는 '{correct_city}' 선택이 정답입니다."
                    st.rerun()

# =========================
# 도착
# =========================
if current == "서울":

    st.success("🎉 목표 도착!")
    st.balloons()

    st.write(f"총 비용: {st.session_state.cost}")
    st.write(f"점수: {st.session_state.score}")
    st.write(" → ".join([str(x) for x in st.session_state.path]))

    if st.button("다시 시작"):
        reset_game()
        st.rerun()
