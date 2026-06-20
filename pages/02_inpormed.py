import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

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
# 세션 상태
# =========================

if "current" not in st.session_state:
    st.session_state.current = "부산"

if "cost" not in st.session_state:
    st.session_state.cost = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "path" not in st.session_state:
    st.session_state.path = ["부산"]

if "game_started" not in st.session_state:
    st.session_state.game_started = False

if "popup" not in st.session_state:
    st.session_state.popup = ""

# =========================
# 제목
# =========================

st.title("🚗 탐색 알고리즘 게임")

algorithm = st.radio(
    "탐색 알고리즘 선택",
    ["최상 우선 탐색", "A* 탐색"],
    horizontal=True
)

# =========================
# 시작 화면
# =========================

if not st.session_state.game_started:

    st.markdown("<br><br>", unsafe_allow_html=True)

    if algorithm == "최상 우선 탐색":

        st.markdown(
        """
        <div style='text-align:center'>
        <h1>최상 우선 탐색</h1>
        <h2>평가 함수 : h(n)</h2>
        <p>현재 위치에서 목표까지의 예상 거리만 고려합니다.</p>
        <p>h(n)이 가장 작은 노드를 선택합니다.</p>
        <h3>최단 거리를 찾아보시겠습니까?</h3>
        </div>
        """,
        unsafe_allow_html=True
        )

    else:

        st.markdown(
        """
        <div style='text-align:center'>
        <h1>A* 탐색</h1>
        <h2>평가 함수 : f(n)=g(n)+h(n)</h2>
        <p>g(n): 지금까지 이동 거리</p>
        <p>h(n): 목표까지 예상 거리</p>
        <p>f(n)이 가장 작은 노드를 선택합니다.</p>
        <h3>최단 거리를 찾아보시겠습니까?</h3>
        </div>
        """,
        unsafe_allow_html=True
        )

    col1,col2,col3 = st.columns([2,1,2])

    with col2:
        if st.button("시작하기", use_container_width=True):
            st.session_state.game_started = True
            st.rerun()

    st.stop()

# =========================
# 팝업
# =========================

if st.session_state.popup:

    st.markdown(
    f"""
    <div style="
    position:fixed;
    top:50%;
    left:50%;
    transform:translate(-50%,-50%);
    background:white;
    border:3px solid red;
    border-radius:15px;
    padding:30px;
    z-index:9999;
    text-align:center;
    width:500px;
    box-shadow:0 0 30px rgba(0,0,0,0.4);
    ">
    <h2>❌ 오답</h2>
    <p>{st.session_state.popup}</p>
    </div>
    """,
    unsafe_allow_html=True
    )

    if st.button("확인"):
        st.session_state.popup = ""
        st.rerun()

# =========================
# 현재 상태
# =========================

current = st.session_state.current

col_graph, col_info = st.columns([3,1])

# =========================
# 후보 계산
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

    if algorithm == "최상 우선 탐색":
        correct_city = min(candidates, key=lambda x:x["h"])["도시"]
    else:
        correct_city = min(candidates, key=lambda x:x["f"])["도시"]

# =========================
# 그래프 그리기
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

fig, ax = plt.subplots(figsize=(8,8))

nx.draw(
    G,
    pos,
    with_labels=True,
    node_color=colors,
    node_size=2500,
    font_size=10,
    ax=ax
)

edge_labels = nx.get_edge_attributes(G, "weight")

nx.draw_networkx_edge_labels(
    G,
    pos,
    edge_labels=edge_labels,
    ax=ax
)

with col_graph:
    st.pyplot(fig)

# =========================
# 우측 정보
# =========================

with col_info:

    st.metric("현재 위치", current)
    st.metric("누적 비용", st.session_state.cost)
    st.metric("점수", st.session_state.score)

    st.write("### 이동 경로")
    st.write(" → ".join(st.session_state.path))

    if current != "서울":

        st.write("### 후보 노드")

        if algorithm == "최상 우선 탐색":

            st.dataframe(
                pd.DataFrame([
                    {"도시":x["도시"],"h(n)":x["h"]}
                    for x in candidates
                ]),
                hide_index=True
            )

        else:

            st.dataframe(
                pd.DataFrame([
                    {
                        "도시":x["도시"],
                        "g(n)":x["g"],
                        "h(n)":x["h"],
                        "f(n)":x["f"]
                    }
                    for x in candidates
                ]),
                hide_index=True
            )

        st.write("### 노드 선택")

        for city in graph[current]:

            if st.button(city, use_container_width=True):

                if city == correct_city:

                    st.session_state.current = city
                    st.session_state.path.append(city)
                    st.session_state.cost += graph[current][city]
                    st.session_state.score += 10

                    st.rerun()

                else:

                    st.session_state.popup = (
                        f"{algorithm}에서는 "
                        f"'{correct_city}' 노드를 선택해야 합니다."
                    )

                    st.rerun()

# =========================
# 도착
# =========================

if current == "서울":

    st.success("🎉 서울 도착!")

    st.balloons()

    st.write(f"총 이동 비용 : {st.session_state.cost}")
    st.write(f"최종 점수 : {st.session_state.score}")
    st.write(" → ".join(st.session_state.path))

    if st.button("다시 시작"):

        st.session_state.current = "부산"
        st.session_state.cost = 0
        st.session_state.score = 0
        st.session_state.path = ["부산"]
        st.session_state.game_started = False

        st.rerun()
