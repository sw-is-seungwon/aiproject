import streamlit as st
import graphviz

# --- 1. 기본 설정 및 미감 향상 (스크롤 및 디자인) ---
st.set_page_config(page_title="AI 탐색 기초 교육", layout="wide")

st.markdown("""
    <style>
    /* 전체 배경 스타일 */
    .main { background-color: #f8fafc; }
    
    /* 1. 상단 시뮬레이션 박스 (애니메이션 1.5초 유지) */
    .sim-container {
        background: linear-gradient(to bottom, #e2f5ff 0%, #ffffff 100%);
        height: 180px;
        border-radius: 12px;
        position: relative;
        overflow: hidden;
        border: 2px solid #cbd5e1;
        margin-bottom: 10px;
    }
    .land { background-color: #8be475; width: 140px; height: 60px; position: absolute; bottom: 0; border-top: 4px solid #65a30d; }
    .land-left { left: 0; border-radius: 0 12px 0 0; }
    .land-right { right: 0; border-radius: 12px 0 0 0; }
    .river { background-color: #38bdf8; height: 40px; position: absolute; bottom: 0; left: 140px; right: 140px; }
    .char { font-size: 28px; position: absolute; transition: all 1.5s ease-in-out; }
    .boat { font-size: 38px; position: absolute; bottom: 5px; transition: all 1.5s ease-in-out; }
    
    /* 2. 상태공간트리 전용 독립 스크롤 창 (핵심 요구사항) */
    .tree-scroll-container {
        background-color: #ffffff;
        border: 2px solid #6366f1;
        border-radius: 12px;
        height: 320px; /* 창 높이 고정 */
        overflow-y: auto; /* 세로 스크롤 활성화 */
        overflow-x: hidden;
        padding: 15px;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.06);
        margin-bottom: 15px;
    }
    
    /* 3. 직관적인 버튼 스타일 (늑대/양 등 명시) */
    .char-button {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 15px;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        background-color: white;
        cursor: pointer;
        transition: all 0.3s;
    }
    .char-button:hover {
        background-color: #f1f5f9;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .char-icon { font-size: 20px; }
    .char-label { font-weight: bold; margin-left: 10px; }
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
        ((next_f, w, s, c), "농부 혼자"),
        ((next_f, next_f, s, c), "농부 & 늑대"),
        ((next_f, w, next_f, c), "농부 & 양"),
        ((next_f, w, s, next_f), "농부 & 양배추")
    ]
    
    for state, label in all_moves:
        if label == "농부 & 늑대" and f != w: continue
        if label == "농부 & 양" and f != s: continue
        if label == "농부 & 양배추" and f != c: continue
        if len(st.session_state.history) > 1 and state == st.session_state.history[-2]: continue
        candidates.append((state, label))
    return candidates

def is_invalid(state):
    f, w, s, c = state
    if w == s and f != w: return True, "🐺 늑대가 🐑 양을 선택했습니다!"
    if s == c and f != s: return True, "🐑 양이 🥬 양배추를 선택했습니다!"
    return False, ""

# --- 3. 상단 레이아웃: 시뮬레이션 화면 ---
curr = st.session_state.history[-1]
f, w, s, c = curr

pos = lambda side, offset: f"{offset}px" if side == 'L' else f"calc(100% - {offset + 30}px)"
boat_pos = "22%" if f == 'L' else "68%"

st.markdown(f"""
    <div class="sim-container">
        <div class="land land-left"></div>
        <div class="land land-right"></div>
        <div class="river"></div>
        <div class="boat" style="left: {boat_pos};">🚣</div>
        <div class="char" style="left: {pos(f, 15)}; bottom: 50px;">👨‍🌾</div>
        <div class="char" style="left: {pos(w, 55)}; bottom: 15px;">🐺</div>
        <div class="char" style="left: {pos(s, 85)}; bottom: 15px;">🐑</div>
        <div class="char" style="left: {pos(c, 115)}; bottom: 15px;">🥬</div>
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

# --- 5. 하단 레이아웃: 트리 전용 스크롤 창 공간 ---
st.markdown("---")
st.write("🌲 **상태 공간 트리 (아래 전용 창에서 스크롤 하세요)**")

# 후보 노드 정보 가져오기
next_candidates = []
if not game_over and curr != ('R','R','R','R'):
    next_candidates = get_allowed_moves(curr)

# Graphviz 트리 노드 사이즈 극단적 축소 (Compact 디자인)
dot = graphviz.Digraph()
dot.attr(rankdir='TB', size='6,4!', ratio='fill') 
dot.attr('node', shape='circle', width='0.3', height='0.3', fixedsize='true', fontsize='9') # 지름 최소화

# 1) 히스토리 노드 생성
for i, state in enumerate(st.session_state.history):
    node_lbl = "".join(state)
    if i == len(st.session_state.history) - 1:
        # 현재 활성화된 최신 노드 (진한 파란 불빛)
        dot.node(f"h_{i}", node_lbl, style="filled", color="#1e40af", fillcolor="#3b82f6", fontcolor="white")
    else:
        # 이미 지나온 부모 노드 (차분한 회색)
        dot.node(f"h_{i}", node_lbl, style="filled", color="#94a3b8", fillcolor="#cbd5e1", fontcolor="#475569")
    if i > 0:
        dot.edge(f"h_{i-1}", f"h_{i}", color="#64748b", arrowsize='0.5')

# 2) 다음 후보 노드 생성 (연두색 점선 링크)
for idx, (cand_state, label_text) in enumerate(next_candidates):
    cand_lbl = "".join(cand_state)
    dot.node(f"c_{idx}", cand_lbl, style="filled", color="#16a34a", fillcolor="#bbf7d0", fontcolor="#166534")
    dot.edge(f"h_{len(st.session_state.history)-1}", f"c_{idx}", style="dashed", color="#22c55e", arrowsize='0.5')

# HTML 컨테이너 내부에 트리를 삽입하여 독립 스크롤 구현
# Streamlit에서 컴포넌트를 깔끔하게 가두기 위해 빈 수용 공간 정의 후 렌더링
with st.container():
    st.markdown('<div class="tree-scroll-container">', unsafe_allow_html=True)
    st.graphviz_chart(dot, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 6. 트리와 일치하는 직관적 노드 선택기 (늑대/양 등 명시) ---
if next_candidates:
    st.write("📍 **다음에 확장할 노드 단추를 누르세요:**")
    for idx, (cand_state, label_text) in enumerate(next_candidates):
        with st.container():
            # 트리의 초록색 자식 노드 순서와 완벽히 일치하는 버튼 인터페이스
            # 늑대/양 등의 아이콘과 레이블을 추가하여 직관성 향상
            with st.column(1, key=f"nd_{idx}"):
                if st.button(f"[{''.join(cand_state)}] {label_text}", key=f"btn_{idx}", use_container_width=True):
                    st.session_state.history.append(cand_state)
                    st.rerun()

                # 아이콘과 레이블을 추가하여 버튼의 직관성 향상
                icon = label_text.split(" ")[-1]
                if icon == "늑대":
                    st.write(f"🦊 {label_text}")
                elif icon == "양":
                    st.write(f"🐏 {label_text}")
                elif icon == "양배추":
                    st.write(f"🥬 {label_text}")
                else:
                    st.write(f"👨‍🌾 {label_text}")
