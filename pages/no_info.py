import streamlit as st
import graphviz

# --- 1. 기본 페이지 설정 및 세련된 테마 적용 ---
st.set_page_config(page_title="AI 탐색 기초 교육", layout="wide")

st.markdown("""
    <style>
    /* 전체 배경을 차분한 소프트 그레이로 변경 */
    .main { background-color: #f8fafc; }
    
    /* 1. 상단 시뮬레이션 박스 (미니멀 디자인) */
    .sim-container {
        background: linear-gradient(to bottom, #f0fdf4 0%, #ffffff 100%);
        height: 160px;
        border-radius: 16px;
        position: relative;
        overflow: hidden;
        border: 1px solid #e2e8f0;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .land { background-color: #a3e635; width: 150px; height: 50px; position: absolute; bottom: 0; border-top: 3px solid #4d7c0f; }
    .land-left { left: 0; border-radius: 0 16px 0 0; }
    .land-right { right: 0; border-radius: 16px 0 0 0; }
    .river { background-color: #38bdf8; height: 35px; position: absolute; bottom: 0; left: 150px; right: 150px; }
    .char { font-size: 26px; position: absolute; transition: all 1.5s ease-in-out; }
    .boat { font-size: 34px; position: absolute; bottom: 3px; transition: all 1.5s ease-in-out; }
    
    /* 2. 하단 선택 버튼 세련되게 커스텀 (트리 노드 느낌의 라운딩) */
    div.stButton > button {
        border-radius: 24px !important;
        border: 1px solid #cbd5e1 !important;
        background-color: #ffffff !important;
        color: #334155 !important;
        font-weight: 600 !important;
        padding: 10px 20px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
        transition: all 0.2s ease-in-out !important;
    }
    div.stButton > button:hover {
        border-color: #4f46e5 !important;
        background-color: #f5f3ff !important;
        color: #4f46e5 !important;
        transform: translateY(-1px);
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. 게임 로직 및 세션 초기화 ---
if 'history' not in st.session_state:
    st.session_state.history = [('L','L','L','L')]
if 'search_mode' not in st.session_state:
    st.session_state.search_mode = "깊이 우선 탐색 (DFS)"

def get_allowed_moves(current_state):
    f, w, s, c = current_state
    next_f = 'R' if f == 'L' else 'L'
    candidates = []
    
    all_moves = [
        ((next_f, w, s, c), "👨‍🌾 농부 혼자 이동"),
        ((next_f, next_f, s, c), "🐺 늑대와 함께 이동"),
        ((next_f, w, next_f, c), "🐑 양과 함께 이동"),
        ((next_f, w, s, next_f), "🥬 양배추와 함께 이동")
    ]
    
    for state, label in all_moves:
        if "🐺" in label and f != w: continue
        if "🐑" in label and f != s: continue
        if "🥬" in label and f != c: continue
        # 직전 단계 중복 제어
        if len(st.session_state.history) > 1 and state == st.session_state.history[-2]: continue
        candidates.append((state, label))
    return candidates

def is_invalid(state):
    f, w, s, c = state
    if w == s and f != w: return True, "늑대가 양을 해쳤습니다! 🐺 먹힘 예방 실패"
    if s == c and f != s: return True, "양이 양배추를 먹어치웠습니다! 🐑 먹힘 예방 실패"
    return False, ""

# --- 3. 상단 레이아웃: 시뮬레이션 화면 ---
curr = st.session_state.history[-1]
f, w, s, c = curr

pos = lambda side, offset: f"{offset}px" if side == 'L' else f"calc(100% - {offset + 25}px)"
boat_pos = "22%" if f == 'L' else "68%"

st.markdown(f"""
    <div class="sim-container">
        <div class="land land-left"></div>
        <div class="land land-right"></div>
        <div class="river"></div>
        <div class="boat" style="left: {boat_pos};">🚣</div>
        <div class="char" style="left: {pos(f, 15)}; bottom: 45px;">👨‍🌾</div>
        <div class="char" style="left: {pos(w, 50)}; bottom: 12px;">🐺</div>
        <div class="char" style="left: {pos(s, 75)}; bottom: 12px;">🐑</div>
        <div class="char" style="left: {pos(c, 100)}; bottom: 12px;">🥬</div>
    </div>
""", unsafe_allow_html=True)

# --- 4. 안내 문구 및 제어부 ---
col_info, col_ctrl = st.columns([3, 1])
with col_ctrl:
    mode = st.radio("🔍 탐색 모드", ["깊이 우선 탐색 (DFS)", "너비 우선 탐색 (BFS)"], label_visibility="collapsed")
    if mode != st.session_state.search_mode:
        st.session_state.search_mode = mode
        st.session_state.history = [('L','L','L','L')]
        st.rerun()

with col_info:
    game_over, reason = is_invalid(curr)
    if game_over:
        st.error(f"🚨 **금지 상태 도달 (Game Over):** {reason}")
        if st.button("🔄 처음부터 다시 탐색"):
            st.session_state.history = [('L','L','L','L')]
            st.rerun()
    elif curr == ('R','R','R','R'):
        st.balloons()
        st.success("🎉 **목표 상태 도달 성공!** 모든 요소를 강 건너로 무사히 이동시켰습니다.")
        if st.button("🔄 게임 초기화 후 다시 하기"):
            st.session_state.history = [('L','L','L','L')]
            st.rerun()

# --- 5. 하단 레이아웃: 강제 격리형 트리 스크롤 박스 (HTML iframe 렌더링) ---
st.markdown("---")
st.write("🌲 **상태 공간 트리 (이 내부 공간 안에서 부드럽게 스크롤됩니다)**")

next_candidates = []
if not game_over and curr != ('R','R','R','R'):
    next_candidates = get_allowed_moves(curr)

# Graphviz 미니 노드 빌드
dot = graphviz.Digraph()
dot.attr(rankdir='TB', size='5,3!', ratio='fill')
dot.attr('node', shape='circle', width='0.2', height='0.2', fixedsize='true', fontsize='8', fontname="Arial")

for i, state in enumerate(st.session_state.history):
    node_lbl = "".join(state)
    if i == len(st.session_state.history) - 1:
        dot.node(f"h_{i}", node_lbl, style="filled", color="#4f46e5", fillcolor="#6366f1", fontcolor="white")
    else:
        dot.node(f"h_{i}", node_lbl, style="filled", color="#cbd5e1", fillcolor="#f1f5f9", fontcolor="#64748b")
    if i > 0:
        dot.edge(f"h_{i-1}", f"h_{i}", color="#94a3b8", arrowsize='0.4')

for idx, (cand_state, label_text) in enumerate(next_candidates):
    cand_lbl = "".join(cand_state)
    dot.node(f"c_{idx}", cand_lbl, style="filled", color="#10b981", fillcolor="#d1fae5", fontcolor="#065f46")
    dot.edge(f"h_{len(st.session_state.history)-1}", f"c_{idx}", style="dashed", color="#10b981", arrowsize='0.4')

svg_data = dot.pipe(format='svg').decode('utf-8')
scrollable_html = f"""
<div style="border: 2px solid #e2e8f0; border-radius: 12px; height: 260px; overflow-y: auto; overflow-x: hidden; padding: 10px; background-color: white; display: flex; justify-content: center;">
    {svg_data}
</div>
"""
st.components.v1.html(scrollable_html, height=280)

# --- 6. 수정된 선택기 (안전한 에러 핸들링 및 예외 처리) ---
if next_candidates:
    st.write("📍 **다음에 탐색할 대상을 선택하세요:**")
    # 컬럼을 생성하기 전에 리스트가 비어있지 않은지 검증(상단 조건문으로 보호)
    cols = st.columns(len(next_candidates))
    for idx, (cand_state, label_text) in enumerate(next_candidates):
        with cols[idx]:
            if st.button(label_text, key=f"action_btn_{idx}", use_container_width=True):
                st.session_state.history.append(cand_state)
                st.rerun()
elif not game_over and curr != ('R','R','R','R'):
    # 다음 후보는 없는데 게임 오버나 성공 상태가 아닌 막다른 길(Deadlock)인 경우
    st.warning("⚠️ **더 이상 이동할 수 있는 경로가 없습니다! (막다른 길)**")
    if st.button("⏪ 한 단계 뒤로 가기"):
        if len(st.session_state.history) > 1:
            st.session_state.history.pop()
            st.rerun()
