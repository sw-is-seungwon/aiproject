import streamlit as st
import graphviz

# 1. 초기 세션 상태 설정
if 'history' not in st.session_state:
    st.session_state.history = ['L,L,L,L']  # 방문한 노드 기록 (농부, 늑대, 양, 양배추)
if 'game_status' not in st.session_state:
    st.session_state.game_status = 'PLAYING' # PLAYING, GAMEOVER, CLEAR
if 'open_list' not in st.session_state:
    st.session_state.open_list = ['L,L,L,L'] # 탐색을 위해 열려있는 노드들

st.set_page_config(layout="wide")
st.title("🤖 AI 기초: 상태 공간 탐색 게임 (농부와 동물들)")
st.caption("깊이 우선 탐색(DFS)과 너비 우선 탐색(BFS)의 차이를 시뮬레이션으로 배워봅시다.")

# 2. 사이드바: 탐색 기법 선택
search_method = st.sidebar.radio("🔍 탐색 기법 선택", ["깊이 우선 탐색 (DFS)", "너비 우선 탐색 (BFS)"])

# 게임 리셋 함수
def reset_game():
    st.session_state.history = ['L,L,L,L']
    st.session_state.game_status = 'PLAYING'
    st.session_state.open_list = ['L,L,L,L']

st.sidebar.button("🔄 게임 다시 시작", on_click=reset_game)

# 3. 게임 로직 및 상태 전이 함수
def get_next_states(state_str):
    """현재 상태에서 이동 가능한 다음 상태들을 반환"""
    f, w, s, c = state_str.split(',')
    next_f = 'R' if f == 'L' else 'L'
    possible = []
    
    # 1. 농부 혼자 이동
    possible.append(f"{next_f},{w},{s},{c}")
    # 2. 농부가 늑대와 이동
    if f == w: possible.append(f"{next_f},{next_f},{s},{c}")
    # 3. 농부가 양과 이동
    if f == s: possible.append(f"{next_f},{w},{next_f},{c}")
    # 4. 농부가 양배추와 이동
    if f == c: possible.append(f"{next_f},{w},{s},{next_f}")
    
    return possible

def check_game_over(state_str):
    f, w, s, c = state_str.split(',')
    if w == s and f != w: return True  # 늑대가 양을 먹음
    if s == c and f != s: return True  # 양이 양배추를 먹음
    return False

# 현재 활성화된(선택된) 최신 상태
current_state = st.session_state.history[-1]

# 게임 상태 체크
if current_state == 'R,R,R,R':
    st.session_state.game_status = 'CLEAR'
elif check_game_over(current_state):
    st.session_state.game_status = 'GAMEOVER'

# --- 화면 분할 (왼쪽: 트리, 오른쪽: 시뮬레이션) ---
col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("🌲 상태 공간 트리 (State Space Tree)")
    
    # Graphviz를 이용한 트리 생성
    dot = graphviz.Digraph(comment='State Space Tree')
    dot.attr(rankdir='TB')
    
    # 규칙에 따른 다음 노드 확장 (DFS vs BFS 시각화 로직)
    # 학생들의 이해를 돕기 위해 현재까지 방문한 경로를 트리로 시각화
    for i, node in enumerate(st.session_state.history):
        if node == current_state:
            dot.node(f"node_{i}", node, color='red', penwidth='3') # 현재 노드는 강조
        else:
            dot.node(f"node_{i}", node, color='gray', style='filled', fillcolor='lightgray') # 지나온 노드는 흐리게
        
        if i > 0:
            dot.edge(f"node_{i-1}", f"node_{i}")
            
    # 다음 선택 가능한 후보 노드들 보여주기
    if st.session_state.game_status == 'PLAYING':
        next_candidates = get_next_states(current_state)
        
        # 알고리즘 선택에 따른 시각적 힌트 분기 (4번 요구사항 구현)
        if search_method == "깊이 우선 탐색 (DFS)":
            st.info("💡 **DFS 법칙:** 방금 확장한 노드의 자식 노드들을 깊숙하게 탐색합니다. (새로운 경로 생성 가능)")
        else:
            st.info("💡 **BFS 법칙:** 현재 깊이(레벨)의 모든 노드를 먼저 탐색하므로, 한 번에 깊은 자식 노드가 새로 열리지 않습니다.")

        # 후보 노드 선택 버튼 생성
        st.write("**다음 행동(노드)을 선택하세요:**")
        cols_btn = st.columns(len(next_candidates))
        for idx, cand in enumerate(next_candidates):
            with cols_btn[idx]:
                if st.button(f"➡️ {cand}", key=f"btn_{cand}_{idx}"):
                    st.session_state.history.append(cand)
                    st.rerun()

    st.graphviz_chart(dot, use_container_width=True)

with col2:
    st.subheader("🚣 실시간 시뮬레이션 상황")
    
    # 현재 상태 파싱 및 이모지 시각화
    f, w, s, c = current_state.split(',')
    
    left_bank = []
    right_bank = []
    
    if f == 'L': left_bank.append("👨‍🌾 농부")
    else: right_bank.append("👨‍🌾 농부")
    if w == 'L': left_bank.append("🐺 늑대")
    else: right_bank.append("🐺 늑대")
    if s == 'L': left_bank.append("🐑 양")
    else: right_bank.append("🐑 양")
    if c == 'L': left_bank.append("🥬 양배추")
    else: right_bank.append("🥬 양배추")
    
    # 화면에 이모지로 강 상황 표현
    st.warning(f"**[시작점 (왼쪽)]** {' / '.join(left_bank)}")
    st.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n~~~~~~~~~~ 🌊 강물 🌊 ~~~~~~~~~~\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    st.success(f"**[목적지 (오른쪽)]** {' / '.join(right_bank)}")
    
    st.markdown("---")
    
    # 게임 결과 출력
    if st.session_state.game_status == 'GAMEOVER':
        st.error("🚨 GAME OVER! 규칙을 위반하여 동물이나 양배추가 먹혔습니다.")
        if st.button("다시 도전하기", key="retry_btn"):
            reset_game()
            st.rerun()
    elif st.session_state.game_status == 'CLEAR':
        st.balloons()
        st.success("🎉 GAME CLEAR! 모든 물품을 안전하게 강 건너로 이동시켰습니다!")
        st.write(f"**이동 경로 ({len(st.session_state.history)-1}회 이동):**")
        st.code(" -> ".join(st.session_state.history))
