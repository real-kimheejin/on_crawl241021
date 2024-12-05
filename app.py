import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import time

# 페이지 설정
st.set_page_config(layout="wide", page_title="HTML 이미지 추출기")

# 제목 및 설명
st.title("🏠 부동산 매물 이미지 추출기")
st.markdown("HTML 소스코드를 입력하면 이미지를 추출하여 URL을 확인할 수 있습니다.")

# HTML 입력 영역
image_urls = []

html_source = st.text_area(
    "HTML > body 태그를 복사해서 입력하세요", 
    height=200, 
    placeholder="HTML > body 태그를 복사해서 입력하세요"
)

if st.button("이미지 추출하기", type="primary", use_container_width=True, disabled=len(image_urls)):
    if html_source:
        # 전체 진행상황을 보여주는 프로그레스 바
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # HTML 파싱 (10%)
        time.sleep(0.5)
        status_text.text("🔍 HTML 파싱 중...")
        progress_bar.progress(10)
        soup = BeautifulSoup(html_source, 'html.parser')
        
        # 주소 추출 (20%)
        time.sleep(0.5)
        status_text.text("📍 주소 추출 중...")
        progress_bar.progress(20)
        addr_elem = soup.find('h6', class_='addr_title')
        address = addr_elem.text if addr_elem else "주소를 찾을 수 없습니다"
        
        # 이미지 URL 추출 시작 (30%)
        time.sleep(0.5)
        status_text.text("🖼️ 이미지 URL 추출 중...")
        progress_bar.progress(30)
        
        # style 속성에서 background-image URL 찾기
        elements_with_style = soup.find_all(lambda tag: tag.get('style') and 'background-image: url("https:' in tag.get('style'))
        total_elements = len(elements_with_style)

        for idx, element in enumerate(elements_with_style):
            style = element.get('style', '')
            url_match = re.search(r'background-image: url\("(https:[^"]+)"\)', style)
            if url_match:
                image_url = url_match.group(1)
                base_url = image_url.split('?')[0]
                if base_url.lower().endswith(('.jpg', '.jpeg')):
                    image_urls.append(base_url)
            
            # 진행률 업데이트 (30% ~ 90%)
            progress = 40 + (40 * (idx + 1) / total_elements)
            progress_bar.progress(int(progress))
            time.sleep(0.1)
            status_text.text(f"🖼️ 이미지 추출 중... ({idx + 1}/{total_elements})")
        
        # 결과 표시
        st.success(f"✅ {len(image_urls)}개 이미지 추출 완료!")
        
        # 완료 (100%)
        progress_bar.empty()
        status_text.empty()
        
        # 주소와 이미지 개수 표시
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"📍 주소: {address}")
        with col2:
            st.info(f"🖼️ 발견된 이미지: {len(image_urls)}개")
        
        # URL 목록 표시
        if image_urls:
            st.markdown("### 📋 이미지 URL 목록")
            for idx, url in enumerate(image_urls, 1):
                st.markdown(f"{idx}번째 이미지: {url}")

    else:
        st.warning("HTML 소스를 입력해주세요.")

# 푸터 추가
st.markdown("---")
st.markdown("Made with 🛠️ by HJ")

