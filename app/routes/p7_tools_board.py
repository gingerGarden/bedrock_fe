"""
사용자 작성 사항
 * 제목, 내용
 * 날짜는 자동으로 남음
 * 어떤 사용자가 작성했는지, 관리자만 볼 수 있음

개발 선정 방식
 * 사용자의 추천이 많은 게시글
 * 개발 난이도가 낮은 게시글
"""
import streamlit as st



class ToolsBoard:
 
    @classmethod
    def UI(cls):
        st.title("💡 신규 도구 개발 요청")
        st.markdown("KHA 플랫폼에 더 필요한 도구가 있나요? 자유롭게 아이디어를 남겨주세요.")
        st.markdown("---")

        # 1. 신규 요청 등록 폼 (카테고리 제외)
        cls.render_request_form()
        st.markdown("---")

        # 2. 요청 내역 리스트 (추천 기능 포함)
        cls.render_request_list()


    @classmethod
    def render_request_form(cls):
        st.write("### 📝 신규 도구 신청")
        with st.form("tool_request_form", clear_on_submit=True):
            req_title = st.text_input(
                "희망 도구명",
                placeholder="예: PDF 내 복잡한 표를 엑셀로 추출해주는 도구"
            )

            req_desc = st.text_area(
                "상세 요구사항",
                placeholder="어떤 상황에서 이 도구가 필요한지, 구체적으로 어떤 결과물이 나오길 기대하시는지 적어주세요."
            )

            submitted = st.form_submit_button("요청 제출", use_container_width=True, type="primary")

            if submitted:
                if req_title and req_desc:
                    # 3단계 DB 연동 시: insert_request(title, desc, status='검토중', votes=0)
                    st.success(f"🎉 '{req_title}' 요청이 성공적으로 접수되었습니다. 개발자가 검토 후 목록에 업데이트하겠습니다.")
                else:
                    st.warning("도구명과 요구사항을 모두 입력해 주세요.")


    @classmethod
    def render_request_list(cls):
        st.write("### 📬 최근 요청 및 검토 현황")
        mock_data = [
            {"id": 1, "title": "임상 데이터 시각화 도구", "desc": "실험 데이터를 넣으면 논문용 그래프 자동 생성", "status": "개발중", "date": "2024-03-20", "votes": 15},
            {"id": 2, "title": "OCR 영수증 처리기", "desc": "식대 영수증 사진을 찍으면 텍스트로 변환하여 엑셀 정리", "status": "검토중", "date": "2024-03-22", "votes": 8},
            {"id": 3, "title": "논문 초록 요약기", "desc": "긴 영문 초록을 한글 3줄로 핵심 요약", "status": "완료", "date": "2024-03-15", "votes": 12},
        ]

        status_colors = {"검토중": "gray", "개발중": "blue", "완료": "green"}

        if not mock_data:
            st.info("아직 등록된 요청이 없습니다.")
            return

        for req in mock_data:
            with st.container(border=True):
                c1, c2, c3 = st.columns([4, 1, 1])
                with c1:
                    st.markdown(f"**{req['title']}**")
                    st.write(req['desc'])
                    st.caption(f"📅 요청일: {req['date']}")
                with c2:
                    color = status_colors.get(req['status'], "gray")
                    st.write("")
                    st.markdown(f"[:{color}[{req['status']}]]")

                # --- 누락된 추천 버튼 영역 추가 ---
                with c3:
                    st.write("")
                    if st.button(f"👍 {req['votes']}", key=f"vote_{req['id']}", use_container_width=True):
                        st.toast(f"'{req['title']}' 도구 개발을 추천하셨습니다!")