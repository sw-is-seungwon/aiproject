import streamlit as st
import graphviz

# --- 1. 기본 페이지 설정 및 사이드바 테마 적용 ---
st.set_page_config(page_title="AI 탐색 기초 교육", layout="wide")

with st.sidebar:
    st.header("🤖 AI 탐색 방식")
    search_mode = st.radio(
        "학습할 알고리즘을 선택하세요:",
        ["깊이 우선 탐색 (DFS)", "너비 우선 탐색 (BFS)"]
    )

st.markdown("""<style>
.main { background-color: #f8fafc; }
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
.char { position: absolute; transition: all 1.2s ease-in-out; }
.boat { position: absolute; bottom: 3px; transition: all 1.2s ease-in-out; }

.game-over-overlay {
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    background-color: rgba(239, 68, 68, 0.85);
    color: white;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    z-index: 10;
    font-weight: bold;
    animation: fadeIn 0.3s ease-in-out 1.2s forwards;
    opacity: 0;
}
.game-over-title { font-size: 32px; margin-bottom: 5px; animation: shake 0.5s infinite; }
.game-over-reason { font-size: 16px; opacity: 0.9; }
@keyframes fadeIn { to { opacity: 1; } }
@keyframes shake {
    0% { transform: translate(1px, 1px) rotate(0deg); }
    10% { transform: translate(-1px, -2px) rotate(-1deg); }
    20% { transform: translate(-3px, 0px) rotate(1deg); }
    30% { transform: translate(0px, 2px) rotate(0deg); }
    40% { transform: translate(1px, -1px) rotate(1deg); }
    50% { transform: translate(-1px, 2px) rotate(-1deg); }
    60% { transform: translate(-3px, 1px) rotate(0deg); }
    70% { transform: translate(2px, 1px) rotate(-1deg); }
    80% { transform: translate(-1px, -1px) rotate(1deg); }
    90% { transform: translate(2px, 2px) rotate(0deg); }
    100% { transform: translate(1px, -2px) rotate(-1deg); }
}
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
}
.timeline-box {
    background-color: #ffffff;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    display: flex;
    align-items: center;
    gap: 10px;
    overflow-x: auto;
    margin-top: 10px;
}
.timeline-node {
    background-color: #f1f5f9;
    padding: 6px 12px;
    border-radius: 12px;
    font-family: monospace;
    font-weight: bold;
    color: #334155;
    border: 1px solid #cbd5e1;
}
.timeline-node.active {
    background-color: #6366f1;
    color: #ffffff;
    border-color: #4f46e5;
}
</style>""", unsafe_allow_html=True)

# --- 2. 함수 선언 (이동 규칙 및 검증) ---
def get_allowed_moves(current_state, history_list):
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
        # 💡 핵심 교정: 농부(f)가 같이 타고 갈 대상과 '같은 강가'에 있는 상태여야만 합법적인 이동 후보가 됨
        if "🐺" in label and f != w: continue
        if "🐑" in label and f != s: continue
        if "🥬" in label and f != c: continue
        if len(history_list) > 1 and state == history_list[-2]: continue
        candidates.append((state, label))
    return candidates

def is_invalid(state):
    f, w, s, c = state
    if w == s and f != w: return True, "늑대가 양을 해쳤습니다! 🐺"
    if s == c and f != s: return True, "양이 양배추를 먹어치웠습니다! 🐑"
    return False, ""

# --- 3. 세션 상태 캐시 초기화 ---
if 'dfs_history' not in st.session_state:
    st.session_state.dfs_history = [('L','L','L','L')]
if 'bfs_history' not in st.session_state:
    st.session_state.bfs_history = [('L','L','L','L')]
if 'bfs_queue' not in st.session_state:
    st.session_state.bfs_queue = get_allowed_moves(('L','L','L','L'), [('L','L','L','L')])
if 'bfs_visited_candidates' not in st.session_state:
    st.session_state.bfs_visited_candidates = set()
if 'bfs_current_preview' not in st.session_state:
    st.session_state.bfs_current_preview = ('L','L','L','L')
if 'bfs_next_level_parent' not in st.session_state:
    st.session_state.bfs_next_level_parent = None
