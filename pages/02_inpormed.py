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
# 🔥 세로형 레이아웃 (핵심 수정)
# =========================
pos = {
    "서울": (0,12),
    "홍천": (0,10),
    "천안": (-2,8),
    "음성": (2,8),
    "제천": (-3,6),
    "안동": (3,6),
    "대전": (-2,4),
    "상주": (2,4),
    "대구": (2,2),
    "울산": (4,1),
    "의성": (1,5),
    "부산": (0,0)
}

# =========================
# 상태
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

st.title("🚗 탐색 알고리즘 게임 (Greedy vs A*)")

algo = st.radio("알고리즘", ["최상 우선 탐색", "A* 탐색"], horizontal=True)

if not st.session_state.started:
    if st.button("시작하기"):
        st.session_state.started = True
        st.rerun()
    st.stop()

current = st.session_state.current

# =========================
# 후보 + 평가 (Greedy = h / A* = f)
# =========================
candidates = []

if current != "서울":
    for nxt, dist in graph[current].items():

        g = st.session_state.cost + dist
        hh = h[nxt]
        f = g + hh

        candidates.append({
            "도시": nxt,
            "g": g,
            "h": hh,
            "f": f
        })

    # 🔥 핵심 수정: Greedy는 h만 사용
    if algo == "최상 우선 탐색":
        correct = min(candidates, key=lambda x: x["h"])["도시"]
    else:
        correct = min(candidates, key=lambda x: x["f"])["도시"]

# =========================
# 그래프
# =========================
def draw():

    edge_x, edge_y, edge_text = [], [], []

    for a in graph:
        for b, w in graph[a].items():
            x0, y0 = pos[a]
            x1, y1 = pos[b]

            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]

            edge_text.append(((x0+x1)/2, (y0+y1)/2, str(w)))

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
        node_x.append(x)
        node_y.append(y)

        # 🔥 노드 값 표시
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
        x=[t[0] for t in edge_text],
        y=[t[1] for t in edge_text],
        mode="text",
        text=[t[2] for t in edge_text],
        textfont=dict(size=12),
        hoverinfo="none"
    )

    fig = go.Figure([edge_trace, weight_trace, node_trace])

    fig.update_layout(
        height=800,   # 🔥 세로 강조
        margin=dict(l=10, r=10, t=10, b=10)
    )

    return fig

# =========================
# 출력
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

        # 🔥 Greedy일 때 h 중심 표시
        if algo == "최상 우선 탐색":
            st.write("### 후보 (h 기준)")
            st.dataframe(
                pd.DataFrame([{"도시":c["도시"], "h(n)":c["h"]} for c in candidates]),
                hide_index=True
            )
        else:
            st.write("### 후보 (f 기준)")
            st.dataframe(pd.DataFrame(candidates), hide_index=True)

        for nxt in graph[current]:

            if st.button(nxt, use_container_width=True):

                if nxt == correct:
                    st.session_state.current = nxt
                    st.session_state.path.append(nxt)
                    st.session_state.cost += graph[current][nxt]
                    st.session_state.score += 10
                    st.rerun()
                else:
                    st.session_state.popup = f"오답! 정답: {correct}"
                    st.rerun()

if st.session_state.popup:
    st.error(st.session_state.popup)

    if st.button("확인"):
        st.session_state.popup = ""

if current == "서울":
    st.success("도착!")
    st.write("총 비용:", st.session_state.cost)
    st.write("점수:", st.session_state.score)

    if st.button("다시 시작"):
        reset()
        st.rerun()
