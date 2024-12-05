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
                
                # 디버깅: 현재 처리 중인 URL 출력
                st.write(f"다운로드 시도 중: {url}")
                
                # 이미지 다운로드 및 저장
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Referer': 'https://www.onhouse.com/',
                    'Origin': 'https://www.onhouse.com',
                    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"macOS"',
                    'Sec-Fetch-Dest': 'image',
                    'Sec-Fetch-Mode': 'no-cors',
                    'Sec-Fetch-Site': 'cross-site'
                }
                response = requests.get(url, headers=headers)
                
                # 디버깅: 응답 상태 코드 출력
                st.write(f"응답 상태 코드: {response.status_code}")
                
                if response.status_code == 200:
                    image_data = response.content
                    filename = f"image_{idx}.jpg"
                    zip_file.writestr(filename, image_data)
                    st.write(f"✓ 이미지 저장 완료: {filename}")
                else:
                    st.error(f"이미지 다운로드 실패 - 상태 코드: {response.status_code}")
                    
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
st.markdown("HTML 소스드를 입력하면 이미지를 추출하여 ZIP 파일로 다운로드할 수 있습니다.")

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
        
        # 디버깅: HTML 파싱 결과 확인
        st.write(f"🔍 HTML 길이: {len(html_source)}자")
        
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
            # 수정된 정규식 패턴: 쿼리 파라미터를 포함한 URL도 매칭
            url_match = re.search(r'background-image: url\("(https:[^"]+)"\)', style)
            if url_match:
                image_url = url_match.group(1)
                # 기본 URL만 저장 (쿼리 파라미터 제거)
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
            st.markdown("### 📋 이미지 다운로드")
            
            # 세션 상태에 다운로드한 URL 저장
            if 'downloaded_urls' not in st.session_state:
                st.session_state.downloaded_urls = set()
            
            # 남은 URL만 표시
            remaining_urls = [url for url in image_urls if url not in st.session_state.downloaded_urls]
            
            if remaining_urls:
                for idx, url in enumerate(remaining_urls, 1):
                    with st.form(key=f"form_{url}"):
                        if st.form_submit_button(
                            label=f"📥 {idx}번째 이미지",
                            type="primary",
                            use_container_width=True
                        ):
                            # 이미지 다운로드 로직
                            try:
                                response = requests.get(url)
                                if response.status_code == 200:
                                    st.download_button(
                                        label="⬇️ 클릭하여 저장",
                                        data=response.content,
                                        file_name=f"image_{idx}.jpg",
                                        mime="image/jpeg",
                                        key=f"download_{url}",
                                        use_container_width=True
                                    )
                                    st.session_state.downloaded_urls.add(url)
                            except Exception as e:
                                st.error(f"다운로드 중 오류 발생: {str(e)}")
            else:
                st.success("✅ 모든 이미지를 다운로드했습니다!")

    else:
        st.warning("HTML 소스를 입력해주세요.")

# 푸터 추가
st.markdown("---")
st.markdown("Made with 🛠️ by HJ")

