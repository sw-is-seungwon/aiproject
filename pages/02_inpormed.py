import streamlit as st

st.set_page_config(page_title="8 Puzzle")

st.title("언덕등반 탐색 - 8 Puzzle")

GOAL = [
[1, 2, 3],
[4, 5, 6],
[7, 8, 0]
]

board = [
[2, 8, 3],
[1, 6, 4],
[7, 0, 5]
]

def heuristic(state):
count = 0

for i in range(3):
    for j in range(3):
        if state[i][j] != 0 and state[i][j] != GOAL[i][j]:
            count += 1

return count

st.subheader("현재 상태")

for row in board:
st.write(row)

st.metric(
"h(n)",
heuristic(board)
)

st.write("언덕등반 탐색 예제 화면")
