import os
import random

import pandas as pd
import requests
import streamlit as st

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="위치 랜덤 데이터 시각화", layout="wide")
st.title("위치 기반 랜덤 데이터 시각화")

try:
    locations = requests.get(f"{BACKEND_URL}/locations", timeout=5).json()
except requests.exceptions.RequestException as e:
    st.error(f"백엔드 연결 실패: {e}")
    st.stop()

st.subheader("방문 기록 입력")
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
                st.error("백엔드에 연결할 수 없습니다. 터미널 1에서 백엔드가 켜져 있는지 확인하세요.")

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

st.subheader("전체 기록")
try:
    records_response = requests.get(f"{BACKEND_URL}/records", timeout=5)
    response_data = records_response.json()
    records = response_data.get("records", [])
    if records:
        df_records = pd.DataFrame(records)
        st.dataframe(df_records)
    else:
        st.info("아직 기록이 없습니다. 위에서 첫 기록을 남겨보세요.")
except requests.exceptions.RequestException:
    st.error("백엔드에서 기록을 불러올 수 없습니다.")

st.subheader("원본 데이터")
st.dataframe(df)
