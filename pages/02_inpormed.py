import streamlit as st
import heapq
import time

st.set_page_config(
    page_title="언덕 등반 탐색 vs A* 탐색",
    layout="centered"
)

st.title("🧭 언덕 등반 탐색 vs A* 탐색")

# ------------------
# 지도 설정
# ------------------
grid = [
    [0,0,0,0,0],
    [0,1,1,1,0],
    [0,0,0,1,0],
    [0,1,0,0,0],
    [0,0,0,1,0]
]

ROWS = len(grid)
COLS = len(grid[0])

start = (0, 0)
goal = (4, 4)

algorithm = st.radio(
    "탐색 알고리즘 선택",
    ["언덕 등반 탐색", "A* 탐색"]
)

# ------------------
# 휴리스틱 함수
# ------------------
def heuristic(pos):
    return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

# ------------------
# 인접 노드 찾기
# ------------------
def get_neighbors(pos):

    r, c = pos

    directions = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1)
    ]

    neighbors = []

    for dr, dc in directions:

        nr = r + dr
        nc = c + dc

        if 0 <= nr < ROWS and 0 <= nc < COLS:
            if grid[nr][nc] == 0:
                neighbors.append((nr, nc))

    return neighbors

# ------------------
# 언덕 등반 탐색
# ------------------
def hill_climbing():

    current = start

    path = [current]

    while current != goal:

        neighbors = get_neighbors(current)

        if not neighbors:
            return path, False

        current_h = heuristic(current)

        best_neighbor = min(
            neighbors,
            key=heuristic
        )

        best_h = heuristic(best_neighbor)

        if best_h >= current_h:
            return path, False

        current = best_neighbor
        path.append(current)

    return path, True

# ------------------
# A* 탐색
# ------------------
def a_star():

    pq = []

    heapq.heappush(
        pq,
        (heuristic(start), 0, start)
    )

    came_from = {}
    g_score = {start: 0}

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

            if (
                neighbor not in g_score
                or tentative_g < g_score[neighbor]
            ):

                g_score[neighbor] = tentative_g

                f_score = tentative_g + heuristic(neighbor)

                heapq.heappush(
                    pq,
                    (f_score,
                     tentative_g,
                     neighbor)
                )

                came_from[neighbor] = current

    return [], visited

# ------------------
# 지도 출력
# ------------------
def draw_map(path=None, current=None):

    board = ""

    for r in range(ROWS):

        for c in range(COLS):

            pos = (r, c)

            if pos == current:
                board += "🟠"

            elif pos == start:
                board += "🟢"

            elif pos == goal:
                board += "🔴"

            elif grid[r][c] == 1:
                board += "⬛"

            elif path and pos in path:
                board += "🟦"

            else:
                board += "⬜"

        board += "\n"

    return board

# ------------------
# 초기 지도
# ------------------
st.subheader("지도")

st.text(draw_map())

st.markdown("""
🟢 시작점  
🔴 목표점  
⬛ 장애물  
🟦 탐색 경로  
🟠 현재 위치
""")

# ------------------
# 탐색 시작
# ------------------
if st.button("탐색 시작"):

    placeholder = st.empty()

    if algorithm == "언덕 등반 탐색":

        path, success = hill_climbing()

        st.subheader("탐색 과정")

        for node in path:

            placeholder.text(
                draw_map(path, node)
            )

            time.sleep(0.8)

        st.write("탐색 경로")

        st.code(str(path))

        if success:
            st.success("목표 도달 성공!")
        else:
            st.error("지역 최적해(Local Optimum)에 빠져 실패!")

    else:

        path, visited = a_star()

        st.subheader("탐색 과정")

        current_path = []

        for node in visited:

            current_path.append(node)

            placeholder.text(
                draw_map(current_path, node)
            )

            time.sleep(0.3)

        st.success("목표 도달 성공!")

        st.write("최단 경로")

        placeholder.text(
            draw_map(path)
        )

        st.code(str(path))
