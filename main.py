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

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 1. 영화별 일관객 변화", 
    "📊 2. 주요 영화 관객 비교", 
    "🏔️ 3. 일별 총 관객수 추이 (영역 그래프)",
    "🏆 4. 기간 내 TOP 10 영화 (가로 막대그래프)",
    "🔥 5. 월×요일별 관객 분포 (히트맵)"
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
    st.subheader("📌 섹션 3: 날짜별 10위권 일관객 합계 추이 (영역 그래프)")
    st.write("매일 박스오피스 상위 10개 영화의 일관객을 모두 합산하여 전체 극장가의 관객 동향과 최고 피크일을 확인합니다.")
    
    # 날짜별 일관객 합계 계산
    daily_total_df = df.groupby('날짜')['일관객'].sum().reset_index().sort_values('날짜')
    
    if not daily_total_df.empty:
        # 상위 3개 관객수 극대화 날짜 추출
        top3_days = daily_total_df.nlargest(3, '일관객').reset_index(drop=True)
        
        # 메트릭 요약
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_daily = int(daily_total_df['일관객'].mean())
            st.metric("일평균 총 관객수(Top 10)", f"{avg_daily:,}명")
        with col2:
            max_day_str = top3_days.iloc[0]['날짜'].strftime('%Y-%m-%d')
            st.metric("최고 관객 기록일 (1위)", max_day_str)
        with col3:
            max_aud_val = top3_days.iloc[0]['일관객']
            st.metric("1위 날의 총 관객수", f"{max_aud_val:,}명")
            
        st.write("")
        
        # Plotly 영역 그래프 (Area Chart) 생성
        fig3 = px.area(
            daily_total_df,
            x='날짜',
            y='일관객',
            title="<b>[전체 박스오피스] 날짜별 일관객 합계 추이</b>",
            labels={'날짜': '날짜', '일관객': '일별 총 관객수(명)'},
            template="plotly_white"
        )
        
        # 그래프 채우기 색상 및 라인 스타일 설정
        fig3.update_traces(
            line=dict(color='#E50914', width=2),
            fillcolor='rgba(229, 9, 20, 0.25)',
            hovertemplate="<b>날짜:</b> %{x|%Y년 %m월 %d일}<br><b>일관객 합계:</b> %{y:,}명<extra></extra>"
        )
        
        # Top 3 피크 날짜 화살표 및 주석(Annotation) 표시
        for rank, row in top3_days.iterrows():
            peak_date = row['날짜']
            peak_val = row['일관객']
            date_label = peak_date.strftime('%Y-%m-%d')
            
            fig3.add_annotation(
                x=peak_date,
                y=peak_val,
                text=f"<b>🔥 Peak {rank+1}위</b><br>{date_label}<br>({peak_val:,}명)",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor="#E50914",
                ax=0,
                ay=-50 - (rank * 10),  # 주석끼리 겹치지 않게 오프셋 부여
                bgcolor="white",
                bordercolor="#E50914",
                borderwidth=1.5,
                borderpad=5,
                opacity=0.9
            )
        
        fig3.update_layout(
            hovermode="x unified",
            xaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
            yaxis=dict(showgrid=True, gridcolor='#f0f0f0', tickformat=","),
            height=500,
            margin=dict(l=20, r=20, t=60, b=20)
        )
        
        st.plotly_chart(fig3, use_container_width=True)
        
        # Top 3 날짜 문구 조합
        top1_str = f"{top3_days.iloc[0]['날짜'].strftime('%Y년 %m월 %d일')}({top3_days.iloc[0]['일관객']:,}명)"
        top2_str = f"{top3_days.iloc[1]['날짜'].strftime('%Y년 %m월 %d일')}({top3_days.iloc[1]['일관객']:,}명)"
        top3_str = f"{top3_days.iloc[2]['날짜'].strftime('%Y년 %m월 %d일')}({top3_days.iloc[2]['일관객']:,}명)"
        
        st.info(f"💡 **이 그래프로 알 수 있는 것**: 1년 중 전체 극장가(Top 10 기준) 관객 동원이 가장 극대화되었던 Peak Top 3 날짜는 **1위 {top1_str}**, **2위 {top2_str}**, **3위 {top3_str}** 입니다. 연휴 및 명절, 대작 개봉일 등 특정 시기 영화 시장 전체의 파이(Market Volume)가 크게 확장되는 지점을 직관적으로 볼 수 있습니다.")
    else:
        st.warning("데이터를 불러올 수 없습니다.")

