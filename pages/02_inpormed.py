import streamlit as st
import heapq
import time

st.set_page_config(page_title="탐색 알고리즘 비교", layout="wide")

st.title("🧭 언덕 등반 탐색 vs A* 탐색")

# -----------------------------
# 상태 관리 (핵심 추가)
# -----------------------------
if "result" not in st.session_state:
    st.session_state.result = None

if "run" not in st.session_state:
    st.session_state.run = False


# 지도
grid = [
    [0,0,0,0,0],
    [0,1,1,1,0],
    [0,0,0,1,0],
    [0,1,0,0,0],
    [0,0,0,1,0]
]

ROWS = len(grid)
COLS = len(grid[0])

start = (0,0)
goal = (4,4)

algorithm = st.radio(
    "알고리즘 선택",
    ["언덕 등반 탐색", "A* 탐색"]
)

def heuristic(pos):
    return abs(pos[0]-goal[0]) + abs(pos[1]-goal[1])

def get_neighbors(pos):
    r, c = pos

    directions = [(-1,0),(1,0),(0,-1),(0,1)]
    neighbors = []

    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        if 0 <= nr < ROWS and 0 <= nc < COLS:
            if grid[nr][nc] == 0:
                neighbors.append((nr,nc))
    return neighbors


# -----------------------------
# Hill Climbing
# -----------------------------
def hill_climbing():
    current = start
    path = [current]

    while current != goal:
        neighbors = get_neighbors(current)
        if not neighbors:
            return path, False

        current_h = heuristic(current)
        best_neighbor = min(neighbors, key=heuristic)
        best_h = heuristic(best_neighbor)

        if best_h >= current_h:
            return path, False

        current = best_neighbor
        path.append(current)

    return path, True


# -----------------------------
# A*
# -----------------------------
def a_star():
    pq = []
    heapq.heappush(pq, (heuristic(start), 0, start))

    came_from = {}
    g_score = {start:0}
    visited = []

    while pq:
        f, g, current = heapq.heappop(pq)
        visited.append(current)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path, visited

        for neighbor in get_neighbors(current):
            tentative_g = g + 1

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                f_score = tentative_g + heuristic(neighbor)

                heapq.heappush(pq, (f_score, tentative_g, neighbor))
                came_from[neighbor] = current

    return [], visited


# -----------------------------
# 지도 출력 (폰트 수정 핵심)
# -----------------------------
def draw_map(path=None, current=None):

    html = """
    <table style='
        border-collapse:collapse;
        font-family: Arial, "Noto Sans KR", sans-serif;
        font-size:14px;
    '>
    """

    for r in range(ROWS):
        html += "<tr>"

        for c in range(COLS):

            color = "white"

            if grid[r][c] == 1:
                color = "black"
            if (r,c) == start:
                color = "green"
            if (r,c) == goal:
                color = "red"
            if path and (r,c) in path:
                color = "skyblue"
            if current and (r,c) == current:
                color = "orange"

            html += f"""
            <td style="
                width:45px;
                height:45px;
                border:1px solid gray;
                background:{color};
                text-align:center;
                font-family: Arial, 'Noto Sans KR', sans-serif;
            ">
            </td>
            """

        html += "</tr>"

    html += "</table>"

    st.markdown(html, unsafe_allow_html=True)


# -----------------------------
# 실행 버튼
# -----------------------------
if st.button("탐색 시작"):
    st.session_state.run = True
    st.session_state.result = None

    placeholder = st.empty()

    if algorithm == "언덕 등반 탐색":

        path, success = hill_climbing()

        st.subheader("탐색 과정")

        for node in path:
            with placeholder.container():
                draw_map(path, node)
            time.sleep(0.8)

        st.session_state.result = success
        st.session_state.path = path

        if success:
            st.success("목표 도달 성공!")
        else:
            st.error("지역 최적해에 빠져 실패!")

    else:

        path, visited = a_star()

        st.subheader("탐색 과정")

        current_path = []

        for node in visited:
            current_path.append(node)

            with placeholder.container():
                draw_map(current_path, node)

            time.sleep(0.3)

        st.session_state.result = True
        st.session_state.path = path

        st.success("목표 도달 성공!")
        st.write("최단 경로:")
        st.write(path)


# -----------------------------
# ❗ 다시 해보기 버튼 (핵심 추가)
# -----------------------------
if st.session_state.result is False:
    if st.button("🔄 다시 해보기"):
        st.session_state.result = None
        st.session_state.run = False
        st.rerun()
