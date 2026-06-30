"""
Sentiment prediction using TextBlob polarity scoring,
matching the methodology from tz_complaint_analysis.ipynb
(Step 5.1 - TextBlob Polarity Score)
"""
from textblob import TextBlob


def get_polarity(text):
    return TextBlob(str(text)).sentiment.polarity


def polarity_to_label(score):
    if score > 0.05:
        return 'Positive'
    elif score < -0.05:
        return 'Negative'
    else:
        return 'Neutral'


def predict_sentiment(text):
    """Returns sentiment + confidence derived from TextBlob polarity,
    same rule used in the notebook (Step 5.1)."""
    score = get_polarity(text)
    sentiment = polarity_to_label(score)
    # Map polarity (-1 to 1) into a confidence-style score (0.5 to 1.0)
    confidence = round(0.5 + min(abs(score), 1.0) / 2, 2)
    return {'sentiment': sentiment, 'confidence': confidence, 'polarity': round(score, 3)}


def predict_bulk(texts):
    return [predict_sentiment(str(t)) for t in texts]


def model_files_exist():
    # Kept for backward compatibility with the admin upload UI
    return False