if 'last_toast' not in st.session_state:
    st.session_state.last_toast = None
if 'current_mode_track' not in st.session_state:
    st.session_state.current_mode_track = search_mode

# 사이드바 모드 전환 시 캐시 초기화
if st.session_state.current_mode_track != search_mode:
    st.session_state.current_mode_track = search_mode
    st.session_state.dfs_history = [('L','L','L','L')]
    st.session_state.bfs_history = [('L','L','L','L')]
    st.session_state.bfs_queue = get_allowed_moves(('L','L','L','L'), [('L','L','L','L')])
    st.session_state.bfs_visited_candidates = set()
    st.session_state.bfs_current_preview = ('L','L','L','L')
    st.session_state.bfs_next_level_parent = None
    st.session_state.last_toast = None
    st.rerun()

# 모드별 매핑
if search_mode == "깊이 우선 탐색 (DFS)":
    history = st.session_state.dfs_history
    curr = st.session_state.dfs_history[-1]
    next_candidates = get_allowed_moves(curr, st.session_state.dfs_history)
else:
    history = st.session_state.bfs_history
    curr = st.session_state.bfs_current_preview
    next_candidates = st.session_state.bfs_queue

game_over, reason = is_invalid(curr)

if game_over and st.session_state.last_toast != reason:
    st.toast(f"🚨 {reason}", icon="🔥")
    st.session_state.last_toast = reason

# --- 4. 메인 화면 및 상단 시뮬레이션 박스 렌더링 ---
st.title(f"✨ {search_mode} 시뮬레이터")

f, w, s, c = curr
pos = lambda side, offset: f"{offset}px" if side == 'L' else f"calc(100% - {offset + 25}px)"
boat_pos = "22%" if f == 'L' else "68%"

overlay_html = ""
if game_over:
    overlay_html = f'<div class="game-over-overlay"><div class="game-over-title">🚨 GAME OVER 🚨</div><div class="game-over-reason">{reason}</div></div>'

st.markdown(f"""<div class="sim-container">
    {overlay_html}
    <div class="land land-left"></div>
    <div class="land land-right"></div>
    <div class="river"></div>
    <div class="boat" style="left: {boat_pos}; font-size:34px;">🚣</div>
    <div class="char" style="left: {pos(f, 15)}; bottom: 45px; font-size:26px;">👨‍🌾</div>
    <div class="char" style="left: {pos(w, 50)}; bottom: 12px; font-size:26px;">🐺</div>
    <div class="char" style="left: {pos(s, 75)}; bottom: 12px; font-size:26px;">🐑</div>
    <div class="char" style="left: {pos(c, 100)}; bottom: 12px; font-size:26px;">🥬</div>
</div>""", unsafe_allow_html=True)

# --- 5. 상태 제어 및 롤백/리셋 장치 ---
if game_over:
    if search_mode == "너비 우선 탐색 (BFS)":
        st.warning("💡 BFS 모드 특성: 현재 분기는 실패 상태이지만, 형제 분기(너비)들이 열려 있습니다. 뒤로 가 다른 너비를 시도하세요.")
        if st.button("⏪ 이 분기 취소하고 다른 너비 탐색하기 (뒤로 가기)"):
            if len(st.session_state.bfs_history) > 1:
                st.session_state.bfs_history.pop()
                st.session_state.last_toast = None
                parent = st.session_state.bfs_history[-1]
                st.session_state.bfs_queue = get_allowed_moves(parent, st.session_state.bfs_history)
                st.session_state.bfs_visited_candidates = set()
                st.session_state.bfs_current_preview = parent
                st.session_state.bfs_next_level_parent = None
                st.rerun()
    else:
        if st.button("🔄 처음부터 다시 탐색 (DFS 리셋)"):
            st.session_state.dfs_history = [('L','L','L','L')]
            st.session_state.last_toast = None
            st.rerun()
            
