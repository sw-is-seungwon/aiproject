import streamlit as st
import graphviz

# --- 1. 페이지 설정 및 디자인 CSS 주입 ---
st.set_page_config(page_title="무정보 탐색 기법 시뮬레이션", layout="wide")

with st.sidebar:
    st.header("🤖 AI 탐색 방식")
    search_mode = st.radio(
        "학습할 알고리즘을 선택하세요:",
        ["깊이 우선 탐색 (DFS)", "너비 우선 탐색 (BFS)"]
    )

st.markdown("""<style>
.main { background-color: #fdfbf7; }

/* 시뮬레이션 박스를 부드러운 파스텔 그라데이션으로 */
.sim-container {
    background: linear-gradient(to bottom, #fff1f2 0%, #f0fdfa 100%);
    height: 160px;
    border-radius: 24px;
    position: relative;
    overflow: hidden;
    border: 2px dashed #fbcfe8;
    margin-bottom: 15px;
    box-shadow: 0 8px 16px -2px rgba(251, 207, 232, 0.25);
}

/* 밀크 파스텔톤의 땅과 강물 색상 */
.land { background-color: #e2f9b8; width: 150px; height: 50px; position: absolute; bottom: 0; border-top: 4px solid #a3e635; }
.land-left { left: 0; border-radius: 0 24px 0 0; }
.land-right { right: 0; border-radius: 24px 0 0 0; }
.river { background-color: #bae6fd; height: 35px; position: absolute; bottom: 0; left: 150px; right: 150px; border-top: 2px dashed #7dd3fc; }

.char { position: absolute; transition: all 1.2s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
.boat { position: absolute; bottom: 3px; transition: all 1.2s cubic-bezier(0.175, 0.885, 0.32, 1.275); }

.game-over-overlay {
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    background-color: rgba(254, 226, 226, 0.9);
    color: #be123c;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    z-index: 10;
    font-weight: bold;
    animation: fadeIn 0.3s ease-in-out 1.2s forwards;
    opacity: 0;
}
@keyframes fadeIn { to { opacity: 1; } }

/* 말랑말랑 마카롱 느낌의 둥근 파스텔 버튼 */
div.stButton > button {
    border-radius: 30px !important;
    border: 2px solid #fbcfe8 !important;
    background-color: #ffffff !important;
    color: #db2777 !important;
    font-weight: 700 !important;
    padding: 10px 20px !important;
    box-shadow: 0 4px 6px rgba(251, 207, 232, 0.3) !important;
    transition: all 0.25s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
}
div.stButton > button:hover {
    border-color: #f472b6 !important;
    background-color: #fdf2f8 !important;
    color: #be123c !important;
    transform: scale(1.03);
}

.timeline-box {
    background-color: #fff9fa;
    padding: 15px;
    border-radius: 20px;
    border: 2px dashed #fbcfe8;
    display: flex;
    align-items: center;
    gap: 10px;
    overflow-x: auto;
}
.timeline-node {
    background-color: #f1f5f9;
    padding: 6px 12px;
    border-radius: 14px;
    font-family: monospace;
    font-weight: bold;
    color: #334155;
    border: 1px solid #cbd5e1;
}
.timeline-node.active {
    background-color: #f472b6;
    color: #ffffff;
    border-color: #db2777;
}
</style>""", unsafe_allow_html=True)

# --- 2. 이동 제한 규칙 및 상태 검증 함수 ---
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
        if "🐺" in label and f != w: continue
        if "🐑" in label and f != s: continue
        if "🥬" in label and f != c: continue
        if len(history_list) > 1 and state == history_list[-2]: continue
        candidates.append((state, label))
    return candidates

def is_invalid(state):
    f, w, s, c = state
    if w == s and f != w: return True, "농부가 없는 사이 늑대가 양을 공격했습니다! 🐺"
    if s == c and f != s: return True, "농부가 없는 사이 양이 양배추를 먹어치웠습니다! 🐑"
    return False, ""

# --- 3. 세션 상태 분리 및 초기화 ---
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
if 'current_mode_track' not in st.session_state:
    st.session_state.current_mode_track = search_mode

