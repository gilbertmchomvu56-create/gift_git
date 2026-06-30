import streamlit as st
import pandas as pd
import plotly.express as px
from utils.database import get_all_complaints

def show():
    st.title("📊 Admin Dashboard")
    st.markdown("Full system overview — all complaints across all users")

    st.success("🤖 **Model active:** TextBlob polarity-based sentiment analysis (from `tz_complaint_analysis.ipynb`, Step 5.1)")

    complaints = get_all_complaints()

    if not complaints:
        st.info("No complaints in the system yet.")
        return

    df = pd.DataFrame(complaints)

    total = len(df)
    positive = len(df[df['sentiment'] == 'Positive'])
    negative = len(df[df['sentiment'] == 'Negative'])
    neutral = len(df[df['sentiment'] == 'Neutral'])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Complaints", total)
    col2.metric("😊 Positive", positive)
    col3.metric("😠 Negative", negative)
    col4.metric("😐 Neutral", neutral)

    st.divider()

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Sentiment Distribution")
        fig = px.pie(df, names='sentiment', color='sentiment',
                     color_discrete_map={'Positive': '#22c55e', 'Negative': '#ef4444', 'Neutral': '#f59e0b'})
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("Complaints by Source")
        source_df = df['source'].value_counts().reset_index()
        source_df.columns = ['Source', 'Count']
        fig2 = px.bar(source_df, x='Source', y='Count', color_discrete_sequence=['#2563eb'])
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    st.subheader("📈 Sentiment Trend Over Time")

    trend_df = df.copy()
    trend_df['date'] = pd.to_datetime(trend_df['created_at']).dt.date
    trend_counts = trend_df.groupby(['date', 'sentiment']).size().reset_index(name='count')

    fig3 = px.line(trend_counts, x='date', y='count', color='sentiment', markers=True,
                   color_discrete_map={'Positive': '#22c55e', 'Negative': '#ef4444', 'Neutral': '#f59e0b'})
    fig3.update_layout(xaxis_title="Date", yaxis_title="Number of Complaints")
    st.plotly_chart(fig3, use_container_width=True)

    st.divider()
    st.subheader("All Complaints")

    display_df = df[['text', 'sentiment', 'confidence', 'source', 'created_at']].copy()
    display_df['confidence'] = (display_df['confidence'] * 100).astype(int).astype(str) + '%'
    display_df.columns = ['Complaint', 'Sentiment', 'Confidence', 'Source', 'Date']
    st.dataframe(display_df, use_container_width=True)

    st.download_button(
        label="📥 Download All as CSV",
        data=display_df.to_csv(index=False),
        file_name="all_complaints.csv",
        mime="text/csv"
    )
