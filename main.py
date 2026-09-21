import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_movie_data():
    """KOBIS 일별 박스오피스 데이터를 불러와 전처리합니다."""
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"
    
    # CSV 데이터 로드
    df = pd.read_csv(url)
    
    # '날짜' 열을 YYYYMMDD 형식을 고려하여 datetime 객체로 변환
    df['날짜'] = pd.to_datetime(df['날짜'].astype(str), format='%Y%m%d')
    
    # 수치형 데이터 컬럼 보장
    numeric_cols = ['순위', '일관객', '누적관객', '스크린수', '상영횟수']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    return df

try:
    with st.spinner("영화 박스오피스 데이터를 불러오는 중입니다..."):
        df = load_movie_data()
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.caption("KOBIS 일별 박스오피스 1년치(365일) 데이터를 바탕으로 시간에 따른 변화를 탐색합니다.")
st.markdown("---")

st.sidebar.header("📊 데이터셋 정보")
min_date = df['날짜'].min().strftime('%Y-%m-%d')
max_date = df['날짜'].max().strftime('%Y-%m-%d')
total_movies = df['영화명'].nunique()

st.sidebar.metric(label="분석 기간", value=f"{min_date} ~ {max_date}")
st.sidebar.metric(label="수집된 영화 수", value=f"{total_movies:,}개")
st.sidebar.markdown("---")
st.sidebar.info("💡 **안내**: 상단 탭을 통해 다양한 관점의 시간 분석 그래프를 확인하실 수 있습니다.")

tab1, tab2, tab3 = st.tabs([
    "📈 1. 영화별 일관객 변화", 
    "📊 2. 주요 영화 관객 비교 (추가 예정)", 
    "📅 3. 월별/요일별 추이 (추가 예정)"
])

