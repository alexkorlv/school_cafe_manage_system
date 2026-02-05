from datetime import datetime
from sqlalchemy import Column, Integer, Float, Date, Boolean, ForeignKey

Base = declarative_base()

class Subscription(Base):
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    meals_left = Column(Integer, nullable=False)
    total_meals = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'meals_left': self.meals_left,
            'total_meals': self.total_meals,
            'price': self.price,
            'is_active': self.is_active
        }