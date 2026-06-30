from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

Base = declarative_base()
engine = create_engine('sqlite:////home/claude/complaintsense/complaints.db', connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(150), unique=True)
    password = Column(String(200))
    role = Column(String(20))

class Complaint(Base):
    __tablename__ = 'complaints'
    id = Column(Integer, primary_key=True)
    text = Column(Text)
    sentiment = Column(String(20))
    confidence = Column(Float)
    source = Column(String(50))
    user_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(engine)
    session = Session()
    existing = session.query(User).filter_by(email='admin@complaintsense.com').first()
    if not existing:
        admin = User(
            name='Super Admin',
            email='admin@complaintsense.com',
            password=generate_password_hash('admin123'),
            role='admin'
        )
        session.add(admin)
        # Add sample complaints - sentiment computed live via TextBlob (utils/predict.py)
        from utils.predict import predict_sentiment
        sample_texts = [
            'Vodacom failed to process my payment twice and I lost money',
            'NMB bank transfer was fast and seamless, very happy!',
            'Tigo Pesa keeps giving me errors when I try to withdraw',
            'CRDB mobile app is excellent and very helpful',
            'My transaction is pending for 3 days, terrible service',
            'Great customer support from Vodacom, problem solved fast',
            'The system was down during my transfer',
            'Charges were deducted but transfer did not go through',
            'Amazing service, best mobile money platform in Tanzania',
            'Transaction took longer than usual but eventually worked',
        ]
        for text in sample_texts:
            result = predict_sentiment(text)
            session.add(Complaint(
                text=text,
                sentiment=result['sentiment'],
                confidence=result['confidence'],
                source='csv_upload',
                user_id=1
            ))
        session.commit()
    session.close()

def get_session():
    return Session()

def register_user(name, email, password, role):
    session = Session()
    existing = session.query(User).filter_by(email=email).first()
    if existing:
        session.close()
        return False, 'Email already registered'
    user = User(name=name, email=email, password=generate_password_hash(password), role=role)
    session.add(user)
    session.commit()
    session.close()
    return True, 'Account created successfully'

def login_user(email, password):
    session = Session()
    user = session.query(User).filter_by(email=email).first()
    session.close()
    if user and check_password_hash(user.password, password):
        return True, user
    return False, None

def save_complaint(text, sentiment, confidence, source, user_id):
    session = Session()
    complaint = Complaint(text=text, sentiment=sentiment, confidence=confidence, source=source, user_id=user_id)
    session.add(complaint)
    session.commit()
    session.close()

def get_all_complaints():
    session = Session()
    complaints = session.query(Complaint).all()
    data = [{'id': c.id, 'text': c.text, 'sentiment': c.sentiment,
              'confidence': c.confidence, 'source': c.source,
              'user_id': c.user_id, 'created_at': c.created_at} for c in complaints]
    session.close()
    return data

def get_user_complaints(user_id):
    session = Session()
    complaints = session.query(Complaint).filter_by(user_id=user_id).all()
    data = [{'id': c.id, 'text': c.text, 'sentiment': c.sentiment,
              'confidence': c.confidence, 'source': c.source,
              'created_at': c.created_at} for c in complaints]
    session.close()
    return data