# 사이드바 모드 교체 시 완벽 리셋
if st.session_state.current_mode_track != search_mode:
    st.session_state.current_mode_track = search_mode
    st.session_state.dfs_history = [('L','L','L','L')]
    st.session_state.bfs_history = [('L','L','L','L')]
    st.session_state.bfs_queue = get_allowed_moves(('L','L','L','L'), [('L','L','L','L')])
    st.session_state.bfs_visited_candidates = set()
    st.session_state.bfs_current_preview = ('L','L','L','L')
    st.session_state.bfs_next_level_parent = None
    st.rerun()

# 작동 모드 데이터 매핑
if search_mode == "깊이 우선 탐색 (DFS)":
    history = st.session_state.dfs_history
    curr = st.session_state.dfs_history[-1]
    next_candidates = get_allowed_moves(curr, st.session_state.dfs_history)
else:
    history = st.session_state.bfs_history
    curr = st.session_state.bfs_current_preview
    next_candidates = st.session_state.bfs_queue

game_over, reason = is_invalid(curr)

if game_over:
    st.toast(f"🚨 {reason}", icon="🔥")

# --- 4. 상단 레이아웃: 시뮬레이션 인터페이스 ---
st.title(f"✨ {search_mode} 시뮬레이터")

f, w, s, c = curr
pos = lambda side, offset: f"{offset}px" if side == 'L' else f"calc(100% - {offset + 25}px)"
boat_pos = "22%" if f == 'L' else "68%"

overlay_html = ""
if game_over:
    overlay_html = f'<div class="game-over-overlay"><div style="font-size:32px;">🚨 GAME OVER 🚨</div></div>'

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

# --- 5. 상태 제어 및 리셋부 ---
col_info, _ = st.columns([3, 1])
with col_info:
    if game_over and search_mode == "깊이 우선 탐색 (DFS)":
        if st.button("🔄 처음부터 다시 탐색 (DFS 리셋)"):
            st.session_state.dfs_history = [('L','L','L','L')]
            st.rerun()
                
    elif curr == ('R','R','R','R'):
        st.success(f"🎉 **목표 상태 도달 성공!** {search_mode} 방식으로 안전하게 탐색을 완료했습니다.")
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
            st.rerun()

    else:
        if search_mode == "너비 우선 탐색 (BFS)":
            all_visited = len(st.session_state.bfs_visited_candidates) == len(st.session_state.bfs_queue)
            if all_visited:
                st.success("✅ **현재 깊이(Level)의 모든 너비 분기 탐색 완료!**")
                if st.session_state.bfs_next_level_parent is not None:
                    if st.button("🔽 안전함이 확인된 다음 깊이(Level)로 트리 확장하기", type="primary"):
                        next_parent = st.session_state.bfs_next_level_parent
                        st.session_state.bfs_history.append(next_parent)
                        st.session_state.bfs_queue = get_allowed_moves(next_parent, st.session_state.bfs_history)
                        st.session_state.bfs_visited_candidates = set()
                        st.session_state.bfs_current_preview = next_parent
                        st.session_state.bfs_next_level_parent = None
                        st.rerun()
                else:
                    st.error("❌ 현재 깊이의 모든 너비 분기가 실패 구역입니다. 이전 레벨의 다른 안전했던 분기로 우회해야 합니다.")
                    if st.button("⏪ 안전했던 상위 레벨 부모 노드로 롤백"):
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
st.write("🌲 **상태 공간 트리**")

dot = graphviz.Digraph()
dot.attr(rankdir='TB', size='6,4!', ratio='fill')
dot.attr('node', shape='box', style='filled,rounded', width='1.4', height='0.4', fixedsize='true', fontsize='10', fontname="Arial", color="#fbcfe8", penwidth="2")

if search_mode == "깊이 우선 탐색 (DFS)":
    for i, state in enumerate(st.session_state.dfs_history):
        node_lbl = "".join(state)
        if i == len(st.session_state.dfs_history) - 1:
            dot.node(f"h_{i}", node_lbl, color="#db2777", fillcolor="#f472b6", fontcolor="white", penwidth="2")
        else:
            dot.node(f"h_{i}", node_lbl, color="#fbcfe8", fillcolor="#fff1f2", fontcolor="#db2777")
        if i > 0: dot.edge(f"h_{i-1}", f"h_{i}", color="#f472b6", arrowsize='0.6', penwidth="2")