with tab1:
    st.subheader("📌 섹션 1: 특정 영화의 날짜별 일관객수 추이")
    st.write("관심 있는 영화를 선택하여 시상(시간) 흐름에 따른 관객수 변화 그래프를 확인하세요.")
    
    # 영화 선택 드롭다운 (가장 최신/관객수 많은 순으로 정렬)
    movie_list = df.groupby('영화명')['일관객'].sum().sort_values(ascending=False).index.tolist()
    selected_movie = st.selectbox(
        "영화명을 선택하세요:",
        options=movie_list,
        index=0,
        help="검색하거나 목록에서 원하는 영화를 선택할 수 있습니다."
    )
    
    # 선택된 영화 데이터 필터링 및 날짜순 정렬
    movie_df = df[df['영화명'] == selected_movie].sort_values('날짜')
    
    if not movie_df.empty:
        # 요약 메트릭 표시
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Top 10 진입 일수", f"{len(movie_df):,}일")
        with col2:
            st.metric("최고 일관객수", f"{movie_df['일관객'].max():,}명")
        with col3:
            st.metric("최고 순위", f"{int(movie_df['순위'].min())}위")
        with col4:
            st.metric("기간 내 최고 누적관객수", f"{movie_df['누적관객'].max():,}명")
        
        st.write("")
        
        # Plotly 선 그래프 생성
        fig = px.line(
            movie_df,
            x='날짜',
            y='일관객',
            title=f"<b>[{selected_movie}] 일별 관객수 변화</b>",
            labels={'날짜': '날짜', '일관객': '일별 관객수(명)'},
            markers=True,
            template="plotly_white"
        )
        
        # 툴팁(Hover) 사용자 정의
        fig.update_traces(
            hovertemplate="<b>날짜:</b> %{x|%Y년 %m월 %d일}<br><b>일관객수:</b> %{y:,}명<extra></extra>",
            line=dict(width=2.5, color='#E50914')
        )
        
        # 레이아웃 미화
        fig.update_layout(
            hovermode="x unified",
            xaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
            yaxis=dict(showgrid=True, gridcolor='#f0f0f0', tickformat=","),
            height=450,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.info(f"💡 **이 그래프로 알 수 있는 것**: **{selected_movie}**은(는) 개봉 초기 관객 집중도와 주말/평일 간의 관객수 격차, 그리고 박스오피스 상위권 유지 기간을 한눈에 파악할 수 있습니다.")
    else:
        st.warning("선택한 영화의 데이터가 존재하지 않습니다.")

with tab2:
    st.subheader("📌 섹션 2: 기간 내 관객수 Top 5 영화의 관객수 추이 비교")
    st.write("수집된 기간 동안 일관객 합계가 가장 큰 상위 5개 영화의 날짜별 관객수 변화를 한 그래프에서 비교합니다.")
    
    # 일관객 합계 기준 Top 5 영화 추출
    top5_movies = df.groupby('영화명')['일관객'].sum().nlargest(5).index.tolist()
    
    # Top 5 영화 데이터 필터링 및 날짜순 정렬
    top5_df = df[df['영화명'].isin(top5_movies)].sort_values('날짜')
    
    if not top5_df.empty:
        # Top 5 영화 메트릭 요약 표시
        st.write("🏆 **기간 내 총 관객수 상위 5개 영화**")
        top5_summary = df[df['영화명'].isin(top5_movies)].groupby('영화명')['일관객'].sum().reindex(top5_movies)
        
        cols = st.columns(5)
        for idx, (movie_name, total_aud) in enumerate(top5_summary.items()):
            with cols[idx]:
                st.metric(
                    label=f"{idx+1}위: {movie_name}",
                    value=f"{total_aud:,}명"
                )
        
        st.write("")
        
        # Plotly 다중 선 그래프 생성
        fig2 = px.line(
            top5_df,
            x='날짜',
            y='일관객',
            color='영화명',
            category_orders={'영화명': top5_movies},
            title="<b>[Top 5 영화] 날짜별 일관객수 비교</b>",
            labels={'날짜': '날짜', '일관객': '일별 관객수(명)', '영화명': '영화 제목'},
            markers=True,
            template="plotly_white"
        )
        
        # 툴팁 및 스타일 설정
        fig2.update_traces(
            hovertemplate="<b>영화명:</b> %{fullData.name}<br><b>날짜:</b> %{x|%Y년 %m월 %d일}<br><b>일관객수:</b> %{y:,}명<extra></extra>",
            line=dict(width=2)
        )
        
        fig2.update_layout(
            hovermode="x unified",
            xaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
            yaxis=dict(showgrid=True, gridcolor='#f0f0f0', tickformat=","),
            height=500,
            legend=dict(
                title="영화 선택 (클릭하여 범례 토글)",
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=20, r=20, t=60, b=20)
        )
        
        st.plotly_chart(fig2, use_container_width=True)
        
        # 인사이트 문구 박스
        top_names_str = ", ".join([f"**{m}**" for m in top5_movies[:3]])
        st.info(f"💡 **이 그래프로 알 수 있는 것**: 흥행 상위 영화인 {top_names_str} 등이 서로 다른 시기에 흥행 정상에 올랐던 패턴과 각 영화별 최고 관객 수(피크 Point)의 높이를 직접 비교할 수 있습니다. (오른쪽 상단 범례 항목을 클릭하여 특정 영화만 선택/제외 가능합니다.)")
    else:
        st.warning("Top 5 영화 데이터를 생성할 수 없습니다.")

with tab3:
    st.subheader("📌 섹션 3: 월별 및 요일별 Box Office 패턴")
    st.write("시즌별(월별, 요일별) 전체 박스오피스 관객 동향 및 시계열 패턴을 분석하는 공간입니다.")
    st.info("💡 **이 그래프로 알 수 있는 것**: (추후 그래프 추가 시 분석 문구가 들어갈 자리입니다.)")

st.markdown("---")
st.caption("데이터 출처: 영화진흥위원회(KOBIS) 일별 박스오피스 데이터 | 영화 데이터 그래프 도감 프로젝트")
