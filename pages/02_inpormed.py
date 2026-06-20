import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

st.set_page_config(
    page_title="탐색 알고리즘 게임",
    layout="wide"
)

# =========================
# 🔥 한글 폰트 설정 (핵심)
# =========================
def set_korean_font():
    font_list = fm.findSystemFonts()

    font_path = None
    for f in font_list:
        if "NanumGothic" in f:
            font_path = f
            break

    if font_path:
        font_prop = fm.FontProperties(fname=font_path)
        plt.rcParams["font.family"] = font_prop.get_name()
    else:
        # fallback
        plt.rcParams["font.family"] = "DejaVu Sans"

    plt.rcParams["axes.unicode_minus"] = False

set_korean_font()

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

if "popup" not in st.session_state:
    st.session_state.popup = ""

# =========================
# UI
# =========================
st.title("🚗 탐색 알고리즘 게임")

algorithm = st.radio(
    "알고리즘 선택",
    ["최상 우선 탐색", "A* 탐색"],
    horizontal=True
)

# =========================
# 시작 화면
# =========================
if not st.session_state.started:

    st.markdown("### 목표: 부산 → 서울 최단 경로 찾기")

    if st.button("시작하기"):
        st.session_state.started = True
        st.rerun()

    st.stop()

# =========================
# 현재 상태
# =========================
current = st.session_state.current

col1, col2 = st.columns([3, 1])

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
        correct = min(candidates, key=lambda x: x["h"])["도시"]
    else:
        correct = min(candidates, key=lambda x: x["f"])["도시"]

# =========================
# 그래프
# =========================
G = nx.Graph()
for c in graph:
    for n, w in graph[c].items():
        G.add_edge(c, n, weight=w)

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

# 🔥 핵심: 한글 노드 그대로 출력
nx.draw(
    G,
    pos,
    with_labels=True,
    labels={n: n for n in G.nodes()},
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

with col1:
    st.pyplot(fig)

# =========================
# 정보 패널
# =========================
with col2:

    st.metric("현재 위치", current)
    st.metric("비용", st.session_state.cost)
    st.metric("점수", st.session_state.score)

    st.write("### 경로")
    st.write(" → ".join(st.session_state.path))

    if current != "서울":

        st.write("### 후보")

        df = pd.DataFrame(candidates)
        st.dataframe(df, hide_index=True)

        st.write("### 이동 선택")

        for city in graph[current]:

            if st.button(city):

                if city == correct:

                    st.session_state.current = city
                    st.session_state.path.append(city)
                    st.session_state.cost += graph[current][city]
                    st.session_state.score += 10
                    st.rerun()

                else:

                    st.session_state.popup = f"정답은 {correct} 입니다."
                    st.rerun()

# =========================
# 도착
# =========================
if current == "서울":
    st.success("도착!")
    st.write(st.session_state.path)

    if st.button("다시 시작"):
        reset()
        st.rerun()
