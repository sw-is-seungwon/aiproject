import streamlit as st
import graphviz

# --- 1. 기본 설정 및 컴포넌트 강제 스크롤 스타일 ---
st.set_page_config(page_title="AI 탐색 기초 교육", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    
    /* 1. 상단 시뮬레이션 박스 */
    .sim-container {
        background: linear-gradient(to bottom, #e2f5ff 0%, #ffffff 100%);
        height: 160px;
        border-radius: 12px;
        position: relative;
        overflow: hidden;
        border: 2px solid #cbd5e1;
        margin-bottom: 5px;
    }
    .land { background-color: #8be475; width: 140px; height: 60px; position: absolute; bottom: 0; border-top: 4px solid #65a30d; }
    .land-left { left: 0; border-radius: 0 12px 0 0; }
    .land-right { right: 0; border-radius: 12px 0 0 0; }
    .river { background-color: #38bdf8; height: 40px; position: absolute; bottom: 0; left: 140px; right: 140px; }
    .char { font-size: 26px; position: absolute; transition: all 1.5s ease-in-out; }
    .boat { font-size: 36px; position: absolute; bottom: 5px; transition: all 1.5s ease-in-out; }
    
    /* 2. 트리를 감싸는 Streamlit block 자체를 스크롤 박스로 강제 지정 (바깥 탈출 방지) */
    [data-testid="stVerticalBlockBorderWrapper"] [data-testid="element-container"]:has(.stGraphvizChart) {
        border: 2px solid #4f46e5;
        border-radius: 12px;
        max-height: 280px;
        overflow-y: auto !important;
        overflow-x: auto !important;
        padding: 10px;
        background-color: white;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* 3. 노드 링크 버튼 스타일 (트리 노드와 시각적 일치) */
    div.stButton > button {
        border-radius: 20px !important;
        border: 2px solid #22c55e !important;
        background-color: #bbf7d0 !important;
        color: #166534 !important;
        font-weight: bold !important;
        transition: all 0.2s;
    }
    div.stButton > button:hover {
        background-color: #16a34a !important;
        color: white !important;
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
        ((next_f, w, s, c), "농부 혼자 이동"),
        ((next_f, next_f, s, c), "농부 & 늑대 이동"),
        ((next_f, w, next_f, c), "농부 & 양 이동"),
        ((next_f, w, s, next_f), "농부 & 양배추 이동")
    ]
    
    for state, label in all_moves:
        if label == "농부 & 늑대 이동" and f != w: continue
        if label == "농부 & 양 이동" and f != s: continue
        if label == "농부 & 양배추 이동" and f != c: continue
        if len(st.session_state.history) > 1 and state == st.session_state.history[-2]: continue
        candidates.append((state, label))
    return candidates

def is_invalid(state):
    f, w, s, c = state
    if w == s and f != w: return True, "🐺 늑대가 🐑 양을 해쳤습니다!"
    if s == c and f != s: return True, "🐑 양이 🥬 양배추를 먹었습니다!"
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
        <div class="char" style="left: {pos(f, 15)}; bottom: 50px;">👨‍🌾</div>
        <div class="char" style="left: {pos(w, 50)}; bottom: 15px;">🐺</div>
        <div class="char" style="left: {pos(s, 75)}; bottom: 15px;">🐑</div>
        <div class="char" style="left: {pos(c, 100)}; bottom: 15px;">🥬</div>
    </div>
""", unsafe_allow_html=True)

# --- 4. 제어 및 상태 메시지 ---
col_info, col_ctrl = st.columns([3, 1])
with col_ctrl:
    mode = st.radio("🔍 알고리즘 선택", ["깊이 우선 탐색 (DFS)", "너비 우선 탐색 (BFS)"], label_visibility="collapsed")
    if mode != st.session_state.search_mode:
        st.session_state.search_mode = mode
        st.session_state.history = [('L','L','L','L')]
        st.rerun()

with col_info:
    game_over, reason = is_invalid(curr)
    if game_over:
        st.error(f"🚨 **금지 상태 도달:** {reason}")
        if st.button("🔄 처음부터 다시 하기", use_container_width=True):
            st.session_state.history = [('L','L','L','L')]
            st.rerun()
    elif curr == ('R','R','R','R'):
        st.balloons()
        st.success("🎉 **목표 상태 도달 성공!**")
        if st.button("🔄 다시 도전하기", use_container_width=True):
            st.session_state.history = [('L','L','L','L')]
            st.rerun()

# --- 5. 하단 레이아웃: 트리 컴포넌트 자체를 가두는 공간 ---
st.markdown("---")
st.write("🌲 **상태 공간 트리 (지정된 테두리 안에서만 스크롤됩니다)**")

# 후보 노드 정보 가져오기
next_candidates = []
if not game_over and curr != ('R','R','R','R'):
    next_candidates = get_allowed_moves(curr)

# 초미니(Micro) 노드 규격 설정
dot = graphviz.Digraph()
dot.attr(rankdir='TB', size='5,3!', ratio='fill')
dot.attr('node', shape='circle', width='0.25', height='0.25', fixedsize='true', fontsize='8')

# 1) 기존 방문 노드 배치
for i, state in enumerate(st.session_state.history):
    node_lbl = "".join(state)
    if i == len(st.session_state.history) - 1:
        dot.node(f"h_{i}", node_lbl, style="filled", color="#1e40af", fillcolor="#3b82f6", fontcolor="white")
    else:
        dot.node(f"h_{i}", node_lbl, style="filled", color="#94a3b8", fillcolor="#cbd5e1", fontcolor="#475569")
    if i > 0:
        dot.edge(f"h_{i-1}", f"h_{i}", color="#64748b", arrowsize='0.4')

# 2) 다음 선택 후보 노드 배치 (연두색 점선)
for idx, (cand_state, label_text) in enumerate(next_candidates):
    cand_lbl = "".join(cand_state)
    dot.node(f"c_{idx}", cand_lbl, style="filled", color="#16a34a", fillcolor="#bbf7d0", fontcolor="#166534")
    dot.edge(f"h_{len(st.session_state.history)-1}", f"c_{idx}", style="dashed", color="#22c55e", arrowsize='0.4')

# Graphviz 차트 호출 (CSS 백엔드 스크롤러가 감지하여 박스 내부에 가둠)
st.graphviz_chart(dot, use_container_width=True)

# --- 6. 트리 노드와 1:1 매칭되는 하단 액션 버튼 ---
if next_candidates:
    st.write("📍 **확장할 노드를 선택하세요:**")
    cols = st.columns(len(next_candidates))
    for idx, (cand_state, label_text) in enumerate(next_candidates):
        with cols[idx]:
            # CSS를 통해 초록색 라운드 노드 형태로 커스텀된 버튼
            if st.button(f"🔴 {''.join(cand_state)} ({label_text.split(' ')[1]})", key=f"nd_{idx}", use_container_width=True):
                st.session_state.history.append(cand_state)
                st.rerun()