elif curr == ('R','R','R','R'):
    st.balloons(); st.snow()
    st.success(f"🎉 **목표 상태 도달 성공!** {search_mode} 방식으로 안전하게 모두 이동시켰습니다.")
    
    st.write("📋 **강을 건넌 성공 이동 경로 기록:**")
    history_elements = []
    for state in history:
        state_str = "".join(state)
        is_last = (state == history[-1])
        active_class = "active" if is_last else ""
        history_elements.append(f'<div class="timeline-node {active_class}">{state_str}</div>')
    arrow_separator = ' <span style="font-weight:bold; color:gray;">➔</span> '
    st.markdown(f'<div class="timeline-box">{"".join([e + (arrow_separator if i < len(history_elements)-1 else "") for i, e in enumerate(history_elements)])}</div>', unsafe_allow_html=True)
    
    if st.button("🔄 전체 초기화 후 다시 하기"):
        st.session_state.dfs_history = [('L','L','L','L')]
        st.session_state.bfs_history = [('L','L','L','L')]
        st.session_state.bfs_queue = get_allowed_moves(('L','L','L','L'), [('L','L','L','L')])
        st.session_state.bfs_visited_candidates = set()
        st.session_state.bfs_current_preview = ('L','L','L','L')
        st.session_state.bfs_next_level_parent = None
        st.session_state.last_toast = None
        st.rerun()

else:
    if search_mode == "너비 우선 탐색 (BFS)":
        all_visited = len(st.session_state.bfs_visited_candidates) == len(st.session_state.bfs_queue)
        if all_visited:
            st.success("✅ **현재 깊이(Level)의 모든 너비 노드를 확인했습니다!**")
            if st.session_state.bfs_next_level_parent is not None:
                if st.button("🔽 안전한 다음 단계(Level) 노드로 탐색 확장하기", type="primary"):
                    next_parent = st.session_state.bfs_next_level_parent
                    st.session_state.bfs_history.append(next_parent)
                    st.session_state.bfs_queue = get_allowed_moves(next_parent, st.session_state.bfs_history)
                    st.session_state.bfs_visited_candidates = set()
                    st.session_state.bfs_current_preview = next_parent
                    st.session_state.bfs_next_level_parent = None
                    st.rerun()
            else:
                st.error("❌ 현재 레벨의 모든 너비 분기가 실패 상태입니다! 나아갈 수 있는 곳이 없습니다.")
                if st.button("⏪ 한 단계 위 부모 노드로 롤백"):
                    if len(st.session_state.bfs_history) > 1:
                        st.session_state.bfs_history.pop()
                        parent = st.session_state.bfs_history[-1]
                        st.session_state.bfs_queue = get_allowed_moves(parent, st.session_state.bfs_history)
                        st.session_state.bfs_visited_candidates = set()
                        st.session_state.bfs_current_preview = parent
                        st.session_state.bfs_next_level_parent = None
                        st.rerun()

# --- 6. 하단 레이아웃: 상태 공간 트리 그래프 빌드 ---
st.markdown("---")
st.write("🌲 **상태 공간 트리 (현재 레벨의 너비 탐색 진척도가 반영됩니다)**")

dot = graphviz.Digraph()
dot.attr(rankdir='TB', size='6,4!', ratio='fill')
dot.attr('node', shape='box', style='filled,rounded', width='1.4', height='0.4', fixedsize='true', fontsize='10', fontname="Arial")

if search_mode == "깊이 우선 탐색 (DFS)":
    for i, state in enumerate(st.session_state.dfs_history):
        node_lbl = "".join(state)
        if i == len(st.session_state.dfs_history) - 1:
            dot.node(f"h_{i}", node_lbl, color="#4f46e5", fillcolor="#6366f1", fontcolor="white", penwidth="2")
        else:
            dot.node(f"h_{i}", node_lbl, color="#cbd5e1", fillcolor="#f1f5f9", fontcolor="#64748b")
        if i > 0: dot.edge(f"h_{i-1}", f"h_{i}", color="#94a3b8", arrowsize='0.6')
else:
    for i, state in enumerate(st.session_state.bfs_history):
        node_lbl = "".join(state)
        dot.node(f"h_{i}", node_lbl, color="#cbd5e1", fillcolor="#f1f5f9", fontcolor="#64748b")
        if i > 0: dot.edge(f"h_{i-1}", f"h_{i}", color="#94a3b8", arrowsize='0.6')