else:
    for i, state in enumerate(st.session_state.bfs_history):
        node_lbl = "".join(state)
        dot.node(f"h_{i}", node_lbl, color="#fbcfe8", fillcolor="#fff1f2", fontcolor="#db2777")
        if i > 0: dot.edge(f"h_{i-1}", f"h_{i}", color="#f472b6", arrowsize='0.6', penwidth="2")

for idx, (cand_state, label_text) in enumerate(next_candidates):
    cand_lbl = "".join(cand_state)
    is_previewed = (search_mode == "너비 우선 탐색 (BFS)" and cand_state == st.session_state.bfs_current_preview)
    is_visited = (search_mode == "너비 우선 탐색 (BFS)" and cand_state in st.session_state.bfs_visited_candidates)
    is_cand_invalid, _ = is_invalid(cand_state)
    
    if is_previewed:
        dot.node(f"c_{idx}", cand_lbl, color="#ca8a04", fillcolor="#fef08a", fontcolor="#854d0e")
    elif is_visited and is_cand_invalid:
         dot.node(f"c_{idx}", cand_lbl, color="#dc2626", fillcolor="#fee2e2", fontcolor="#991b1b")
    elif is_visited:
         dot.node(f"c_{idx}", cand_lbl, color="#16a34a", fillcolor="#dcfce7", fontcolor="#14532d")
    else:
         dot.node(f"c_{idx}", cand_lbl, color="#cbd5e1", fillcolor="#ffffff", fontcolor="#64748b")
         
    parent_idx = len(st.session_state.dfs_history)-1 if search_mode == "깊이 우선 탐색 (DFS)" else len(st.session_state.bfs_history)-1
    dot.edge(f"h_{parent_idx}", f"c_{idx}", style="dashed", color="#fbcfe8", arrowsize='0.6', penwidth="1.5")

svg_data = dot.pipe(format='svg').decode('utf-8')

scrollable_html = f"""<div id="scroll-container" style="border: 2px dashed #fbcfe8; border-radius: 20px; height: 260px; overflow-y: auto; overflow-x: hidden; padding: 10px; background-color: white; display: flex; justify-content: center;">
    <div>{svg_data}</div>
</div>
<script>
    function scrollToBottom() {{
        var container = document.getElementById("scroll-container");
        if(container) {{ container.scrollTop = container.scrollHeight; }}
    }}
    window.onload = function() {{ setTimeout(scrollToBottom, 50); }};
</script>"""
st.components.v1.html(scrollable_html, height=280)

# --- 7. 하단 탐색 제어 선택 버튼부 ---
should_show_buttons = False
if search_mode == "깊이 우선 탐색 (DFS)" and not game_over and curr != ('R','R','R','R'):
    should_show_buttons = True
elif search_mode == "너비 우선 탐색 (BFS)" and curr != ('R','R','R','R'):
    should_show_buttons = True

if next_candidates and should_show_buttons:
    if search_mode == "깊이 우선 탐색 (DFS)":
        st.write("📍 **다음에 깊게 탐색할 대상을 선택하세요:**")
        cols = st.columns(len(next_candidates))
        for idx, (cand_state, label_text) in enumerate(next_candidates):
            with cols[idx]:
                if st.button(label_text, key=f"action_btn_{idx}", use_container_width=True):
                    st.session_state.dfs_history.append(cand_state)
                    st.rerun()
    else:
        if len(st.session_state.bfs_visited_candidates) < len(st.session_state.bfs_queue):
            st.write("📍 **이번 깊이(Level)에서 검사할 너비 노드들을 하나씩 모두 확인해 보세요:**")
            cols = st.columns(len(next_candidates))
            for idx, (cand_state, label_text) in enumerate(next_candidates):
                with cols[idx]:
                    btn_label = label_text
                    if cand_state in st.session_state.bfs_visited_candidates:
                        is_cand_fail, _ = is_invalid(cand_state)
                        btn_label += " ❌ (실패)" if is_cand_fail else " ✔️ (안전)"
                        
                    if st.button(btn_label, key=f"action_btn_{idx}", use_container_width=True):
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
