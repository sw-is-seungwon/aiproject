import streamlit as st
import copy

st.set_page_config(
page_title="언덕등반 탐색 - 8퍼즐",
layout="wide"
)

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

def heuristic(board):
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

def get_moves(board):

```
r, c = find_blank(board)

result = []

directions = {
    "위": (-1, 0),
    "아래": (1, 0),
    "왼쪽": (0, -1),
    "오른쪽": (0, 1)
}

for name, (dr, dc) in directions.items():

    nr = r + dr
    nc = c + dc

    if 0 <= nr < 3 and 0 <= nc < 3:

        new_board = copy.deepcopy(board)

        new_board[r][c], new_board[nr][nc] = (
            new_board[nr][nc],
            new_board[r][c]
        )

        h = heuristic(new_board)

        result.append((name, new_board, h))

return result
```

def board_to_text(board):

```
lines = []

for row in board:

    row_text = []

    for value in row:

        if value == 0:
            row_text.append("□")
        else:
            row_text.append(str(value))

    lines.append(" ".join(row_text))

return "\n".join(lines)
```

if "board" not in st.session_state:
st.session_state.board = copy.deepcopy(INITIAL)

if "step" not in st.session_state:
st.session_state.step = 0

st.title("언덕등반 탐색(Hill Climbing) - 8퍼즐")

st.markdown("""

### 평가함수

**h(n) = 제자리에 있지 않은 타일 개수**

언덕등반 탐색은 현재 상태보다 더 좋은 상태(h값 감소)만 선택합니다.
""")

col1, col2 = st.columns(2)

with col1:
st.subheader("목표 상태")
st.text(board_to_text(GOAL))

with col2:
st.subheader("현재 상태")
st.text(board_to_text(st.session_state.board))

current_h = heuristic(st.session_state.board)

st.metric(
"현재 h(n)",
current_h
)

st.write("이동 횟수:", st.session_state.step)

moves = get_moves(st.session_state.board)

st.subheader("가능한 이동")

for name, board, h in moves:
st.write(f"{name} 이동 → h(n) = {h}")

if current_h == 0:

```
st.success("목표 상태에 도달했습니다!")
```

else:

```
if st.button("언덕등반 탐색 한 단계 진행"):

    best_move = min(
        moves,
        key=lambda x: x[2]
    )

    if best_move[2] >= current_h:

        st.error(
            "더 좋은 상태가 없어 지역 최적해(Local Optimum)에 도달했습니다."
        )

    else:

        st.session_state.board = best_move[1]
        st.session_state.step += 1
        st.rerun()
```

if st.button("끝까지 자동 실행"):

```
board = copy.deepcopy(st.session_state.board)

history = []

while True:

    current = heuristic(board)

    if current == 0:
        break

    candidates = get_moves(board)

    best = min(
        candidates,
        key=lambda x: x[2]
    )

    if best[2] >= current:
        break

    history.append(
        f"{best[0]} 이동 → h={best[2]}"
    )

    board = best[1]

st.subheader("탐색 과정")

if len(history) == 0:
    st.write("더 진행할 수 없습니다.")

else:
    for item in history:
        st.write(item)
```

if st.button("초기화"):

```
st.session_state.board = copy.deepcopy(INITIAL)
st.session_state.step = 0
st.rerun()
```
