import streamlit as st
import graphviz

# --- 1. 기본 설정 및 스타일 ---
st.set_page_config(page_title="AI 탐색 기초 교육", layout="wide")

st.markdown("""
    <style>
    /* 전체 배경 및 폰트 */
    .main { background-color: #f0f4f8; }
    
    /* 시뮬레이션 박스 스타일 (전달해주신 이미지 느낌) */
    .sim-container {
        background: linear-gradient(to bottom, #d9f99d 0%, #ffffff 100%);
        height: 250px;
        border-radius: 20px;
        position: relative;
        overflow: hidden;
        border: 2px solid #e2e8f0;
        margin-bottom: 20px;
    }
    .land { background-color: #fb923c; width: 150px; height: 80px; position: absolute; bottom: 0; }
    .land-left { left: 0; border-radius: 0 20px 0 0; }
    .land-right { right: 0; border-radius: 20px 0 0 0; }
    .river { background-color: #7dd3fc; height: 60px; position: absolute; bottom: 0; left: 150px; right: 150px; }
    
    /* 캐릭터 아이콘 */
    .char { font-size: 35px; position: absolute; transition: all 0.5s ease-in-out; }
    .boat { font-size: 45px; position: absolute; bottom: 15px; transition: all 0.5s ease-in-out; }
    
    /* 하단 노드 선택 영역 */
    .node-option {
        background-color: white;
        border: 2px solid #6366f1;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        font-weight: bold;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. 게임 로직 및 세션 관리 ---
if 'history' not in st.session_state:
    st.session_state.history = [('L','L','L','L')] # (농부, 늑대, 양, 양배추)
if 'search_mode' not in st.session_state:
    st.session_state.search_mode = "DFS"
if 'game_over' not in st.session_state:
    st.session_state.game_over = False

def get_allowed_moves(state):
    f, w, s, c = state
    next_f = 'R' if f == 'L' else 'L'
    moves = []
    # 가능한 이동: 혼자, 늑대와, 양과, 양배추와
    candidates = [ (next_f, w, s, c) ]
    if f == w: candidates.append((next_f, next_f, s, c))
    if f == s: candidates.append((next_f, w, next_f, c))
    if f == c: candidates.append((next_f, w, s, next_f))
    return candidates

def is_invalid(state):
    f, w, s, c = state
    if w == s and f != w: return True # 늑대+양
    if s == c and f != s: return True # 양+양배추
    return False

# --- 3. 상단: 시뮬레이션 화면 (이미지 스타일 구현) ---
curr = st.session_state.history[-1]
f, w, s, c = curr

# 캐릭터 위치 계산
pos = lambda side, offset: f"{offset}px" if side == 'L' else f"calc(100% - {offset + 40}px)"
boat_pos = "20%" if f == 'L' else "70%"

st.markdown(f"""
    <div class="sim-container">
        <div class="land land-left"></div>
        <div class="land land-right"></div>
        <div class="river"></div>
        <div class="boat" style="left: {boat_pos};">🚣</div>
        <div class="char" style="left: {pos(f, 20)}; bottom: 70px;">👨‍🌾</div>
        <div class="char" style="left: {pos(w, 70)}; bottom: 30px;">🐺</div>
        <div class="char" style="left: {pos(s, 100)}; bottom: 30px;">🐑</div>
        <div class="char" style="left: {pos(c, 130)}; bottom: 30px;">🥬</div>
    </div>
""", unsafe_allow_html=True)

# --- 4. 중단: 메시지 및 컨트롤 ---
col_msg, col_mode = st.columns([3, 1])
with col_mode:
    mode = st.radio("탐색 기법 선택", ["DFS", "BFS"], horizontal=True)
    if mode != st.session_state.search_mode:
        st.session_state.search_mode = mode
        st.session_state.history = [('L','L','L','L')]
        st.rerun()

with col_msg:
    if is_invalid(curr):
        st.error("🚨 먹혔습니다! 게임 오버.")
        if st.button("다시 시작"):
            st.session_state.history = [('L','L','L','L')]
            st.rerun()
    elif curr == ('R','R','R','R'):
        st.success("🎉 축하합니다! 모든 미션을 완료했습니다!")
        if st.button("다시 도전"):
            st.session_state.history = [('L','L','L','L')]
            st.rerun()
    else:
        st.info("💡 배에 누구를 태워 보낼지 아래 노드에서 선택하세요.")

# --- 5. 하단: 노드 트리 및 선택창 ---
st.markdown("---")
tree_col, select_col = st.columns([2, 1])

with tree_col:
    st.write("🌲 **상태 공간 트리 (진행 경로)**")
    dot = graphviz.Digraph()
    dot.attr(rankdir='LR', size='10,3!', fixedsize='true') # 가로로 길고 컴팩트하게
    
    for i, state in enumerate(st.session_state.history):
        label = "".join(state)
        # 노드 스타일링 (작고 심플하게)
        color = "#6366f1" if i == len(st.session_state.history)-1 else "#cbd5e1"
        dot.node(str(i), label, shape="circle", width="0.6", color=color, fontname="Arial")
        if i > 0:
            dot.edge(str(i-1), str(i))
    st.graphviz_chart(dot)

with select_col:
    st.write("📍 **다음 단계 선택**")
    next_moves = get_allowed_moves(curr)
    
    # DFS/BFS 원리에 따른 노드 노출 로직
    # DFS는 현재의 자식만, BFS는 동일 레벨을 고려해야 하지만 
    # 교육용 시뮬레이션에서는 '선택 가능한 다음 노드'를 알고리즘 힌트와 함께 제공
    if st.session_state.search_mode == "DFS":
        st.caption("DFS: 방금 도달한 상태에서 더 깊이 들어갑니다.")
    else:
        st.caption("BFS: 현재 깊이의 모든 가능성을 먼저 검토합니다.")

    for i, move in enumerate(next_moves):
        # 이동 시 농부와 함께 가는 대상 찾기
        diff = []
        names = ["농부", "늑대", "양", "양배추"]
        for j in range(4):
            if curr[j] != move[j]: diff.append(names[j])
        
        move_label = " & ".join(diff) if diff else "농부 혼자"
        
        if st.button(f"선택 {i+1}: {move_label}", use_container_width=True):
            st.session_state.history.append(move)
            st.rerun()

st.markdown("""
<script>
    // 자동 스크롤 로직 (Streamlit 컴포넌트 특성상 완벽한 제어는 어렵지만 트리 업데이트 시 시각적 유지 유도)
    window.scrollTo(0, document.body.scrollHeight);
</script>
""", unsafe_allow_html=True)
