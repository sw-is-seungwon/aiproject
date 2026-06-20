import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import random
import copy

st.set_page_config(page_title="정보 이용 탐색 알고리즘", layout="wide")

# =====================================================

# 8퍼즐 관련 함수

# =====================================================

GOAL = [
[1,2,3],
[4,5,6],
[7,8,0]
]

INITIAL_PUZZLE = [
[2,8,3],
[1,6,4],
[7,0,5]
]

def misplaced_tiles(board):
count = 0
for i in range(3):
for j in range(3):
if board[i][j] != 0 and board[i][j] != GOAL[i][j]:
count += 1
return count

def find_blank(board):
for i in range(3):
for j in range(3):
if board[i][j] == 0:
return i, j

def possible_moves(board):
r, c = find_blank(board)

```
moves = []

directions = {
    "위":(-1,0),
    "아래":(1,0),
    "왼쪽":(0,-1),
    "오른쪽":(0,1)
}

for name, (dr,dc) in directions.items():

    nr = r + dr
    nc = c + dc

    if 0 <= nr < 3 and 0 <= nc < 3:
        new_board = copy.deepcopy(board)

        new_board[r][c], new_board[nr][nc] = \
            new_board[nr][nc], new_board[r][c]

        h = misplaced_tiles(new_board)

        moves.append((name,new_board,h))

return moves
```

def board_to_text(board):
text = ""

```
for row in board:
    for v in row:
        if v == 0:
            text += "□ "
        else:
            text += str(v)+" "
    text += "\n"

return text
```

# =====================================================

# 학교 지도

# =====================================================

heuristic = {
"교실":60,
"복도A":45,
"복도B":40,
"계단1":30,
"계단2":25,
"도서관":15,
"과학실":20,
"체육관":10,
"강당":15,
"급식실":0
}

edges = [
("교실","복도A",20),

```
("복도A","복도B",10),
("복도A","계단1",15),

("복도B","계단2",20),

("계단1","계단2",15),
("계단1","도서관",10),

("계단2","과학실",10),

("도서관","과학실",15),

("도서관","체육관",20),

("과학실","강당",20),

("체육관","강당",10),

("체육관","급식실",15)
```

]

G = nx.Graph()

for node in heuristic:
G.add_node(node)

for u,v,w in edges:
G.add_edge(u,v,weight=w)

positions = {
"교실":(0,4),

```
"복도A":(-2,3),
"복도B":(2,3),

"계단1":(-2,2),
"계단2":(2,2),

"도서관":(-2,1),
"과학실":(2,1),

"체육관":(-2,0),
"강당":(2,0),

"급식실":(-2,-1)
```

}

# =====================================================

# 세션

# =====================================================

if "puzzle" not in st.session_state:
st.session_state.puzzle = copy.deepcopy(INITIAL_PUZZLE)

if "current_node" not in st.session_state:
st.session_state.current_node = "교실"

if "visited" not in st.session_state:
st.session_state.visited = ["교실"]

if "g_cost" not in st.session_state:
st.session_state.g_cost = 0

# =====================================================

# 메뉴

# =====================================================

st.title("정보 이용 탐색 알고리즘 체험")

mode = st.radio(
"알고리즘 선택",
["언덕등반 탐색", "최상우선 탐색", "A* 탐색"]
)

# =====================================================

# 언덕등반 탐색

# =====================================================

if mode == "언덕등반 탐색":

```
st.header("8퍼즐 : 언덕등반 탐색")

board = st.session_state.puzzle

col1,col2 = st.columns(2)

with col1:
    st.subheader("목표 상태")
    st.text(board_to_text(GOAL))

with col2:
    st.subheader("현재 상태")
    st.text(board_to_text(board))

current_h = misplaced_tiles(board)

st.metric("현재 평가함수 h(n)", current_h)

moves = possible_moves(board)

st.subheader("가능한 이동")

for name,new_board,h in moves:
    st.write(f"{name} → h={h}")

if st.button("다음 이동 선택"):

    best_move = min(moves, key=lambda x:x[2])

    if best_move[2] >= current_h:
        st.error("지역 최적해(Local Optimum)에 도달했습니다.")
    else:
        st.session_state.puzzle = best_move[1]
        st.success(
            f"{best_move[0]} 이동 선택! h={best_move[2]}"
        )
        st.rerun()

if st.button("8퍼즐 초기화"):
    st.session_state.puzzle = copy.deepcopy(INITIAL_PUZZLE)
    st.rerun()
```

