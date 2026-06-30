import streamlit as st
import pandas as pd
from utils.database import get_user_complaints, save_complaint
from utils.predict import predict_sentiment

def show(user):
    st.title("👤 Customer Portal")
    st.markdown(f"Welcome, **{user.name}**")

    tab1, tab2 = st.tabs(["✍️ Submit Complaint", "📋 My Complaints"])

    with tab1:
        st.subheader("Submit a New Complaint")
        st.markdown("Describe your experience and our system will analyse the sentiment instantly.")

        complaint_text = st.text_area(
            "Your Complaint",
            placeholder="e.g. I tried to send money via M-Pesa but the transaction failed and I was charged twice...",
            height=150
        )

        if st.button("Submit & Analyse"):
            if not complaint_text.strip():
                st.warning("Please enter a complaint before submitting.")
            else:
                with st.spinner("Analysing your complaint..."):
                    result = predict_sentiment(complaint_text)
                    save_complaint(complaint_text, result['sentiment'], result['confidence'], 'manual', user.id)

                sentiment = result['sentiment']
                confidence = int(result['confidence'] * 100)

                if sentiment == 'Positive':
                    st.success(f"😊 Sentiment: **{sentiment}** ({confidence}% confidence)")
                elif sentiment == 'Negative':
                    st.error(f"😠 Sentiment: **{sentiment}** ({confidence}% confidence)")
                else:
                    st.warning(f"😐 Sentiment: **{sentiment}** ({confidence}% confidence)")

    with tab2:
        st.subheader("My Complaint History")
        complaints = get_user_complaints(user.id)

        if not complaints:
            st.info("You have not submitted any complaints yet.")
            return

        df = pd.DataFrame(complaints)
        display_df = df[['text', 'sentiment', 'confidence', 'created_at']].copy()
        display_df['confidence'] = (display_df['confidence'] * 100).astype(int).astype(str) + '%'
        display_df.columns = ['Complaint', 'Sentiment', 'Confidence', 'Date']
        st.dataframe(display_df, use_container_width=True)
