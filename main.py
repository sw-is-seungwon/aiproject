import streamlit as st

# 1. 페이지 기본 설정 (가장 상단에 위치)
st.set_page_config(
    page_title="AI 탐색 알고리즘 시각화",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 파스텔톤 커스텀 CSS 적용
st.markdown("""
    <style>
    /* 전체 배경 및 폰트 스타일 */
    .stApp {
        background-color: #FAFAFA;
    }
    
    /* 메인 타이틀 스타일 */
    .main-title {
        color: #4A5568;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        text-align: center;
        padding: 20px;
        margin-bottom: 10px;
    }
    
    /* 서브타이틀 스타일 */
    .sub-title {
        color: #718096;
        text-align: center;
        margin-bottom: 40px;
    }
    
    /* 파스텔톤 카드 공통 스타일 */
    .pastel-card {
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
        margin-bottom: 20px;
        transition: transform 0.2s;
        min-height: 280px;
    }
    .pastel-card:hover {
        transform: translateY(-5px);
    }
    
    /* 1번 카드: 무정보 탐색 (연한 파스텔 블루/라벤더) */
    .uninformed-card {
        background-color: #EBF8FF;
        border-left: 5px solid #90CDF4;
    }
    
    /* 2번 카드: 정보 이용 탐색 (연한 파스텔 그린/민트) */
    .informed-card {
        background-color: #E6FFFA;
        border-left: 5px solid #81E6D9;
    }
    
    /* 카드 제목 스타일 */
    .card-title {
        font-size: 20px;
        font-weight: 600;
        color: #2D3748;
        margin-bottom: 15px;
    }
    
    /* 카드 본문 스타일 */
    .card-body {
        font-size: 15px;
        color: #4A5568;
        line-height: 1.6;
    }
    
    /* 강조 뱃지 스타일 */
    .badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        margin-right: 5px;
        background-color: rgba(255, 255, 255, 0.6);
        color: #4A5568;
    }
    </style>
""", unsafe_allow_html=True)

# 3. 헤더 영역
st.markdown("<h1 class='main-title'>🤖 탐색 알고리즘 시각화 플레이그라운드</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>인공지능의 핵심인 무정보 탐색과 정보 이용 탐색의 원리를 시각적으로 이해해 보세요.</p>", unsafe_allow_html=True)

st.write("---")

# 4. 메인 콘텐츠 (2열 카드 배치)
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown(
        """
        <div class="pastel-card uninformed-card">
            <div class="card-title">🧩 1. 무정보 탐색 (Uninformed Search)</div>
            <p class="card-body">
                목적지에 대한 사전 정보 없이 오직 목표 상태인지 여부만 확인하며 탐색하는 방식입니다.<br><br>
                <b>주요 학습 내용:</b><br>
                <span class="badge">DFS (깊이우선)</span><span class="badge">BFS (너비우선)</span><br>
                • 농부, 양, 늑대, 양배추의 강 건너기 문제 해결<br>
                • 규칙에 따른 <b>상태공간트리(State Space Tree)</b> 변화 관찰<br>
                • 두 알고리즘의 탐색 경로 및 효율성 차이 비교
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    # 실제 구현된 페이지로 이동하는 버튼 (사이드바 이동 안내 또는 직접 링크)
    if st.button("무정보 탐색 실험실 입장 👉", key="btn_uninformed", use_container_width=True):
        st.info("왼쪽 사이드바 메뉴에서 no info 페이지를 선택해 주세요!")

with col2:
    st.markdown(
        """
        <div class="pastel-card informed-card">
            <div class="card-title">💡 2. 정보 이용 탐색 (Informed Search)</div>
            <p class="card-body">
                휴리스틱(Heuristic) 함수와 같은 추가적인 정보를 활용하여 목적지까지 더 효율적으로 찾아가는 방식입니다.<br><br>
                <b>주요 학습 내용:</b><br>
                <span class="badge">Heuristic</span><span class="badge">경로 최적화</span><br>
                • <b>서울에서 부산까지</b> 가는 최적의 경로 찾기<br>
                • 직접 노드(도시)를 선택하며 휴리스틱 값 변화 체험<br>
                • 실시간으로 계산되는 점수와 비용을 통해 알고리즘 직관적 이해
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    if st.button("정보 이용 탐색 실험실 입장 👉", key="btn_informed", use_container_width=True):
        st.info("왼쪽 사이드바 메뉴에서 inpormed 페이지를 선택해 주세요!")

# 5. 하단 가이드 팁
st.write("---")
st.markdown("""
    <div style='text-align: center; color: #A0AEC0; font-size: 13px;'>
        💡 본 웹앱은 학생들의 인공지능 알고리즘 수업을 돕기 위해 제작된 시각화 교구입니다.
    </div>
""", unsafe_allow_html=True)
