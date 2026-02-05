from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(Integer, nullable=False)  # 0=ученик, 1=повар, 2=админ
    class_name = Column(String(20))
    balance = Column(Float, default=0.0)
    allergies = Column(Text)
    dietary_preferences = Column(Text)
    email = Column(String(100))
    phone = Column(String(20))
    created_at = Column(DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'role': self.role,
            'class_name': self.class_name,
            'balance': self.balance,
            'allergies': self.allergies,
            'dietary_preferences': self.dietary_preferences,
            'email': self.email,
            'phone': self.phone,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }