import os
import random

import pandas as pd
import requests
import streamlit as st

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="우리 지역 체크인", page_icon="📍", layout="wide")
st.title("우리 지역 체크인")

try:
    locations = requests.get(f"{BACKEND_URL}/locations", timeout=5).json()
except requests.exceptions.RequestException as e:
    st.error("백엔드 서버(8000번)에 연결할 수 없습니다. BE 터미널이 켜져 있는지 확인하세요.")
    st.stop()

st.sidebar.subheader("🔍 검색 조건")
selected_region = st.sidebar.selectbox("지역", ["전체"] + list(locations.keys()))
selected_min_score = st.sidebar.slider("최소 만족도", 1, 5, 1)
search_memo = st.sidebar.text_input("메모 검색")

filter_params = {}
if selected_region != "전체":
    filter_params["region"] = selected_region
if selected_min_score > 1:
    filter_params["min_score"] = selected_min_score
if search_memo:
    filter_params["keyword"] = search_memo

tab1, tab2, tab3 = st.tabs(["기록 남기기", "내 기록", "전체 현황"])

with tab1:
    st.caption("새로운 방문 기록을 입력하고 저장합니다.")
    with st.form("record_form"):
        name = st.text_input("이름")
        region = st.selectbox("지역", list(locations.keys()))
        satisfaction = st.slider("만족도", 1, 5, 3)
        memo = st.text_input("한 줄 메모")
        submit_button = st.form_submit_button("기록 저장")

        if submit_button:
            if not name:
                st.warning("이름을 입력해주세요")
            else:
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/records",
                        json={
                            "user_name": name,
                            "region": region,
                            "score": satisfaction,
                            "memo": memo
                        },
                        timeout=5
                    )
                    if response.status_code == 201:
                        record_id = response.json().get("id")
                        st.success(f"저장 완료! (id: {record_id})")
                    else:
                        detail = response.json().get("detail", "알 수 없는 오류")
                        st.error(f"저장 실패: {detail}")
                except requests.exceptions.RequestException:
                    st.error("백엔드에 연결할 수 없습니다. BE 터미널이 켜져 있는지 확인하세요.")

with tab2:
    st.caption("내가 남긴 기록을 조회하고 관리합니다.")
    st.write("조회할 이름")
    col_name, col_button = st.columns([3, 1])
    with col_name:
        search_name = st.text_input("조회할 이름", label_visibility="collapsed")
    with col_button:
        st.write("")
        search_button = st.button("내 기록 보기")

    if search_button or (search_name and "last_search" in st.session_state and st.session_state.last_search == search_name):
        if search_button:
            st.session_state.last_search = search_name
        try:
            response = requests.get(f"{BACKEND_URL}/records/user/{search_name}", timeout=5)
            data = response.json()
            count = data.get("count", 0)
            avg_score = data.get("avg_score", 0)
            records = data.get("records", [])

            if count == 0:
                st.info(f"'{search_name}' 이름으로 남긴 기록이 없습니다.")
            else:
                metric_col1, metric_col2 = st.columns(2)
                with metric_col1:
                    st.metric("내 기록 수", count)
                with metric_col2:
                    st.metric("평균 만족도", avg_score)
                st.dataframe(pd.DataFrame(records))

                st.write("**기록 삭제**")
                record_options = [
                    f"{r['id']} · {r['region']} · {r['score']} · {r['memo']}"
                    for r in records
                ]
                selected_record = st.selectbox("삭제할 기록 선택", record_options)

                if st.button("선택한 기록 삭제"):
                    selected_id = selected_record.split(" · ")[0]
                    try:
                        delete_response = requests.delete(
                            f"{BACKEND_URL}/records/{selected_id}",
                            timeout=5
                        )
                        if delete_response.status_code == 200:
                            st.success("삭제했습니다")
                            st.rerun()
                        else:
                            st.error("삭제에 실패했습니다.")
                    except requests.exceptions.RequestException:
                        st.error("백엔드에서 기록을 삭제할 수 없습니다.")
        except requests.exceptions.RequestException:
            st.error("백엔드에서 기록을 불러올 수 없습니다.")

with tab3:
    st.caption("전체 통계와 기록을 확인합니다.")

    try:
        stats_response = requests.get(f"{BACKEND_URL}/stats", timeout=5)
        stats = stats_response.json()

        metric_col1, metric_col2, metric_col3 = st.columns(3)
        with metric_col1:
            st.metric("총 기록 수", stats.get("total", 0))
        with metric_col2:
            st.metric("참여자 수", stats.get("user_count", 0))
        with metric_col3:
            st.metric("전체 평균 만족도", stats.get("overall_avg", 0))

        by_region = stats.get("by_region", [])
        if by_region:
            region_df = pd.DataFrame(by_region)
            region_df = region_df.set_index("region")
            st.bar_chart(region_df["avg_score"])
    except requests.exceptions.RequestException:
        st.error("백엔드에서 통계를 불러올 수 없습니다.")

    st.subheader("전체 기록")
    try:
        records_response = requests.get(f"{BACKEND_URL}/records", timeout=5, params=filter_params)
        response_data = records_response.json()
        records = response_data.get("records", [])
        record_count = response_data.get("count", 0)

        st.sidebar.markdown(f"**조건에 맞는 기록: {record_count}건**")

        if records:
            df_records = pd.DataFrame(records)
            st.dataframe(df_records)

            csv_response = requests.get(f"{BACKEND_URL}/records/export.csv", timeout=5, params=filter_params)
            st.download_button(
                label="CSV로 내려받기",
                data=csv_response.content,
                file_name="records.csv",
                mime="text/csv"
            )
        else:
            st.warning("조건에 맞는 기록이 없습니다. 조건을 완화해보세요.")
    except requests.exceptions.RequestException:
        st.error("백엔드에서 기록을 불러올 수 없습니다.")

    st.caption("실습 시작 코드에 있던 데모 지도입니다. 저장된 기록과는 무관하게 랜덤 좌표를 표시합니다.")

    city = st.selectbox("지역 선택", list(locations.keys()))
    n_points = st.slider("랜덤 포인트 개수", 10, 200, 50)

    center = locations[city]

    random.seed()
    df = pd.DataFrame(
        {
            "lat": [center["lat"] + random.uniform(-0.02, 0.02) for _ in range(n_points)],
            "lon": [center["lon"] + random.uniform(-0.02, 0.02) for _ in range(n_points)],
            "value": [random.randint(1, 100) for _ in range(n_points)],
        }
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader(f"{city} 지도")
        st.map(df, latitude="lat", longitude="lon", size="value")

    with col2:
        st.subheader("값 분포")
        st.bar_chart(df["value"])

    st.subheader("원본 데이터")
    st.dataframe(df)
