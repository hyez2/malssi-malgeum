import streamlit as st
import re
import time
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="말씨맑음 - 실시간 욕설 필터링 데모",
    page_icon="✨",
    layout="wide"
)

# 사이드바 정보
with st.sidebar:
    st.image("https://via.placeholder.com/150x150.png?text=말씨맑음", width=150)
    st.title("말씨맑음")
    st.caption("상담사를 위한 실시간 욕설 필터링 서비스")
    st.markdown("---")
    st.markdown("""
    ### 데모 안내
    이 데모는 상담사가 경험하는 부적절한 언어를 실시간으로 
    필터링하는 기술의 프로토타입입니다.
    
    채팅창에 메시지를 입력하면 욕설이나 부적절한 표현이
    자동으로 필터링됩니다.
    
    ### 프로젝트 소개
    말씨맑음은 상담사들의 심리적 안전을 보호하기 위한
    대학생 주도 프로젝트입니다.
    """)
    st.markdown("---")
    filter_level = st.select_slider(
        "필터링 강도 설정",
        options=["낮음", "중간", "높음"],
        value="중간"
    )
    
    show_stats = st.checkbox("통계 보기", value=True)
    
    st.markdown("---")
    st.caption("© 2025 말씨맑음 프로젝트")

# 한국어 욕설/비속어 사전 (데모용)
korean_slurs = {
    "낮음": ["존나", "죤나", "좆", "씨발", "병신", "지랄", "개새끼", "씨팔", "ㅅㅂ", "ㅂㅅ", "ㅈㄹ", "ㄱㅅㄲ"],
    "중간": ["존나", "죤나", "좆", "씨발", "병신", "지랄", "개새끼", "씨팔", "ㅅㅂ", "ㅂㅅ", "ㅈㄹ", "ㄱㅅㄲ", 
            "꺼져", "닥쳐", "죽어", "엿먹어", "미친", "개놈", "걸레", "창녀"],
    "높음": ["존나", "죤나", "좆", "씨발", "병신", "지랄", "개새끼", "씨팔", "ㅅㅂ", "ㅂㅅ", "ㅈㄹ", "ㄱㅅㄲ", 
            "꺼져", "닥쳐", "죽어", "엿먹어", "미친", "개놈", "걸레", "창녀",
            "멍청", "바보", "등신", "쓰레기", "못난", "찌질", "루저", "무능"]
}

# 공격적 표현 패턴 (데모용)
aggressive_patterns = {
    "낮음": [r'너\s*때문', r'니\s*탓', r'고소', r'소송', r'죽'],
    "중간": [r'너\s*때문', r'니\s*탓', r'고소', r'소송', r'죽', r'해고', r'짤', r'클레임', r'매니저', r'상사'],
    "높음": [r'너\s*때문', r'니\s*탓', r'고소', r'소송', r'죽', r'해고', r'짤', r'클레임', r'매니저', r'상사', 
            r'무능', r'제대로', r'제 때', r'일 못', r'왜 이렇게', r'항상', r'늘', r'맨날']
}

# 필터링 함수
def filter_text(text, level="중간"):
    filtered_text = text
    filter_count = 0
    detected_words = []
    
    # 욕설 필터링
    for word in korean_slurs[level]:
        if word in filtered_text:
            filtered_text = filtered_text.replace(word, "◼"*len(word))
            filter_count += 1
            detected_words.append(word)
    
    # 공격적 표현 필터링
    for pattern in aggressive_patterns[level]:
        matches = re.finditer(pattern, filtered_text)
        for match in matches:
            start, end = match.span()
            filtered_text = filtered_text[:start] + "◼"*(end-start) + filtered_text[end:]
            filter_count += 1
            detected_words.append(match.group())
    
    return filtered_text, filter_count, detected_words

# 세션 상태 초기화
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'filter_counts' not in st.session_state:
    st.session_state.filter_counts = []
    
if 'timestamps' not in st.session_state:
    st.session_state.timestamps = []

if 'total_filtered' not in st.session_state:
    st.session_state.total_filtered = 0