# =====================================================

# 최상우선 탐색

# =====================================================

elif mode == "최상우선 탐색":

```
st.header("학교 길찾기 : 최상우선 탐색")

fig, ax = plt.subplots(figsize=(8,6))

node_colors = []

for node in G.nodes():
    if node == st.session_state.current_node:
        node_colors.append("red")
    elif node in st.session_state.visited:
        node_colors.append("orange")
    else:
        node_colors.append("lightblue")

labels = {}

for n in G.nodes():
    labels[n] = f"{n}\nh={heuristic[n]}"

nx.draw(
    G,
    positions,
    labels=labels,
    node_color=node_colors,
    node_size=2500,
    ax=ax
)

edge_labels = nx.get_edge_attributes(G,'weight')

nx.draw_networkx_edge_labels(
    G,
    positions,
    edge_labels=edge_labels,
    ax=ax
)

st.pyplot(fig)

current = st.session_state.current_node

st.info("평가함수 : f(n)=h(n)")

neighbors = []

for n in G.neighbors(current):

    if n not in st.session_state.visited:

        neighbors.append((n,heuristic[n]))

if neighbors:

    st.subheader("후보 노드")

    for n,h in neighbors:
        st.write(f"{n} → h={h}")

    if st.button("다음 노드 선택"):

        best = min(neighbors,key=lambda x:x[1])

        st.session_state.current_node = best[0]
        st.session_state.visited.append(best[0])

        st.success(
            f"{best[0]} 선택 (h={best[1]})"
        )

        st.rerun()

if current == "급식실":
    st.success("급식실 도착!")

if st.button("최상우선 초기화"):
    st.session_state.current_node = "교실"
    st.session_state.visited = ["교실"]
    st.rerun()
```

# =====================================================

# A*

# =====================================================

else:

```
st.header("학교 길찾기 : A* 탐색")

fig, ax = plt.subplots(figsize=(8,6))

node_colors = []

for node in G.nodes():

    if node == st.session_state.current_node:
        node_colors.append("red")

    elif node in st.session_state.visited:
        node_colors.append("orange")

    else:
        node_colors.append("lightgreen")

labels = {}

for n in G.nodes():
    labels[n] = f"{n}\nh={heuristic[n]}"

nx.draw(
    G,
    positions,
    labels=labels,
    node_color=node_colors,
    node_size=2500,
    ax=ax
)

edge_labels = nx.get_edge_attributes(G,'weight')

nx.draw_networkx_edge_labels(
    G,
    positions,
    edge_labels=edge_labels,
    ax=ax
)

st.pyplot(fig)

current = st.session_state.current_node

st.info("평가함수 : f(n)=g(n)+h(n)")

candidates = []

for neighbor in G.neighbors(current):

    if neighbor not in st.session_state.visited:

        cost = G[current][neighbor]["weight"]

        g = st.session_state.g_cost + cost

        h = heuristic[neighbor]

        f = g + h

        candidates.append(
            (neighbor,g,h,f,cost)
        )

if candidates:

    st.subheader("후보 노드")

    for n,g,h,f,c in candidates:

        st.write(
            f"{n} → g={g}, h={h}, f={f}"
        )

    if st.button("A* 다음 이동"):

        best = min(
            candidates,
            key=lambda x:x[3]
        )

        st.session_state.current_node = best[0]
        st.session_state.visited.append(best[0])
        st.session_state.g_cost = best[1]

        st.success(
            f"{best[0]} 선택 (f={best[3]})"
        )

        st.rerun()

st.write(
    f"현재 누적 비용 g(n) = {st.session_state.g_cost}"
)

if current == "급식실":
    st.success("급식실 도착!")

if st.button("A* 초기화"):

    st.session_state.current_node = "교실"
    st.session_state.visited = ["교실"]
    st.session_state.g_cost = 0

    st.rerun()
```
