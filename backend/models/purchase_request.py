from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey

Base = declarative_base()

class PurchaseRequest(Base):
    __tablename__ = 'purchase_requests'

    id = Column(Integer, primary_key=True)
    cook_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    product_name = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit = Column(String(20), nullable=False)  # кг, л, шт
    reason = Column(Text)
    status = Column(String(20), default='pending')  # pending, approved, rejected
    admin_id = Column(Integer, ForeignKey('users.id'))
    admin_comment = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'cook_id': self.cook_id,
            'product_name': self.product_name,
            'quantity': self.quantity,
            'unit': self.unit,
            'reason': self.reason,
            'status': self.status,
            'admin_id': self.admin_id,
            'admin_comment': self.admin_comment,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }