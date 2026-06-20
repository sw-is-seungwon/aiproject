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

# 💡 CSS 주입: 이모지 이동 속도를 1.2초로 빠르게 조정
st.html("""<style>
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

/* 1. 답답하지 않게 딜레이 타임 1.2초로 감소 최적화 */
.char { position: absolute; transition: all 1.2s ease-in-out; }
.boat { position: absolute; bottom: 3px; transition: all 1.2s ease-in-out; }

/* 2. 이동 직후(1.2초) 곧바로 오버레이가 스르륵 뜨도록 변경 */
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

# --- 3. 세션 상태 및 변수 초기화 ---
if 'dfs_history' not in st.session_state:
    st.session_state.dfs_history = [('L','L','L','L')]

# 💡 BFS용 구조 개편: 현재 깊이의 '큐(너비 노드들)', '현재 임시 미리보기 상태', '방문 완료 기록'을 추적
if 'bfs_history' not in st.session_state:
    st.session_state.bfs_history = [('L','L','L','L')]
if 'bfs_queue' not in st.session_state:
    # 최초 LLLL에서 갈 수 있는 너비 분기들을 큐로 초기화
    st.session_state.bfs_queue = get_allowed_moves(('L','L','L','L'), [('L','L','L','L')])
if 'bfs_visited_candidates' not in st.session_state:
    st.session_state.bfs_visited_candidates = set() # 이번 깊이에서 클릭해 본 노드들
if 'bfs_current_preview' not in st.session_state:
    st.session_state.bfs_current_preview = ('L','L','L','L') # 시뮬레이션에 띄워줄 임시 노드 상태
if 'bfs_next_level_parent' not in st.session_state:
    st.session_state.bfs_next_level_parent = None # 다음 깊이로 넘어갈 때 부모가 될 합격 노드 저장

if 'last_toast' not in st.session_state:
    st.session_state.last_toast = None

# --- 4. 데이터 맵핑 및 분기 설정 ---
if search_mode == "깊이 우선 탐색 (DFS)":
    curr = st.session_state.dfs_history[-1]
    next_candidates = get_allowed_moves(curr, st.session_state.dfs_history)
else:
    # BFS 일 때는 사용자가 눌러서 "확인 중인 분기 노드"를 시뮬레이션에 노출
    curr = st.session_state.bfs_current_preview
    next_candidates = st.session_state.bfs_queue

game_over, reason = is_invalid(curr)

if game_over and st.session_state.last_toast != reason:
    st.toast(f"🚨 {reason}", icon="🔥")
    st.session_state.last_toast = reason

# --- 5. 메인 화면 타이틀 및 상단 시뮬레이션 박스 ---
st.title(f"✨ {search_mode} 시뮬레이터")

f, w, s, c = curr
pos = lambda side, offset: f"{offset}px" if side == 'L' else f"calc(100% - {offset + 25}px)"
boat_pos = "22%" if f == 'L' else "68%"

overlay_html = ""
if game_over:
    overlay_html = f'<div class="game-over-overlay"><div class="game-over-title">🚨 GAME OVER 🚨</div><div class="game-over-reason">{reason}</div></div>'

st.html(f"""<div class="sim-container">
    {overlay_html}
    <div class="land land-left"></div>
    <div class="land land-right"></div>
    <div class="river"></div>
    <div class="boat" style="left: {boat_pos}; font-size:34px;">🚣</div>
    <div class="char" style="left: {pos(f, 15)}; bottom: 45px; font-size:26px;">👨‍🌾</div>
    <div class="char" style="left: {pos(w, 50)}; bottom: 12px; font-size:26px;">🐺</div>
    <div class="char" style="left: {pos(s, 75)}; bottom: 12px; font-size:26px;">🐑</div>
    <div class="char" style="left: {pos(c, 100)}; bottom: 12px; font-size:26px;">🥬</div>
</div>""")

# --- 6. 탐색 알고리즘 제어부 (DFS / BFS) ---
if search_mode == "깊이 우선 탐색 (DFS)":
    if game_over:
        if st.button("🔄 처음부터 다시 탐색 (DFS 리셋)"):
            st.session_state.dfs_history = [('L','L','L','L')]
            st.session_state.last_toast = None
            st.rerun()
    elif curr == ('R','R','R','R'):
        st.balloons(); st.snow()
        st.success("🎉 **목표 상태 도달 성공!** DFS 방식으로 해를 찾았습니다.")
        st.write("📋 **이동 경로 기록:**")
        history_elements = [f'<div class="timeline-node">{"".join(state)}</div>' for state in st.session_state.dfs_history]
        st.html(f'<div class="timeline-box">{"➔".join(history_elements)}</div>')
        if st.button("🔄 게임 초기화"):
            st.session_state.dfs_history = [('L','L','L','L')]
            st.rerun()

else:
    # 🌳 BFS 제어 시스템
    if curr == ('R','R','R','R'):
        st.balloons(); st.snow()
        st.success("🎉 **최적의 정답 상태(RRRR) 발견 완료!** BFS 탐색에 성공했습니다.")
        st.write("📋 **최종 매핑된 합격 경로 이력:**")
        history_elements = [f'<div class="timeline-node">{"".join(state)}</div>' for state in st.session_state.bfs_history]
        st.html(f'<div class="timeline-box">{"➔".join(history_elements)}</div>')
        if st.button("🔄 전체 리셋 후 다시 하기"):
            st.session_state.bfs_history = [('L','L','L','L')]
            st.session_state.bfs_queue = get_allowed_moves(('L','L','L','L'), [('L','L','L','L')])
            st.session_state.bfs_visited_candidates = set()
            st.session_state.bfs_current_preview = ('L','L','L','L')
            st.session_state.bfs_next_level_parent = None
            st.rerun()
    else:
        # 💡 핵심 가이드: 현재 레벨의 모든 너비 경우의 수를 눌렀는지 판단
        all_visited = len(st.session_state.bfs_visited_candidates) == len(st.session_state.bfs_queue)
        
        if all_visited:
            st.success("✅ **현재 깊이(Level)의 모든 너비 노드를 확인했습니다!**")
            if st.session_state.bfs_next_level_parent is not None:
                if st.button("🔽 안전한 다음 단계(Level) 노드로 탐색 확장하기", type="primary"):
                    # 다음 단계로 히스토리를 갱신하고 새 큐(Queue) 생성
                    next_parent = st.session_state.bfs_next_level_parent
                    st.session_state.bfs_history.append(next_parent)
                    st.session_state.bfs_queue = get_allowed_moves(next_parent, st.session_state.bfs_history)
                    st.session_state.bfs_visited_candidates = set()
                    st.session_state.bfs_current_preview = next_parent
                    st.session_state.bfs_next_level_parent = None
                    st.rerun()
            else:
                st.error("❌ 현재 레벨의 모든 너비 분기가 실패 상태(Game over)입니다! 더 나아갈 수 없습니다.")
                if st.button("⏪ 한 단계 위 부모 노드로 롤백"):
                    if len(st.session_state.bfs_history) > 1:
                        st.session_state.bfs_history.pop()
                        parent = st.session_state.bfs_history[-1]
                        st.session_state.bfs_queue = get_allowed_moves(parent, st.session_state.bfs_history)
                        st.session_state.bfs_visited_candidates = set()
                        st.session_state.bfs_current_preview = parent
                        st.session_state.bfs_next_level_parent = None
                        st.rerun()

# --- 7. 하단 레이아웃: 트리 구조 시각화 ---
st.markdown("---")
st.write("🌲 **상태 공간 트리 (현재 레벨의 너비 탐색 진척도가 반영됩니다)**")

dot = graphviz.Digraph()
dot.attr(rankdir='TB', size='6,4!', ratio='fill')
dot.attr('node', shape='box', style='filled,rounded', width='1.0', height='0.4', fixedsize='false', fontsize='12', fontname="Arial")

if search_mode == "깊이 우선 탐색 (DFS)":
    for i, state in enumerate(st.session_state.dfs_history):
        node_lbl = " - ".join(state)
        if i == len(st.session_state.dfs_history) - 1:
            dot.node(f"h_{i}", node_lbl, color="#4f46e5", fillcolor="#6366f1", fontcolor="white", penwidth="2")
        else:
            dot.node(f"h_{i}", node_lbl, color="#cbd5e1", fillcolor="#f1f5f9", fontcolor="#64748b")
        if i > 0: dot.edge(f"h_{i-1}", f"h_{i}", color="#94a3b8", arrowsize='0.6')
else:
    # BFS 트리 시각화
    for i, state in enumerate(st.session_state.bfs_history):
        node_lbl = " - ".join(state)
        dot.node(f"h_{i}", node_lbl, color="#cbd5e1", fillcolor="#f1f5f9", fontcolor="#64748b")
        if i > 0: dot.edge(f"h_{i-1}", f"h_{i}", color="#94a3b8", arrowsize='0.6')

# 하단 후보(너비) 노드 생성 및 확인 여부 칠하기
for idx, (cand_state, label_text) in enumerate(next_candidates):
    cand_lbl = " - ".join(cand_state)
    is_previewed = (search_mode == "너비 우선 탐색 (BFS)" and cand_state == st.session_state.bfs_current_preview)
    is_visited = (search_mode == "너비 우선 탐색 (BFS)" and cand_state in st.session_state.bfs_visited_candidates)
    is_cand_invalid, _ = is_invalid(cand_state)
    
    if is_previewed:
        dot.node(f"c_{idx}", cand_lbl + " (확인중)", color="#4f46e5", fillcolor="#818cf8", fontcolor="white")
    elif is_visited and is_cand_invalid:
         dot.node(f"c_{idx}", cand_lbl + " (실패)", color="#ef4444", fillcolor="#fee2e2", fontcolor="#991b1b")
    elif is_visited:
         dot.node(f"c_{idx}", cand_lbl + " (안전)", color="#10b981", fillcolor="#d1fae5", fontcolor="#065f46")
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

# --- 8. 하단 선택 버튼 컨트롤러 ---
if next_candidates:
    if search_mode == "깊이 우선 탐색 (DFS)":
        st.write("📍 **다음에 깊게 탐색할 대상을 선택하세요:**")
    else:
        st.write("📍 **이번 깊이(Level)에서 검사할 너비 노드들을 하나씩 모두 확인해 보세요:**")
        
    cols = st.columns(len(next_candidates))
    for idx, (cand_state, label_text) in enumerate(next_candidates):
        with cols[idx]:
            # BFS 모드일 때 이미 체크한 노드라면 체크 표시(✔️) 달아주기
            btn_label = label_text
            if search_mode == "너비 우선 탐색 (BFS)" and cand_state in st.session_state.bfs_visited_candidates:
                is_cand_fail, _ = is_invalid(cand_state)
                btn_label += " ❌ (확인완료)" if is_cand_fail else " ✔️ (안전확인)"
                
            if st.button(btn_label, key=f"action_btn_{idx}", use_container_width=True):
                if search_mode == "깊이 우선 탐색 (DFS)":
                    st.session_state.dfs_history.append(cand_state)
                else:
                    # 💡 BFS 작동: 클릭 시 해당 노드를 시뮬레이터에 '미리보기' 형태로 띄우고 방문 목록에 등록
                    st.session_state.bfs_current_preview = cand_state
                    st.session_state.bfs_visited_candidates.add(cand_state)
                    # 만약 안전한 이동이라면, 다음 깊이로 확장해나갈 수 있도록 후보로 임시 저장
                    is_cand_fail, _ = is_invalid(cand_state)
                    if not is_cand_fail:
                        st.session_state.bfs_next_level_parent = cand_state
                st.rerun()
