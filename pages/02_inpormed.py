import streamlit as st

st.set_page_config(page_title="탐색 알고리즘 게임")

# --------------------
# 그래프
# --------------------

graph = {

    "서울": {
        "홍천":50,
        "천안":100,
        "음성":100
    },

    "홍천": {
        "서울":50,
        "음성":80,
        "제천":60
    },

    "천안": {
        "서울":100,
        "음성":40,
        "대전":50
    },

    "음성": {
        "서울":100,
        "홍천":80,
        "천안":40,
        "상주":100,
        "의성":200
    },

    "제천": {
        "홍천":60,
        "안동":60
    },

    "안동": {
        "제천":60,
        "의성":50
    },

    "상주": {
        "음성":100,
        "부산":110
    },

    "의성": {
        "음성":200,
        "안동":50,
        "울산":120
    },

    "대전": {
        "천안":50,
        "대구":90
    },

    "대구": {
        "대전":90,
        "부산":60
    },

    "울산": {
        "의성":120,
        "부산":40
    },

    "부산": {
        "상주":110,
        "대구":60,
        "울산":40
    }
}

# --------------------
# 휴리스틱
# --------------------

h = {
    "서울":0,
    "홍천":50,
    "천안":100,
    "음성":100,
    "제천":110,
    "안동":120,
    "대전":150,
    "상주":200,
    "의성":220,
    "대구":240,
    "울산":340,
    "부산":999
}

# --------------------
# 세션 상태
# --------------------

if "current" not in st.session_state:
    st.session_state.current = "부산"

if "path" not in st.session_state:
    st.session_state.path = ["부산"]

if "cost" not in st.session_state:
    st.session_state.cost = 0

# --------------------
# 화면
# --------------------

st.title("🚗 서울로 가는 길")

st.write("목표 : 서울 도착")

st.subheader(f"현재 위치 : {st.session_state.current}")

st.write(f"누적 이동 시간 : {st.session_state.cost}분")

st.write("이동 경로")

st.write(" → ".join(st.session_state.path))

# --------------------
# 도착
# --------------------

if st.session_state.current == "서울":

    st.success("서울 도착!")

    st.balloons()

    if st.button("다시 시작"):

        st.session_state.current = "부산"
        st.session_state.path = ["부산"]
        st.session_state.cost = 0

        st.rerun()

# --------------------
# 이동
# --------------------

else:

    neighbors = graph[st.session_state.current]

    st.subheader("선택 가능한 도시")

    for city, distance in neighbors.items():

        col1, col2 = st.columns([4,1])

        with col1:

            st.write(
                f"{city} "
                f"(이동시간 {distance}분, "
                f"h={h[city]})"
            )

        with col2:

            if st.button(
                f"선택",
                key=city
            ):

                st.session_state.cost += distance

                st.session_state.current = city

                st.session_state.path.append(city)

                st.rerun()
