import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from contextlib import contextmanager

# -----------------------------
# DATABASE SETUP
# -----------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.normpath(os.path.join(BASE_DIR, "..", "complaints.db"))

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False}
)

Session = sessionmaker(bind=engine)
Base = declarative_base()


# -----------------------------
# MODELS
# -----------------------------

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


# -----------------------------
# SAFE SESSION HANDLER
# -----------------------------

@contextmanager
def get_session():
    session = Session()
    try:
        yield session
        session.commit()
    finally:
        session.close()


# -----------------------------
# DATABASE INIT (FIXED)
# -----------------------------

def init_db():
    # IMPORTANT FIX: prevents "table already exists" error
    Base.metadata.create_all(engine, checkfirst=True)

    with get_session() as session:
        existing = session.query(User).filter_by(
            email='admin@complaintsense.com'
        ).first()

        if not existing:
            from utils.predict import predict_sentiment

            admin = User(
                name='Super Admin',
                email='admin@complaintsense.com',
                password=generate_password_hash('admin123'),
                role='admin'
            )
            session.add(admin)

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
                    source='seed_data',
                    user_id=1
                ))


# -----------------------------
# USER FUNCTIONS
# -----------------------------

def register_user(name, email, password, role):
    with get_session() as session:
        existing = session.query(User).filter_by(email=email).first()

        if existing:
            return False, 'Email already registered'

        user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            role=role
        )

        session.add(user)
        return True, 'Account created successfully'


def login_user(email, password):
    with get_session() as session:
        user = session.query(User).filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            return True, user

        return False, None


# -----------------------------
# COMPLAINT FUNCTIONS
# -----------------------------

def save_complaint(text, sentiment, confidence, source, user_id):
    with get_session() as session:
        complaint = Complaint(
            text=text,
            sentiment=sentiment,
            confidence=confidence,
            source=source,
            user_id=user_id
        )
        session.add(complaint)


def get_all_complaints():
    with get_session() as session:
        complaints = session.query(Complaint).all()

        return [
            {
                'id': c.id,
                'text': c.text,
                'sentiment': c.sentiment,
                'confidence': c.confidence,
                'source': c.source,
                'user_id': c.user_id,
                'created_at': c.created_at
            }
            for c in complaints
        ]


def get_user_complaints(user_id):
    with get_session() as session:
        complaints = session.query(Complaint).filter_by(user_id=user_id).all()

        return [
            {
                'id': c.id,
                'text': c.text,
                'sentiment': c.sentiment,
                'confidence': c.confidence,
                'source': c.source,
                'created_at': c.created_at
            }
            for c in complaints
        ]
