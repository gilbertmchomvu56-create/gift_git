import streamlit as st
import pandas as pd
import plotly.express as px
from utils.database import get_user_complaints, save_complaint
from utils.predict import predict_bulk

def show(user):
    st.title("🏢 Company Dashboard")
    st.markdown(f"Welcome, **{user.name}** — upload and analyse your complaint data")

    tab1, tab2 = st.tabs(["📊 My Analytics", "📂 Upload CSV"])

    with tab1:
        complaints = get_user_complaints(user.id)

        if not complaints:
            st.info("No complaints yet. Upload a CSV file to get started.")
            return

        df = pd.DataFrame(complaints)
        total = len(df)
        positive = len(df[df['sentiment'] == 'Positive'])
        negative = len(df[df['sentiment'] == 'Negative'])
        neutral = len(df[df['sentiment'] == 'Neutral'])

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total", total)
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
            st.subheader("Sentiment Breakdown")
            bar_df = df['sentiment'].value_counts().reset_index()
            bar_df.columns = ['Sentiment', 'Count']
            fig2 = px.bar(bar_df, x='Sentiment', y='Count', color='Sentiment',
                          color_discrete_map={'Positive': '#22c55e', 'Negative': '#ef4444', 'Neutral': '#f59e0b'})
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

        st.subheader("Your Complaints")
        display_df = df[['text', 'sentiment', 'confidence', 'created_at']].copy()
        display_df['confidence'] = (display_df['confidence'] * 100).astype(int).astype(str) + '%'
        display_df.columns = ['Complaint', 'Sentiment', 'Confidence', 'Date']
        st.dataframe(display_df, use_container_width=True)

        st.download_button(
            label="📥 Download My CSV",
            data=display_df.to_csv(index=False),
            file_name="my_complaints.csv",
            mime="text/csv"
        )

    with tab2:
        st.subheader("Upload Complaints CSV")
        st.info('Your CSV must have a column named **complaint**')

        uploaded = st.file_uploader("Choose CSV file", type=['csv'])

        if uploaded:
            df_upload = pd.read_csv(uploaded)

            if 'complaint' not in df_upload.columns:
                st.error('CSV must have a "complaint" column!')
                return

            st.write(f"**{len(df_upload)} complaints found. Preview:**")
            st.dataframe(df_upload.head(), use_container_width=True)

            if st.button("🔍 Analyse All Complaints"):
                with st.spinner('Analysing complaints...'):
                    texts = df_upload['complaint'].tolist()
                    results = predict_bulk(texts)
                    for text, result in zip(texts, results):
                        save_complaint(str(text), result['sentiment'], result['confidence'], 'csv_upload', user.id)

                st.success(f"✅ {len(texts)} complaints analysed and saved!")
                st.balloons()