if 'total_messages' not in st.session_state:
    st.session_state.total_messages = 0

# 메인 컨테이너
main_container = st.container()

with main_container:
    st.title("😊 말씨맑음 - 실시간 욕설 필터링 데모")
    
    # 채팅 이력 표시
    chat_container = st.container()
    
    # 입력 폼
    with st.form(key="message_form", clear_on_submit=True):
        cols = st.columns([4, 1])
        with cols[0]:
            user_input = st.text_input("메시지 입력:", placeholder="여기에 메시지를 입력하세요...")
        with cols[1]:
            submit_button = st.form_submit_button("전송")
    
    if submit_button and user_input:
        # 메시지 필터링 처리 (실시간 효과를 위한 지연 추가)
        st.session_state.total_messages += 1
        
        with st.spinner("메시지 처리 중..."):
            # 원본 메시지 표시 (매우 짧은 시간만)
            temp_msg = st.empty()
            temp_msg.chat_message("user").write(f"{user_input}")
            
            # 필터링 진행 (실제로는 더 빠르게 처리되지만, 데모를 위해 지연 추가)
            time.sleep(0.5)
            
            # 필터링된 메시지로 교체
            filtered_msg, count, detected = filter_text(user_input, filter_level)
            
            if count > 0:
                st.session_state.total_filtered += 1
                
            temp_msg.empty()
            
            # 타임스탬프 생성
            current_time = datetime.now().strftime("%H:%M:%S")
            
            # 메시지 및 통계 저장
            st.session_state.messages.append((user_input, filtered_msg, count, detected, current_time))
            st.session_state.filter_counts.append(count)
            st.session_state.timestamps.append(current_time)
    
    # 채팅 이력 표시
    with chat_container:
        if len(st.session_state.messages) == 0:
            st.info("메시지를 입력하면 실시간으로 필터링 결과를 확인할 수 있습니다.")
        
        for i, (original, filtered, count, detected, timestamp) in enumerate(st.session_state.messages):
            message_container = st.container()
            
            with message_container:
                cols = st.columns([5, 1])
                with cols[0]:
                    if count > 0:
                        st.chat_message("user", avatar="🧍").write(f"{filtered}")
                        st.caption(f"⚠️ {count}개의 부적절 표현이 감지되었습니다.")
                    else:
                        st.chat_message("user", avatar="🧍").write(f"{filtered}")
                with cols[1]:
                    st.caption(f"시간: {timestamp}")

    # 통계 섹션
    if show_stats and len(st.session_state.messages) > 0:
        st.markdown("---")
        st.subheader("📊 필터링 통계")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="총 메시지 수",
                value=st.session_state.total_messages
            )
        
        with col2:
            st.metric(
                label="필터링된 메시지 수",
                value=st.session_state.total_filtered
            )
        
        with col3:
            if st.session_state.total_messages > 0:
                percentage = (st.session_state.total_filtered / st.session_state.total_messages) * 100
                st.metric(
                    label="필터링 비율",
                    value=f"{percentage:.1f}%"
                )
            else:
                st.metric(
                    label="필터링 비율",
                    value="0.0%"
                )
        
        # 시간별 필터링 차트
        if len(st.session_state.timestamps) > 1:
            df = pd.DataFrame({
                '시간': st.session_state.timestamps,
                '필터링 수': st.session_state.filter_counts
            })
            
            chart = alt.Chart(df).mark_line().encode(
                x='시간',
                y='필터링 수',
                tooltip=['시간', '필터링 수']
            ).properties(
                title='시간별 필터링 발생 추이',
                width=600,
                height=300
            )
            
            st.altair_chart(chart, use_container_width=True)

# 배포 안내
st.markdown("---")
st.info("""
### 배포 안내
이 데모는 Streamlit으로 제작되었으며, Streamlit Cloud 또는 Streamlit Community Cloud를 통해 무료로 배포할 수 있습니다.
1. GitHub에 이 코드를 업로드
2. Streamlit Cloud에 GitHub 저장소 연결
3. 몇 분 내에 공유 가능한 URL 생성
""")