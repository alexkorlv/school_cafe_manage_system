import React, { useState, useEffect } from 'react';
import api from '../services/api.js';

const MenuList = ({ onOrder }) => {
    const [dishes, setDishes] = useState([]);
    const [filter, setFilter] = useState('all');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchMenu();
    }, []);

    const fetchMenu = async () => {
        try {
            const response = await api.getMenu();
            setDishes(response.data);
        } catch (error) {
            console.error('Ошибка загрузки меню:', error);
        } finally {
            setLoading(false);
        }
    };

    const filteredDishes = filter === 'all'
        ? dishes
        : dishes.filter(dish => dish.category === filter);

    const categories = ['all', 'завтрак', 'обед', 'напиток'];

    if (loading) {
        return <div className="text-center">Загрузка меню...</div>;
    }

    return (
        <div className="menu-list">
            <div className="filters mb-4">
                {categories.map(category => (
                    <button
                        key={category}
                        className={`btn ${filter === category ? 'btn-primary' : 'btn-outline-primary'}`}
                        onClick={() => setFilter(category)}
                    >
                        {category === 'all' ? 'Все' : category}
                    </button>
                ))}
            </div>

            <div className="row">
                {filteredDishes.length === 0 ? (
                    <div className="col-12">
                        <p className="text-muted">Нет доступных блюд в этой категории</p>
                    </div>
                ) : (
                    filteredDishes.map(dish => (
                        <div key={dish.id} className="col-md-4 mb-4">
                            <div className="card h-100">
                                <div className="card-body">
                                    <h5 className="card-title">{dish.name}</h5>
                                    <p className="card-text text-muted">{dish.description}</p>

                                    <div className="dish-info">
                                        <span className="badge bg-secondary">{dish.category}</span>
                                        {dish.allergens && (
                                            <span className="badge bg-warning ms-2">⚠️ {dish.allergens}</span>
                                        )}
                                    </div>

                                    <div className="mt-3">
                                        <p><strong>Состав:</strong> {dish.ingredients}</p>
                                        {dish.calories && (
                                            <p><strong>Калории:</strong> {dish.calories} ккал</p>
                                        )}
                                    </div>

                                    <div className="d-flex justify-content-between align-items-center mt-3">
                                        <div>
                                            <div className="price">{dish.price} ₽</div>
                                            <div className="quantity text-muted small">
                                                В наличии: {dish.quantity} шт
                                            </div>
                                        </div>

                                        {onOrder && dish.quantity > 0 && (
                                            <button
                                                className="btn btn-success"
                                                onClick={() => {
                                                    console.log('Кнопка нажата, dish.id:', dish.id);
                                                    onOrder(dish.id);
                                                }}
                                            >
                                                Заказать
                                            </button>
                                        )}

                                        {onOrder && dish.quantity <= 0 && (
                                            <button className="btn btn-secondary" disabled>
                                                Нет в наличии
                                            </button>
                                        )}
                                    </div>

                                    {dish.rating_count > 0 && (
                                        <div className="mt-3">
                                            <div className="rating">
                                                <span className="text-warning">★ {dish.rating.toFixed(1)}</span>
                                                <span className="text-muted ms-2">({dish.rating_count} отзывов)</span>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default MenuList;