with tab4:
    st.subheader("📌 섹션 4: 기간 내 총 관객수 TOP 10 영화 (가로 막대그래프)")
    st.write("수집된 기간 동안 10위권 내에서 기록한 일관객수의 합이 가장 큰 상위 10개 영화를 가로 막대그래프로 비교합니다.")
    
    # 영화별 총 관객수 및 TOP 10 진입 일수 집계
    movie_stats = df.groupby('영화명').agg(
        총관객수=('일관객', 'sum'),
        진입일수=('날짜', 'nunique')
    ).reset_index()
    
    # TOP 10 영화 추출
    top10_movies = movie_stats.nlargest(10, '총관객수')
    
    # Plotly 가로 막대 그래프 생성을 위해 관객수 오름차순 정렬 (그래프 상단에 1위가 오도록 설정)
    top10_sorted = top10_movies.sort_values('총관객수', ascending=True)
    
    if not top10_sorted.empty:
        # 1위 영화 정보 추출
        top1_movie = top10_sorted.iloc[-1]['영화명']
        top1_aud = top10_sorted.iloc[-1]['총관객수']
        top1_days = top10_sorted.iloc[-1]['진입일수']
        
        # 요약 메트릭 표시
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("기간 내 1위 영화", top1_movie)
        with col2:
            st.metric("1위 영화 총 관객수", f"{top1_aud:,}명")
        with col3:
            st.metric("1위 영화 TOP 10 진입 일수", f"{top1_days}일")
            
        st.write("")
        
        # Plotly 가로 막대 그래프 생성
        fig4 = px.bar(
            top10_sorted,
            x='총관객수',
            y='영화명',
            orientation='h',
            title="<b>[TOP 10] 기간 내 총 관객수 순위</b>",
            labels={'총관객수': '총 관객수(명)', '영화명': '영화 제목'},
            text='총관객수',
            custom_data=['진입일수'],
            template="plotly_white"
        )
        
        # 막대 스타일 및 툴팁(Hover) 사용자 정의
        fig4.update_traces(
            marker_color='#E50914',
            texttemplate='%{x:,}명',
            textposition='outside',
            hovertemplate="<b>영화명:</b> %{y}<br><b>기간 내 총 관객수:</b> %{x:,}명<br><b>TOP 10 진입 일수:</b> %{customdata[0]}일<extra></extra>"
        )
        
        fig4.update_layout(
            xaxis=dict(showgrid=True, gridcolor='#f0f0f0', tickformat=","),
            yaxis=dict(showgrid=False),
            height=500,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        
        st.plotly_chart(fig4, use_container_width=True)
        
        # 인사이트 문구 박스
        st.info(f"💡 **이 그래프로 알 수 있는 것**: 해당 기간 최다 관객을 동원한 영화 1위는 **{top1_movie}**({top1_aud:,}명, TOP 10 진입 {top1_days}일)입니다. 막대에 마우스를 올리면 각 영화가 TOP 10 박스오피스 순위권에 며칠 동안 머물렀는지 누적 진입 일수를 한눈에 비교할 수 있습니다.")
    else:
        st.warning("데이터를 불러올 수 없습니다.")

with tab5:
    st.subheader("📌 섹션 5: 월×요일별 관객수 분포 (히트맵)")
    st.write("월과 요일에 따른 관객수 합계를 히트맵으로 시각화하여, 극장 관객이 어느 달과 요일에 가장 많이 집중되는지 파악합니다.")
    
    # 데이터 복사 및 월, 요일 추출
    heatmap_df = df.copy()
    heatmap_df['월_num'] = heatmap_df['날짜'].dt.month
    heatmap_df['월'] = heatmap_df['월_num'].astype(str) + "월"
    
    # 요일 이름 매핑 (월요일 ~ 일요일)
    day_map = {0: '월요일', 1: '화요일', 2: '수요일', 3: '목요일', 4: '금요일', 5: '토요일', 6: '일요일'}
    heatmap_df['요일'] = heatmap_df['날짜'].dt.weekday.map(day_map)
    
    # 정렬 순서 정의
    days_order = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
    months_order = [f"{m}월" for m in sorted(heatmap_df['월_num'].unique())]
    
    # 피벗 테이블 생성 (행: 월, 열: 요일, 값: 일관객 합계)
    pivot_df = heatmap_df.pivot_table(
        index='월', 
        columns='요일', 
        values='일관객', 
        aggfunc='sum'
    ).reindex(index=months_order, columns=days_order).fillna(0)
    
    if not pivot_df.empty:
        # 최다 관객 지점(월, 요일) 산출
        max_val = pivot_df.max().max()
        max_month, max_day = pivot_df.stack().idxmax()
        
        # 상단 메트릭
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("최대 관객 집중 월", max_month)
        with col2:
            st.metric("최대 관객 집중 요일", max_day)
        with col3:
            st.metric("해당 월×요일 총 관객수", f"{int(max_val):,}명")
            
        st.write("")
        
        # Plotly Heatmap 생성
        fig5 = px.imshow(
            pivot_df,
            labels=dict(x="요일", y="월", color="총 관객수(명)"),
            x=days_order,
            y=months_order,
            color_continuous_scale="Reds",
            aspect="auto",
            title="<b>[월×요일] 관객수 합계 히트맵</b>",
            text_auto=",.0f"
        )
        
        # 툴팁 및 레이아웃 설정
        fig5.update_traces(
            hovertemplate="<b>%{y} %{x}</b><br>총 관객수: %{z:,}명<extra></extra>"
        )
        
        fig5.update_layout(
            xaxis=dict(tickangle=0),
            yaxis=dict(autorange="reversed"),  # 1월이 상단에 오도록 설정
            height=520,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        
        st.plotly_chart(fig5, use_container_width=True)
        
        # 인사이트 문구 박스
        st.info(f"💡 **이 그래프로 알 수 있는 것**: 분석 대상 기간 중 **{max_month} {max_day}**에 총 **{int(max_val):,}명**으로 관객 집중도가 가장 높았습니다. 색상의 짙은 정도를 통해 주말(토·일요일) 및 특정 흥행 계절(명절, 여름/겨울 성수기 등)의 극장가 관객 몰림 현상을 한눈에 비교할 수 있습니다.")
    else:
        st.warning("데이터를 불러올 수 없습니다.")

st.markdown("---")
st.caption("데이터 출처: 영화진흥위원회(KOBIS) 일별 박스오피스 데이터 | 영화 데이터 그래프 도감 프로젝트")
