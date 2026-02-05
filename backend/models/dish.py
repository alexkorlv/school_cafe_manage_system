from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime

Base = declarative_base()

class Dish(Base):
    __tablename__ = 'dishes'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    category = Column(String(50), nullable=False)  # завтрак, обед, напиток
    price = Column(Float, nullable=False)
    ingredients = Column(Text)
    allergens = Column(Text)
    calories = Column(Integer)
    is_available = Column(Boolean, default=True)
    quantity = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'price': self.price,
            'ingredients': self.ingredients,
            'allergens': self.allergens,
            'calories': self.calories,
            'is_available': self.is_available,
            'quantity': self.quantity,
            'rating': self.rating,
            'rating_count': self.rating_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
