import streamlit as st
import graphviz

# --- 1. 기본 페이지 설정 및 사이드바 테마 적용 ---
st.set_page_config(page_title="AI 탐색 기초 교육", layout="wide")

# 사이드바에서 탐색 모드 선택 (한 파일 안에서 제어)
with st.sidebar:
    st.header("🤖 AI 탐색 방식")
    search_mode = st.radio(
        "학습할 알고리즘을 선택하세요:",
        ["깊이 우선 탐색 (DFS)", "너비 우선 탐색 (BFS)"]
    )

# 💡 CSS 주입: st.html을 사용하여 텍스트 노출 버그 완벽 차단
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

/* 1. 이동 속도 감속 (3.0초로 부드럽게) */
.char { position: absolute; transition: all 3.0s ease-in-out; }
.boat { position: absolute; bottom: 3px; transition: all 3.0s ease-in-out; }

/* 2. 이동 완료(3초) 후 오버레이가 나타나도록 3초 애니메이션 딜레이 타이밍 설계 */
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
    animation: fadeIn 0.5s ease-in-out 3.0s forwards;
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
</style>""")

# --- 2. 세션 상태 분리 및 초기화 ---
if 'dfs_history' not in st.session_state:
    st.session_state.dfs_history = [('L','L','L','L')]
if 'bfs_history' not in st.session_state:
    st.session_state.bfs_history = [('L','L','L','L')]
if 'bfs_failed_nodes' not in st.session_state:
    st.session_state.bfs_failed_nodes = set()
if 'last_toast' not in st.session_state:
    st.session_state.last_toast = None

# 현재 선택한 모드에 맞춰 사용할 변수 매핑
if search_mode == "깊이 우선 탐색 (DFS)":
    history = st.session_state.dfs_history
else:
    history = st.session_state.bfs_history

# --- 3. 공통 핵심 알고리즘 및 규칙 정의 ---
def get_allowed_moves(current_state, current_history):
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
        if len(current_history) > 1 and state == current_history[-2]: continue
        candidates.append((state, label))
    return candidates

def is_invalid(state):
    f, w, s, c = state
    if w == s and f != w: return True, "늑대가 양을 해쳤습니다! 🐺"
    if s == c and f != s: return True, "양이 양배추를 먹어치웠습니다! 🐑"
    return False, ""

curr = history[-1]
game_over, reason = is_invalid(curr)

if game_over and st.session_state.last_toast != reason:
    st.toast(f"🚨 {reason}", icon="🔥")
    st.session_state.last_toast = reason

# --- 4. 메인 화면 타이틀 및 상단 시뮬레이션 박스 렌더링 ---
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

# --- 5. 게임 상태 제어 및 리셋/뒤로가기 버튼부 ---
if game_over:
    # 3. 너비 우선 탐색(BFS) 모드일 때 틀려도 되돌아갈 수 있는 '우회 기능' 완벽 작동
    if search_mode == "너비 우선 탐색 (BFS)":
        st.warning("💡 BFS 모드 특성: 현재 분기는 실패 상태이지만, 형제 분기(너비)들이 열려 있습니다. 뒤로 가 다른 너비를 시도하세요.")
        if st.button("⏪ 이 분기 취소하고 다른 너비 탐색하기 (뒤로 가기)"):
            if len(st.session_state.bfs_history) > 1:
                st.session_state.bfs_failed_nodes.add(st.session_state.bfs_history[-1])
                st.session_state.bfs_history.pop()
                st.session_state.last_toast = None
                st.rerun()
    else:
        if st.button("🔄 처음부터 다시 탐색 (DFS 리셋)"):
            st.session_state.dfs_history = [('L','L','L','L')]
            st.session_state.last_toast = None
            st.rerun()
            
elif curr == ('R','R','R','R'):
    # 5. 성공 시 강력한 빵빠레 효과 (풍선 + 눈꽃 레이어 결합)
    st.balloons()
    st.snow()
    st.success(f"🎉 **목표 상태 도달 성공!** {search_mode} 방식으로 안전하게 모두 이동시켰습니다.")
    
    # 4. 정답 맞췄을 때 실시간 이동 과정 타임라인 이력 요약 정리
    st.write("📋 **강을 건넌 성공 이동 경로 기록:**")
    history_elements = []
    for state in history:
        state_str = "".join(state)
        is_last = (state == history[-1])
        active_class = "active" if is_last else ""
        history_elements.append(f'<div class="timeline-node {active_class}">{state_str}</div>')
    arrow_separator = ' <span style="font-weight:bold; color:gray;">➔</span> '
    st.html(f'<div class="timeline-box">{"".join([e + (arrow_separator if i < len(history_elements)-1 else "") for i, e in enumerate(history_elements)])}</div>')
    
    if st.button("🔄 전체 초기화 후 다시 하기"):
        if search_mode == "깊이 우선 탐색 (DFS)":
            st.session_state.dfs_history = [('L','L','L','L')]
        else:
            st.session_state.bfs_history = [('L','L','L','L')]
            st.session_state.bfs_failed_nodes = set()
        st.session_state.last_toast = None
        st.rerun()

# --- 6. 하단 레이아웃: 상태 공간 트리 그래프 빌드 ---
st.markdown("---")
st.write("🌲 **상태 공간 트리 (자동으로 최하단 스크롤이 적용됩니다)**")

next_candidates = []
if not game_over and curr != ('R','R','R','R'):
    next_candidates = get_allowed_moves(curr, history)

dot = graphviz.Digraph()
dot.attr(rankdir='TB', size='6,4!', ratio='fill')
dot.attr('node', shape='box', style='filled,rounded', width='1.0', height='0.4', fixedsize='false', fontsize='12', fontname="Arial")

# 탐색 이력 노드 생성
for i, state in enumerate(history):
    node_lbl = " - ".join(state)
    if i == len(history) - 1:
        dot.node(f"h_{i}", node_lbl, color="#4f46e5", fillcolor="#6366f1", fontcolor="white", penwidth="2")
    else:
        dot.node(f"h_{i}", node_lbl, color="#cbd5e1", fillcolor="#f1f5f9", fontcolor="#64748b")
    if i > 0:
        dot.edge(f"h_{i-1}", f"h_{i}", color="#94a3b8", arrowsize='0.6')

# 후보 분기 노드 생성 (BFS 실패 이력이 있으면 붉은색 낙인)
for idx, (cand_state, label_text) in enumerate(next_candidates):
    cand_lbl = " - ".join(cand_state)
    if search_mode == "너비 우선 탐색 (BFS)" and cand_state in st.session_state.bfs_failed_nodes:
        dot.node(f"c_{idx}", cand_lbl + " (실패)", color="#ef4444", fillcolor="#fee2e2", fontcolor="#991b1b")
    else:
        dot.node(f"c_{idx}", cand_lbl, color="#10b981", fillcolor="#d1fae5", fontcolor="#065f46")
    dot.edge(f"h_{len(history)-1}", f"c_{idx}", style="dashed", color="#10b981", arrowsize='0.6')

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
if next_candidates:
    st.write("📍 **다음에 탐색할 대상을 선택하세요:**")
    cols = st.columns(len(next_candidates))
    for idx, (cand_state, label_text) in enumerate(next_candidates):
        with cols[idx]:
            # BFS 전용 실패 인덱스 시각화 표기 적용
            btn_label = label_text + " ❌" if (search_mode == "너비 우선 탐색 (BFS)" and cand_state in st.session_state.bfs_failed_nodes) else label_text
            if st.button(btn_label, key=f"action_btn_{idx}", use_container_width=True):
                if search_mode == "깊이 우선 탐색 (DFS)":
                    st.session_state.dfs_history.append(cand_state)
                else:
                    st.session_state.bfs_history.append(cand_state)
                st.rerun()
elif not game_over and curr != ('R','R','R','R'):
    st.warning("⚠️ **더 이상 이동할 수 있는 경로가 없습니다! (막다른 길)**")
    if st.button("⏪ 한 단계 뒤로 가기"):
        if search_mode == "깊이 우선 탐색 (DFS)" and len(st.session_state.dfs_history) > 1:
            st.session_state.dfs_history.pop()
        elif search_mode == "너비 우선 탐색 (BFS)" and len(st.session_state.bfs_history) > 1:
            st.session_state.bfs_history.pop()
        st.rerun()
