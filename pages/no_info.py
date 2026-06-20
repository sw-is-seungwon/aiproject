import streamlit as st
import graphviz

# --- 1. 기본 설정 및 애니메이션 스타일 ---
st.set_page_config(page_title="AI 탐색 기초 교육", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    
    /* 교과서 스타일의 시뮬레이션 박스 (애니메이션 속도 1.5초로 완화) */
    .sim-container {
        background: linear-gradient(to bottom, #e2f5ff 0%, #ffffff 100%);
        height: 220px;
        border-radius: 16px;
        position: relative;
        overflow: hidden;
        border: 2px solid #cbd5e1;
        margin-bottom: 10px;
    }
    .land { background-color: #8be475; width: 160px; height: 70px; position: absolute; bottom: 0; border-top: 4px solid #65a30d; }
    .land-left { left: 0; border-radius: 0 16px 0 0; }
    .land-right { right: 0; border-radius: 16px 0 0 0; }
    .river { background-color: #38bdf8; height: 50px; position: absolute; bottom: 0; left: 160px; right: 160px; }
    
    /* 캐릭터 및 배 이동 (1.5초 서서히 이동) */
    .char { font-size: 32px; position: absolute; transition: all 1.5s ease-in-out; }
    .boat { font-size: 42px; position: absolute; bottom: 10px; transition: all 1.5s ease-in-out; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 게임 로직 및 세션 상태 초기화 ---
if 'history' not in st.session_state:
    st.session_state.history = [('L','L','L','L')] # (농부, 늑대, 양, 양배추)
if 'search_mode' not in st.session_state:
    st.session_state.search_mode = "깊이 우선 탐색 (DFS)"

def get_allowed_moves(current_state):
    f, w, s, c = current_state
    next_f = 'R' if f == 'L' else 'L'
    candidates = []
    
    # 가능한 이동 정의
    all_moves = [
        ((next_f, w, s, c), "농부 혼자"),
        ((next_f, next_f, s, c), "농부 & 늑대"),
        ((next_f, w, next_f, c), "농부 & 양"),
        ((next_f, w, s, next_f), "농부 & 양배추")
    ]
    
    for state, label in all_moves:
        # 조건 1: 배에 같이 탈 수 있는 조건인지 (농부와 같은 위치에 있었는지)
        if label == "농부 & 늑대" and f != w: continue
        if label == "농부 & 양" and f != s: continue
        if label == "농부 & 양배추" and f != c: continue
        
        # 조건 2: 방금 전 단계로 되돌아가는 중복 이동 방지 (요구사항 반영)
        if len(st.session_state.history) > 1:
            if state == st.session_state.history[-2]:
                continue
                
        candidates.append((state, label))
    return candidates

def is_invalid(state):
    f, w, s, c = state
    if w == s and f != w: return True, "🐺 늑대가 🐑 양을 잡아먹었습니다!"
    if s == c and f != s: return True, "🐑 양이 🥬 양배추를 먹어치웠습니다!"
    return False, ""

# --- 3. 상단: 실시간 그래픽 시뮬레이션 (천천히 이동) ---
curr = st.session_state.history[-1]
f, w, s, c = curr

# 이모지 위치 계산 토글
pos = lambda side, offset: f"{offset}px" if side == 'L' else f"calc(100% - {offset + 35}px)"
boat_pos = "25%" if f == 'L' else "65%"

st.markdown(f"""
    <div class="sim-container">
        <div class="land land-left"></div>
        <div class="land land-right"></div>
        <div class="river"></div>
        <div class="boat" style="left: {boat_pos};">🚣</div>
        <div class="char" style="left: {pos(f, 20)}; bottom: 60px;">👨‍🌾</div>
        <div class="char" style="left: {pos(w, 65)}; bottom: 25px;">🐺</div>
        <div class="char" style="left: {pos(s, 100)}; bottom: 25px;">🐑</div>
        <div class="char" style="left: {pos(c, 135)}; bottom: 25px;">🥬</div>
    </div>
""", unsafe_allow_html=True)

# --- 4. 중단: 규칙 및 탐색 제어판 ---
col_info, col_ctrl = st.columns([3, 1])

with col_ctrl:
    mode = st.radio("🔍 탐색 알고리즘 선택", ["깊이 우선 탐색 (DFS)", "너비 우선 탐색 (BFS)"])
    if mode != st.session_state.search_mode:
        st.session_state.search_mode = mode
        st.session_state.history = [('L','L','L','L')]
        st.rerun()

with col_info:
    game_over, reason = is_invalid(curr)
    if game_over:
        st.error(f"🚨 **금지 상태 도달 (게임 오버):** {reason}")
        if st.button("🔄 처음부터 다시 탐색하기", use_container_width=True):
            st.session_state.history = [('L','L','L','L')]
            st.rerun()
    elif curr == ('R','R','R','R'):
        st.balloons()
        st.success("🎉 **목표 상태 도달!** 모든 물품을 안전하게 이동시켰습니다.")
        if st.button("🔄 다시 도전하기", use_container_width=True):
            st.session_state.history = [('L','L','L','L')]
            st.rerun()
    else:
        st.info(f"💡 현재 탐색 기법: **{st.session_state.search_mode}** | 아래 트리에서 다음에 확장할 노드를 클릭하세요.")

# --- 5. 하단: 세로형 상태 공간 트리 및 직접 선택 기능 ---
st.markdown("---")
st.subheader("🌲 아래로 이어나가는 상태 공간 트리 (State Space Tree)")

# 현재 상태에서 갈 수 있는 다음 후보 노드들 확보
next_candidates = []
if not game_over and curr != ('R','R','R','R'):
    next_candidates = get_allowed_moves(curr)

# Graphviz 트리 시각화 생성
dot = graphviz.Digraph()
dot.attr(rankdir='TB', size='8,6!') # 위에서 아래로(TB) 정렬, 컴팩트한 노드 사이즈

# 1) 이미 선택해서 지나온 노드들 그리기
for i, state in enumerate(st.session_state.history):
    label = f"단계 {i}\n[{''.join(state)}]"
    
    # 불빛 효과 다르게 주기: 현재 맨 마지막 활성 노드는 '강렬한 파란색', 이전 노드는 '차분한 회색'
    if i == len(st.session_state.history) - 1:
        dot.node(f"hist_{i}", label, shape="circle", style="filled", color="#1e40af", fillcolor="#3b82f6", fontcolor="white", penwidth="3")
    else:
        dot.node(f"hist_{i}", label, shape="circle", style="filled", color="#94a3b8", fillcolor="#cbd5e1", fontcolor="#475569")
        
    if i > 0:
        dot.edge(f"hist_{i-1}", f"hist_{i}", color="#64748b", penwidth="2")

# 2) 현재 노드 바로 밑에 선택 가능한 자식 노드(미리보기) 그리기
current_idx = len(st.session_state.history) - 1
for idx, (cand_state, label_text) in enumerate(next_candidates):
    cand_id = f"cand_{idx}"
    cand_label = f"{label_text}\n[{''.join(cand_state)}]"
    
    # 아직 선택되지 않은 자식 노드는 '연두색 불빛'으로 하이라이트하여 선택 가능함을 명시
    dot.node(cand_id, cand_label, shape="circle", style="filled", color="#16a34a", fillcolor="#bbf7d0", fontcolor="#166534")
    dot.edge(f"hist_{current_idx}", cand_id, style="dashed", color="#22c55e")

# 트리 화면에 렌더링
st.graphviz_chart(dot, use_container_width=True)

# 3) 트리 밑에 학생들이 노드를 즉시 선택할 수 있도록 트리 매핑 버튼 배치
if next_candidates:
    st.write("📍 **확장할 노드를 선택하세요:**")
    cols = st.columns(len(next_candidates))
    for idx, (cand_state, label_text) in enumerate(next_candidates):
        with cols[idx]:
            # 트리에 그려진 연두색 노드와 매칭되는 선택 버튼
            if st.button(f"🟢 {label_text} [{''.join(cand_state)}]", key=f"select_{idx}", use_container_width=True):
                st.session_state.history.append(cand_state)
                st.rerun()

# 자동으로 최신 상태 레이아웃 유지 유도
st.markdown("<script>window.scrollTo(0, 0);</script>", unsafe_allow_html=True)
