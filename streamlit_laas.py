import requests
from dotenv import load_dotenv
import os
import streamlit as st
import OpenDartReader
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import rc

rc('font', family='Malgun Gothic')
plt.rcParams['axes.unicode_minus'] = False

# Load environment variables from .env file
load_dotenv()

header = {
    "project": os.getenv("WANTED_LASS_PROJECT"),
    "apiKey": os.getenv("WANTED_LASS_API_KEY")
}
URL = os.getenv("WANTED_LASS_URL")

if not URL.startswith("http://") and not URL.startswith("https://"):
    URL = "https://" + URL

# Load Dart API key
api_key = 'd995ea890aedf240f9270e6e368699baeaa46d13'
dart = OpenDartReader(api_key)

# Sidebar for navigation
st.sidebar.title("프로젝트 에이전트")
page = st.sidebar.radio("필요한 LLM을 골라주세요", ["주제 분석기", "기업 분석기", "최신 소식 에이전트"])

# Sidebar input for company name
default_company = st.sidebar.text_input('기본 기업/브랜드명 입력', value='')

# Page 1: 주제 분석기
if page == "주제 분석기":
    st.title('주제 분석기')
    st.write('주제를 입력하면, 전공 용어에 대한 상세한 설명을 제시합니다.')
    topic = st.text_input('주제')
    if topic:
        body1 = {
            "hash": "99ab29fce39ae3c8824c3e4dcc6cc315579135292b719114e2e86e56ada4cd51",
            "params": {"topic": topic}
        }
        response1 = requests.post(URL, headers=header, json=body1)
        if response1.status_code == 200:
            st.write(response1.json()["choices"][0]["message"]["content"])
        else:
            st.write("Error:", response1.status_code, response1.text)

# Page 2: 기업 분석기
elif page == "기업 분석기":
    st.title('기업 분석기')
    st.write('키워드를 기반으로, 기업/브랜드에 대한 분석을 제공합니다.')
    company = st.text_input('기업/브랜드명', value=default_company)
    keyword = st.text_input('주제 키워드')
    if company:
        try:
            # Retrieve financial statement data for 2023
            data_2023 = dart.finstate(company, 2023)
            if data_2023 is not None and not data_2023.empty:
                # Filter for operating profit data
                operating_profit_data = data_2023[data_2023['account_nm'] == '영업이익']
                if not operating_profit_data.empty:
                    # Extract operating profit amounts for each year
                    years = ['2021', '2022', '2023']
                    operating_profits = [
                        int(operating_profit_data[f'thstrm_amount'].iloc[0].replace(',', '')),
                        int(operating_profit_data[f'frmtrm_amount'].iloc[0].replace(',', '')),
                        int(operating_profit_data[f'bfefrmtrm_amount'].iloc[0].replace(',', ''))
                    ]
                    # Plot the operating profit trend
                    fig, ax = plt.subplots(figsize=(4, 1))
                    ax.bar(years, operating_profits)
                    ax.set_xlabel('연도')
                    ax.set_ylabel('영업이익 (백만 원)')
                    ax.set_title(f'{company} 영업이익 추이')
                    st.pyplot(fig)
                
                # Filter for sales data
                sales_data = data_2023[data_2023['account_nm'] == '매출액']
                if not sales_data.empty:
                    # Extract sales amounts for each year
                    sales = [
                        int(sales_data[f'thstrm_amount'].iloc[0].replace(',', '')),
                        int(sales_data[f'frmtrm_amount'].iloc[0].replace(',', '')),
                        int(sales_data[f'bfefrmtrm_amount'].iloc[0].replace(',', ''))
                    ]
                    # Plot the sales trend
                    fig, ax = plt.subplots(figsize=(4, 1))
                    ax.bar(years, sales)
                    ax.set_xlabel('연도')
                    ax.set_ylabel('매출액 (백만 원)')
                    ax.set_title(f'{company} 매출액 추이')
                    st.pyplot(fig)
        except Exception as e:
            st.write("DART 데이터 조회 중 오류가 발생했습니다:", str(e))

    if company and keyword:
        body2 = {
            "hash": "7e88656315e1fc05bf2b1524eb475c17a518162380c2d116ffa540cc97e5cc8a",
            "params": {"company": company, "keyword": keyword}
        }
        response2 = requests.post(URL, headers=header, json=body2)
        if response2.status_code == 200:
            st.write(response2.json()["choices"][0]["message"]["content"])
        else:
            st.write("Error:", response2.status_code, response2.text)

# Page 3: 최신 소식 에이전트
elif page == "최신 소식 에이전트":
    st.title('최신 소식 에이전트')
    st.write('기업/브랜드를 입력하면, 그에 맞는 소식을 제공합니다.')
    company2 = st.text_input('기업/브랜드명', value=default_company)
    if company2:
        body3 = {
            "hash": "d5d1832354c30dcfbc31f642166763cef4d14cf158fe8aae779ef45953b260b7",
            "params": {"company": company2}
        }
        response3 = requests.post(URL, headers=header, json=body3)
        if response3.status_code == 200:
            response_json = response3.json()
            if "choices" in response_json and len(response_json["choices"]) > 0:
                st.write(response_json["choices"][0]["message"]["content"])
            else:
                st.write("해당 기업에 대한 최신 소식을 찾을 수 없습니다.")
        else:
            st.write("Error:", response3.status_code, response3.text)
