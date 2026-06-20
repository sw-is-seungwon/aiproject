import streamlit as st
import pandas as pd
from streamlit_agraph import agraph, Node, Edge, Config

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

    "음성": {
        "서울":100,
        "홍천":80,
        "천안":40,
        "상주":100,
        "의성":200
    },

    "제천": {
        "홍천":60,
        "안동":60
    },

    "안동": {
        "제천":60,
        "의성":50
    },

    "상주": {
        "음성":100,
        "부산":110
    },

    "의성": {
        "음성":200,
        "안동":50,
        "울산":120
    },

    "대전": {
        "천안":50,
        "대구":90
    },

    "대구": {
        "대전":90,
        "부산":60
    },

    "울산": {
        "의성":120,
        "부산":40
    },

    "부산": {
        "상주":110,
        "대구":60,
        "울산":40
    }
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
# 노드 위치
# =========================

positions = {

    "서울": (100,100),

    "홍천": (350,50),

    "천안": (150,300),

    "음성": (320,250),

    "제천": (520,170),

    "안동": (700,300),

    "상주": (520,430),

    "의성": (680,470),

    "대전": (220,550),

    "대구": (550,700),

    "울산": (850,760),

    "부산": (760,900)
}

# =========================
# 세션 상태
# =========================

if "current" not in st.session_state:
    st.session_state.current = "부산"

if "path" not in st.session_state:
    st.session_state.path = ["부산"]

if "cost" not in st.session_state:
    st.session_state.cost = 0

if "score" not in st.session_state:
    st.session_state.score = 0

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
# 현재 상태
# =========================

current = st.session_state.current

col1, col2 = st.columns([3,1])

with col2:

    st.info(f"현재 위치 : {current}")

    st.metric(
        "누적 이동 시간",
        f"{st.session_state.cost}분"
    )

    st.metric(
        "점수",
        st.session_state.score
    )

    st.write("### 이동 경로")

    st.write(
        " → ".join(st.session_state.path)
    )

    if st.button("처음부터 다시"):

        st.session_state.current = "부산"
        st.session_state.path = ["부산"]
        st.session_state.cost = 0
        st.session_state.score = 0

        st.rerun()

# =========================
# 후보 노드 계산
# =========================

candidates = []

if current != "서울":

    for city, distance in graph[current].items():

        g = st.session_state.cost + distance
        h_value = h[city]
        f = g + h_value

        candidates.append({
            "도시": city,
            "g": g,
            "h": h_value,
            "f": f
        })

# =========================
# 후보 노드 표
# =========================

with col2:

    st.write("---")

    if current != "서울":

        st.subheader("후보 노드")

        if algorithm == "최상 우선 탐색":

            df = pd.DataFrame([
                {
                    "도시": x["도시"],
                    "h(n)": x["h"]
                }
                for x in candidates
            ])

        else:

            df = pd.DataFrame([
                {
                    "도시": x["도시"],
                    "g(n)": x["g"],
                    "h(n)": x["h"],
                    "f(n)": x["f"]
                }
                for x in candidates
            ])

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

# =========================
# 정답 계산
# =========================

correct_city = None

if current != "서울":

    if algorithm == "최상 우선 탐색":

        correct_city = min(
            candidates,
            key=lambda x: x["h"]
        )["도시"]

    else:

        correct_city = min(
            candidates,
            key=lambda x: x["f"]
        )["도시"]

# =========================
# 그래프 생성
# =========================

nodes = []

for city in positions:

    x, y = positions[city]

    color = "#F4A261"

    if city == "서울":
        color = "#E63946"

    if city in st.session_state.path:
        color = "#87CEEB"

    if city == current:
        color = "#2ECC71"

    nodes.append(
        Node(
            id=city,
            label=f"{city}\nh={h[city]}",
            x=x,
            y=y,
            size=28,
            color=color
        )
    )

# =========================
# 간선
# =========================

edges = []
added = set()

for city in graph:

    for neighbor, cost in graph[city].items():

        key = tuple(sorted([city, neighbor]))

        if key not in added:

            edges.append(
                Edge(
                    source=city,
                    target=neighbor,
                    label=str(cost)
                )
            )

            added.add(key)

# =========================
# 그래프 출력
# =========================

with col1:

    st.subheader("그래프")

    config = Config(
        width=1000,
        height=950,
        directed=False,
        physics=False,
        nodeHighlightBehavior=True,
        highlightColor="#F7A7A6"
    )

    selected = agraph(
        nodes=nodes,
        edges=edges,
        config=config
    )

# =========================
# 노드 클릭 처리
# =========================

if selected and current != "서울":

    if selected == current:
        st.info("현재 위치입니다.")

    elif selected not in graph[current]:

        st.warning(
            f"{current}에서 {selected}(으)로 이동할 수 없습니다."
        )

    else:

        if selected == correct_city:

            st.success(
                f"정답! {selected} 선택"
            )

            move_cost = graph[current][selected]

            st.session_state.cost += move_cost
            st.session_state.current = selected
            st.session_state.path.append(selected)
            st.session_state.score += 10

            st.rerun()

        else:

            st.error(
                f"오답! {algorithm}은 "
                f"'{correct_city}' 노드를 선택합니다."
            )

# =========================
# 도착
# =========================

if current == "서울":

    st.success("🎉 서울 도착 성공!")

    st.balloons()

    st.write(
        f"총 이동 시간 : {st.session_state.cost}분"
    )

    st.write(
        f"최종 점수 : {st.session_state.score}점"
    )

    st.write(
        "경로 : " +
        " → ".join(st.session_state.path)
    )
