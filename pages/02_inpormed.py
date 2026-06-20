import streamlit as st
import pandas as pd
import plotly.graph_objects as go

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
# 위치 (고정 좌표)
# =========================
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

# =========================
# 상태 초기화
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
# UI
# =========================
st.title("🚗 탐색 알고리즘 게임 (Plotly 버전)")

algorithm = st.radio(
    "알고리즘 선택",
    ["최상 우선 탐색", "A* 탐색"],
    horizontal=True
)

# =========================
# 시작 화면
# =========================
if not st.session_state.started:

    st.markdown("### 시작 화면")

    if st.button("시작하기"):
        st.session_state.started = True
        st.rerun()

    st.stop()

# =========================
# 현재 상태
# =========================
current = st.session_state.current

# =========================
# 후보 계산
# =========================
candidates = []

if current != "서울":
    for city, dist in graph[current].items():
        g = st.session_state.cost + dist
        hh = h[city]
        f = g + hh

        candidates.append({"도시": city, "g": g, "h": hh, "f": f})

    if algorithm == "최상 우선 탐색":
        correct_city = min(candidates, key=lambda x: x["h"])["도시"]
    else:
        correct_city = min(candidates, key=lambda x: x["f"])["도시"]

# =========================
# Plotly 그래프 생성
# =========================
def draw_graph():

    edge_x = []
    edge_y = []

    for a in graph:
        for b in graph[a]:
            x0, y0 = pos[a]
            x1, y1 = pos[b]
            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=2, color="#888"),
        hoverinfo="none",
        mode="lines"
    )

    node_x = []
    node_y = []
    text = []
    colors = []

    for node in graph:

        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        text.append(node)

        if node == current:
            colors.append("green")
        elif node == "서울":
            colors.append("red")
        elif node in st.session_state.path:
            colors.append("skyblue")
        else:
            colors.append("orange")

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=text,
        textposition="top center",
        marker=dict(size=35, color=colors),
        hoverinfo="text"
    )

    fig = go.Figure(data=[edge_trace, node_trace])

    fig.update_layout(
        showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10),
        height=600
    )

    return fig

# =========================
# 그래프 출력
# =========================
col1, col2 = st.columns([3, 1])

with col1:
    st.plotly_chart(draw_graph(), use_container_width=True)

# =========================
# 정보 패널
# =========================
with col2:

    st.metric("현재 위치", current)
    st.metric("누적 비용", st.session_state.cost)
    st.metric("점수", st.session_state.score)

    st.write("### 경로")
    st.write(" → ".join(st.session_state.path))

    if current != "서울":

        st.write("### 후보")

        st.dataframe(pd.DataFrame(candidates), hide_index=True)

        st.write("### 이동")

        for city in graph[current]:

            if st.button(city, use_container_width=True):

                if city == correct_city:

                    st.session_state.current = city
                    st.session_state.path.append(city)
                    st.session_state.cost += graph[current][city]
                    st.session_state.score += 10
                    st.rerun()

                else:

                    st.session_state.popup = f"오답! 정답은 {correct_city}"
                    st.rerun()

# =========================
# 팝업
# =========================
if st.session_state.popup:
    st.error(st.session_state.popup)

    if st.button("확인"):
        st.session_state.popup = ""

# =========================
# 종료
# =========================
if current == "서울":
    st.success("🎉 도착!")

    st.write("총 비용:", st.session_state.cost)
    st.write("점수:", st.session_state.score)

    if st.button("다시 시작"):
        reset()
        st.rerun()
