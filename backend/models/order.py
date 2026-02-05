from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    dish_id = Column(Integer, ForeignKey('dishes.id'), nullable=False)
    order_date = Column(DateTime, default=datetime.now)
    meal_type = Column(String(20))  # завтрак, обед
    status = Column(String(20), default='pending')  # pending, preparing, served, cancelled
    payment_type = Column(String(20))  # разовый, абонемент
    price = Column(Float, nullable=False)
    served_by = Column(Integer, ForeignKey('users.id'))
    served_at = Column(DateTime)

    # Relationships
    user = relationship('User', foreign_keys=[user_id])
    dish = relationship('Dish')
    server = relationship('User', foreign_keys=[served_by])

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'dish_id': self.dish_id,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'meal_type': self.meal_type,
            'status': self.status,
            'payment_type': self.payment_type,
            'price': self.price,
            'served_by': self.served_by,
            'served_at': self.served_at.isoformat() if self.served_at else None
        }