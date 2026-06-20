import streamlit as st
import copy

st.set_page_config(page_title="정보 이용 탐색", layout="wide")

# =====================================================

# 8퍼즐

# =====================================================

GOAL = [
[1, 2, 3],
[4, 5, 6],
[7, 8, 0]
]

INITIAL = [
[2, 8, 3],
[1, 6, 4],
[7, 0, 5]
]

def h_value(board):
count = 0

```
for i in range(3):
    for j in range(3):
        if board[i][j] != 0 and board[i][j] != GOAL[i][j]:
            count += 1

return count
```

def find_blank(board):
for i in range(3):
for j in range(3):
if board[i][j] == 0:
return i, j

def moves(board):

```
r, c = find_blank(board)

result = []

dirs = {
    "위": (-1, 0),
    "아래": (1, 0),
    "왼쪽": (0, -1),
    "오른쪽": (0, 1)
}

for name, (dr, dc) in dirs.items():

    nr = r + dr
    nc = c + dc

    if 0 <= nr < 3 and 0 <= nc < 3:

        new_board = copy.deepcopy(board)

        new_board[r][c], new_board[nr][nc] = \
            new_board[nr][nc], new_board[r][c]

        result.append(
            (name, new_board, h_value(new_board))
        )

return result
```

def board_text(board):

```
text = ""

for row in board:

    for value in row:

        if value == 0:
            text += "□ "
        else:
            text += str(value) + " "

    text += "\n"

return text
```

# =====================================================

# 학교 지도

# =====================================================

heuristic = {
"교실": 60,
"복도A": 45,
"복도B": 40,
"계단1": 30,
"계단2": 25,
"도서관": 15,
"과학실": 20,
"체육관": 10,
"강당": 15,
"급식실": 0
}

graph = {
"교실": [("복도A", 20)],

```
"복도A": [("교실", 20),
         ("복도B", 10),
         ("계단1", 15)],

"복도B": [("복도A", 10),
         ("계단2", 20)],

"계단1": [("복도A", 15),
         ("계단2", 15),
         ("도서관", 10)],

"계단2": [("복도B", 20),
         ("계단1", 15),
         ("과학실", 10)],

"도서관": [("계단1", 10),
         ("과학실", 15),
         ("체육관", 20)],

"과학실": [("계단2", 10),
         ("도서관", 15),
         ("강당", 20)],

"체육관": [("도서관", 20),
         ("강당", 10),
         ("급식실", 15)],

"강당": [("과학실", 20),
        ("체육관", 10)],

"급식실": [("체육관", 15)]
```

}

# =====================================================

# 세션

# =====================================================

if "board" not in st.session_state:
st.session_state.board = copy.deepcopy(INITIAL)

if "node" not in st.session_state:
st.session_state.node = "교실"

if "visited" not in st.session_state:
st.session_state.visited = ["교실"]

if "g" not in st.session_state:
st.session_state.g = 0

# =====================================================

# 메뉴

# =====================================================

st.title("정보 이용 탐색 알고리즘")

menu = st.radio(
"선택",
["언덕등반 탐색", "최상우선 탐색", "A* 탐색"]
)

# =====================================================

# 언덕등반 탐색

# =====================================================

if menu == "언덕등반 탐색":

```
st.header("8퍼즐 - 언덕등반 탐색")

col1, col2 = st.columns(2)

with col1:
    st.subheader("목표 상태")
    st.text(board_text(GOAL))

with col2:
    st.subheader("현재 상태")
    st.text(board_text(st.session_state.board))

current_h = h_value(st.session_state.board)

st.metric("현재 h(n)", current_h)

candidate_moves = moves(st.session_state.board)

st.subheader("가능한 이동")

for name, board, h in candidate_moves:
    st.write(f"{name} → h={h}")

if st.button("다음 이동"):

    best = min(candidate_moves, key=lambda x: x[2])

    if best[2] >= current_h:
        st.error("지역 최적해(Local Optimum)")
    else:
        st.session_state.board = best[1]
        st.rerun()

if st.button("퍼즐 초기화"):
    st.session_state.board = copy.deepcopy(INITIAL)
    st.rerun()
```

# =====================================================

# 최상우선 탐색

# =====================================================

elif menu == "최상우선 탐색":

```
st.header("최상우선 탐색")

current = st.session_state.node

st.write("현재 위치 :", current)

st.write("평가함수")
st.code("f(n) = h(n)")

candidates = []

for next_node, cost in graph[current]:

    if next_node not in st.session_state.visited:

        candidates.append(
            (next_node,
             heuristic[next_node])
        )

st.subheader("OPEN 리스트")

for node, h in candidates:
    st.write(f"{node} : h={h}")

if candidates:

    best = min(candidates, key=lambda x: x[1])

    st.success(
        f"선택 예정 노드 : {best[0]}"
    )

    if st.button("다음 단계"):

        st.session_state.node = best[0]
        st.session_state.visited.append(best[0])

        st.rerun()

if current == "급식실":
    st.success("급식실 도착!")

if st.button("최상우선 초기화"):

    st.session_state.node = "교실"
    st.session_state.visited = ["교실"]

    st.rerun()
```

# =====================================================

# A*

# =====================================================

else:

```
st.header("A* 탐색")

current = st.session_state.node

st.write("현재 위치 :", current)

st.write("평가함수")
st.code("f(n) = g(n) + h(n)")

st.write(
    f"현재 누적비용 g(n) = {st.session_state.g}"
)

candidates = []

for next_node, cost in graph[current]:

    if next_node not in st.session_state.visited:

        g = st.session_state.g + cost

        h = heuristic[next_node]

        f = g + h

        candidates.append(
            (next_node, g, h, f)
        )

st.subheader("OPEN 리스트")

for node, g, h, f in candidates:

    st.write(
        f"{node} → g={g}, h={h}, f={f}"
    )

if candidates:

    best = min(candidates, key=lambda x: x[3])

    st.success(
        f"선택 예정 노드 : {best[0]}"
    )

    if st.button("다음 단계"):

        st.session_state.node = best[0]
        st.session_state.g = best[1]

        st.session_state.visited.append(
            best[0]
        )

        st.rerun()

if current == "급식실":
    st.success("급식실 도착!")

if st.button("A* 초기화"):

    st.session_state.node = "교실"
    st.session_state.visited = ["교실"]
    st.session_state.g = 0

    st.rerun()
```
