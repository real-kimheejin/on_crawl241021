import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import zipfile
import io
import os
from urllib.parse import unquote
import time
import pandas as pd

def create_zip(image_urls, address):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        total_images = len(image_urls)
        
        # 진행 상태 업데이트
        progress_bar = st.progress(0)
        status_text = st.empty()

        for idx, url in enumerate(image_urls, 1):
            try:
                
                progress = int((idx / total_images) * 100)
                progress_bar.progress(progress)
                status_text.text(f"ZIP 파일 생성 중... ({idx}/{total_images})")
                
                # 이미지 다운로드 및 저장
                response = requests.get(url)
                if response.status_code == 200:
                    image_data = response.content
                    filename = f"image_{idx}.jpg"
                    zip_file.writestr(filename, image_data)
            except Exception as e:
                st.error(f"이미지 다운로드 중 오류 발생: {str(e)}")

        # 완료 후 상태 텍스트와 프로그레스 바 제거
        status_text.empty()
        progress_bar.empty()
        st.success(f"✅ {address} 매물 이미지 ZIP 파일 생성 완료!")
        
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

# 페이지 설정
st.set_page_config(layout="wide", page_title="HTML 이미지 추출기")

# 제목 및 설명
st.title("🏠 부동산 매물 이미지 추출기")
st.markdown("HTML 소스코드를 입력하면 이미지를 추출하여 ZIP 파일로 다운로드할 수 있습니다.")

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
        status_text = st.empty()  # 상태 텍스트를 위한 빈 공간
        
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
        swiper_wrapper = soup.find('div', class_='swiper-wrapper')
        

        if swiper_wrapper:
            slides = swiper_wrapper.find_all('div', class_='swiper-slide')

            # 이미지 URL 추출 진행
            total_slides = len(slides)
            for idx, slide in enumerate(slides):
                img = slide.find('img')
                if img:
                    src = img.get('src')
                    if any(ext in src.lower() for ext in ['.jpg', '.jpeg']):
                        clean_url = src.split('?')[0]
                        image_urls.append(clean_url)
                # 진행률 업데이트 (30% ~ 90%)
                progress = 40 + (40 * (idx + 1) / total_slides)
                progress_bar.progress(int(progress))
                time.sleep(0.1)
                status_text.text(f"🖼️ 이미지 추출 중... ({idx + 1}/{total_slides})")
            # 결과 표시
            st.success(f"✅ {len(image_urls)}개 이미지 추출 완료!")
            
            # 완료 (100%)
            progress_bar.empty()
            status_text.empty()  # 상태 텍스트 제거
            

            
            # 주소와 이미지 개수 표시
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"📍 주소: {address}")
            with col2:
                st.info(f"🖼️ 발견된 이미지: {len(image_urls)}개")
            
            
            # 다운로드 버튼
            if image_urls:
                # ZIP 파일 생성 및 다운로드 버튼

                st.download_button(
                    label="📥 이미지 ZIP 다운로드",
                    data=create_zip(image_urls, address),
                    file_name=f"{address}.zip",
                    mime="application/zip",
                    use_container_width=True,
                    type="primary"
                )

        else:
            st.error("이미지를 찾을 수 없습니다.")
    else:
        st.warning("HTML 소스를 입력해주세요.")

# 푸터 추가
st.markdown("---")
st.markdown("Made with 🛠️ by HJ")

