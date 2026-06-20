import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

st.set_page_config(
    page_title="탐색 알고리즘 게임",
    layout="wide"
)

# ------------------------
# 그래프 정의
# ------------------------

graph = {

    "서울": {"홍천":50, "천안":100, "음성":100},

    "홍천": {"서울":50, "음성":80, "제천":60},

    "천안": {"서울":100, "음성":40, "대전":50},

    "음성": {"서울":100,
            "홍천":80,
            "천안":40,
            "상주":100,
            "의성":200},

    "제천": {"홍천":60,
            "안동":60},

    "안동": {"제천":60,
            "의성":50},

    "상주": {"음성":100,
            "부산":110},

    "의성": {"음성":200,
            "안동":50,
            "울산":120},

    "대전": {"천안":50,
            "대구":90},

    "대구": {"대전":90,
            "부산":60},

    "울산": {"의성":120,
            "부산":40},

    "부산": {"상주":110,
            "대구":60,
            "울산":40}
}

# ------------------------
# 휴리스틱 값
# ------------------------

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

# ------------------------
# 노드 위치
# ------------------------

positions = {

    "서울": (100,100),

    "홍천": (350,50),

    "천안": (150,300),

    "음성": (300,250),

    "제천": (500,180),

    "안동": (700,300),

    "상주": (500,430),

    "의성": (650,450),

    "대전": (220,520),

    "대구": (580,700),

    "울산": (850,760),

    "부산": (760,900)
}

# ------------------------
# 세션 상태
# ------------------------

if "current" not in st.session_state:
    st.session_state.current = "부산"

if "path" not in st.session_state:
    st.session_state.path = ["부산"]

if "cost" not in st.session_state:
    st.session_state.cost = 0

# ------------------------
# 제목
# ------------------------

st.title("🚗 서울로 가는 길")

col1, col2 = st.columns([3,1])

with col2:

    st.metric(
        "현재 위치",
        st.session_state.current
    )

    st.metric(
        "누적 이동 시간",
        f"{st.session_state.cost}분"
    )

    st.write("### 이동 경로")

    st.write(
        " → ".join(st.session_state.path)
    )

    if st.button("처음부터 다시"):
        st.session_state.current = "부산"
        st.session_state.path = ["부산"]
        st.session_state.cost = 0
        st.rerun()

# ------------------------
# 그래프 생성
# ------------------------

nodes = []

for city in positions:

    x, y = positions[city]

    color = "#f28c28"

    if city == "서울":
        color = "#ff4b4b"

    if city in st.session_state.path:
        color = "#7fd3ff"

    if city == st.session_state.current:
        color = "#00cc66"

    nodes.append(

        Node(
            id=city,
            label=f"{city}\n(h={h[city]})",
            x=x,
            y=y,
            size=30,
            color=color
        )
    )

# ------------------------
# 간선 생성
# ------------------------

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

# ------------------------
# 그래프 표시
# ------------------------

with col1:

    st.subheader("그래프 지도")

    config = Config(
        width=1000,
        height=900,
        directed=False,
        physics=False,
        hierarchical=False,
        nodeHighlightBehavior=True,
        highlightColor="#F7A7A6"
    )

    selected = agraph(
        nodes=nodes,
        edges=edges,
        config=config
    )

# ------------------------
# 이동 처리
# ------------------------

if selected:

    current = st.session_state.current

    if selected == current:
        st.info("현재 위치입니다.")

    elif selected in graph[current]:

        cost = graph[current][selected]

        st.session_state.cost += cost

        st.session_state.current = selected

        st.session_state.path.append(selected)

        st.rerun()

    else:

        st.warning(
            f"{current}에서 {selected}로는 이동할 수 없습니다."
        )

# ------------------------
# 도착
# ------------------------

if st.session_state.current == "서울":

    st.success("🎉 서울 도착!")

    st.balloons()

    st.write(
        f"총 이동 시간 : {st.session_state.cost}분"
    )

    st.write(
        "이동 경로 : " +
        " → ".join(st.session_state.path)
    )