for idx, (cand_state, label_text) in enumerate(next_candidates):
    cand_lbl = "".join(cand_state)
    is_previewed = (search_mode == "너비 우선 탐색 (BFS)" and cand_state == st.session_state.bfs_current_preview)
    is_visited = (search_mode == "너비 우선 탐색 (BFS)" and cand_state in st.session_state.bfs_visited_candidates)
    is_cand_invalid, _ = is_invalid(cand_state)
    
    if is_previewed:
        dot.node(f"c_{idx}", cand_lbl, color="#4f46e5", fillcolor="#818cf8", fontcolor="white")
    elif is_visited and is_cand_invalid:
         dot.node(f"c_{idx}", cand_lbl, color="#ef4444", fillcolor="#fee2e2", fontcolor="#991b1b")
    elif is_visited:
         dot.node(f"c_{idx}", cand_lbl, color="#10b981", fillcolor="#d1fae5", fontcolor="#065f46")
    else:
         dot.node(f"c_{idx}", cand_lbl, color="#94a3b8", fillcolor="#ffffff", fontcolor="#64748b")
         
    parent_idx = len(st.session_state.dfs_history)-1 if search_mode == "깊이 우선 탐색 (DFS)" else len(st.session_state.bfs_history)-1
    dot.edge(f"h_{parent_idx}", f"c_{idx}", style="dashed", color="#94a3b8", arrowsize='0.6')

svg_data = dot.pipe(format='svg').decode('utf-8')

scrollable_html = f"""<div id="scroll-container" style="border: 2px solid #e2e8f0; border-radius: 12px; height: 260px; overflow-y: auto; overflow-x: hidden; padding: 10px; background-color: white; display: flex; justify-content: center;">
    <div>{svg_data}</div>
</div>
<script>
    function scrollToBottom() {{
        var container = document.getElementById("scroll-container");
        if(container) {{
            container.scrollTop = container.scrollHeight;
        }}
    }}
    window.onload = function() {{
        setTimeout(scrollToBottom, 50);
    }};
</script>"""
st.components.v1.html(scrollable_html, height=280)

# --- 7. 하단 선택 버튼 컨트롤러 ---
if next_candidates and not (search_mode == "너비 우선 탐색 (BFS)" and len(st.session_state.bfs_visited_candidates) == len(st.session_state.bfs_queue)):
    if search_mode == "깊이 우선 탐색 (DFS)":
        st.write("📍 **다음에 깊게 탐색할 대상을 선택하세요:**")
    else:
        st.write("📍 **이번 깊이(Level)에서 검사할 너비 노드들을 하나씩 모두 확인해 보세요:**")
        
    cols = st.columns(len(next_candidates))
    for idx, (cand_state, label_text) in enumerate(next_candidates):
        with cols[idx]:
            btn_label = label_text
            if search_mode == "너비 우선 탐색 (BFS)" and cand_state in st.session_state.bfs_visited_candidates:
                is_cand_fail, _ = is_invalid(cand_state)
                btn_label += " ❌ (확인됨)" if is_cand_fail else " ✔️ (안전)"
                
            if st.button(btn_label, key=f"action_btn_{idx}", use_container_width=True):
                if search_mode == "깊이 우선 탐색 (DFS)":
                    st.session_state.dfs_history.append(cand_state)
                else:
                    st.session_state.bfs_current_preview = cand_state
                    st.session_state.bfs_visited_candidates.add(cand_state)
                    is_cand_fail, _ = is_invalid(cand_state)
                    if not is_cand_fail:
                        st.session_state.bfs_next_level_parent = cand_state
                st.rerun()
elif not game_over and curr != ('R','R','R','R') and search_mode == "깊이 우선 탐색 (DFS)":
    st.warning("⚠️ **더 이상 이동할 수 있는 경로가 없습니다! (막다른 길)**")
    if st.button("⏪ 한 단계 뒤로 가기"):
        if len(st.session_state.dfs_history) > 1:
            st.session_state.dfs_history.pop()
        st.rerun()
