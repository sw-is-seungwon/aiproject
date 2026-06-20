import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="탐색 알고리즘 게임", layout="wide")

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

Y_SCALE = 1.8

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

st.title("🚗 탐색 알고리즘 게임")

algo = st.radio("알고리즘 선택", ["최상 우선 탐색", "A* 탐색"], horizontal=True)

# =========================
# 🔥 시작 화면 (핵심 수정)
# =========================
if not st.session_state.started:

    if algo == "최상 우선 탐색":

        st.markdown("""
        ## 🧠 최상 우선 탐색 (Greedy Best-First Search)

        ### 📌 개념
        현재 노드에서 목표까지 **가장 가까워 보이는 노드(h(n))**를 선택하는 탐색 방법

        ### 📊 평가 함수
        ```
        h(n)
        ```

        ### ⚙️ 의미
        - g(n): 고려하지 않음
        - h(n): 목표까지의 추정 거리만 사용

        👉 즉, "당장 좋아 보이는 방향"으로만 이동

        ---
        """)

    else:

        st.markdown("""
        ## 🧠 A* 탐색 (A-Star Search)

        ### 📌 개념
        현재까지의 비용 + 목표까지의 추정을 함께 고려하는 최적 탐색

        ### 📊 평가 함수
        ```
        f(n) = g(n) + h(n)
        ```

        ### ⚙️ 의미
        - g(n): 시작 → 현재까지 실제 비용
        - h(n): 현재 → 목표 예상 비용

        👉 "현재까지 비용 + 미래 예측"을 동시에 고려

        ---
        """)

    col1, col2, col3 = st.columns([2,1,2])

    with col2:
        if st.button("🚀 시작하기", use_container_width=True):
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
    for nxt, dist in graph[current].items():
        g = st.session_state.cost + dist
        hh = h[nxt]
        f = g + hh

        candidates.append({"도시": nxt, "g": g, "h": hh, "f": f})

    if algo == "최상 우선 탐색":
        correct = min(candidates, key=lambda x: x["h"])["도시"]
    else:
        correct = min(candidates, key=lambda x: x["f"])["도시"]

# =========================
# 그래프
# =========================
def draw():

    edge_x, edge_y, edge_text_x, edge_text_y, edge_text = [], [], [], [], []

    for a in graph:
        for b, w in graph[a].items():

            x0, y0 = pos[a]
            x1, y1 = pos[b]

            y0 *= Y_SCALE
            y1 *= Y_SCALE

            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]

            edge_text_x.append((x0+x1)/2)
            edge_text_y.append((y0+y1)/2)
            edge_text.append(str(w))

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        line=dict(width=2, color="#888"),
        hoverinfo="none"
    )

    node_x, node_y, labels, colors = [], [], [], []

    for n in graph:
        x, y = pos[n]
        y *= Y_SCALE

        node_x.append(x)
        node_y.append(y)

        if algo == "최상 우선 탐색":
            labels.append(f"{n}\nh={h[n]}")
        else:
            g = st.session_state.cost
            labels.append(f"{n}\nf={g + h[n]}")

        if n == current:
            colors.append("green")
        elif n == "서울":
            colors.append("red")
        elif n in st.session_state.path:
            colors.append("skyblue")
        else:
            colors.append("orange")

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=labels,
        textposition="top center",
        marker=dict(size=35, color=colors),
        hoverinfo="text"
    )

    weight_trace = go.Scatter(
        x=edge_text_x,
        y=edge_text_y,
        mode="text",
        text=edge_text,
        textfont=dict(size=12),
        hoverinfo="none"
    )

    return go.Figure([edge_trace, weight_trace, node_trace])

# =========================
# 화면
# =========================
col1, col2 = st.columns([3,1])

with col1:
    st.plotly_chart(draw(), use_container_width=True)

with col2:

    st.metric("현재", current)
    st.metric("비용", st.session_state.cost)
    st.metric("점수", st.session_state.score)

    st.write("### 경로")
    st.write(" → ".join(st.session_state.path))

    if current != "서울":

        st.dataframe(pd.DataFrame(candidates), hide_index=True)

        for nxt in graph[current]:

            if st.button(nxt, use_container_width=True):

                if nxt == correct:
                    st.session_state.current = nxt
                    st
