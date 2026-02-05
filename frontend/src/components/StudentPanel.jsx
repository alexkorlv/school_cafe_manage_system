import React, { useState, useEffect } from 'react';
import api from '../services/api.js';
import MenuList from './MenuList.jsx';
import OrderList from './OrderList';
import Profile from './Profile';

const StudentPanel = () => {
    const [activeTab, setActiveTab] = useState('menu');
    const [balance, setBalance] = useState(0);
    const [topupAmount, setTopupAmount] = useState(100);
    const [orders, setOrders] = useState([]);

    useEffect(() => {
        fetchUserData();
        fetchOrders();
    }, []);

    const fetchUserData = async () => {
        try {
            const response = await api.getProfile();
            setBalance(response.data.balance);
        } catch (error) {
            console.error('Ошибка загрузки данных:', error);
        }
    };

    const fetchOrders = async () => {
        try {
            const response = await api.getMyOrders();
            setOrders(response.data);
        } catch (error) {
            console.error('Ошибка загрузки заказов:', error);
        }
    };

    const handleTopup = async () => {
        try {
            await api.topupBalance(topupAmount);
            alert(`Баланс пополнен на ${topupAmount} руб.`);
            fetchUserData();
        } catch (error) {
            alert('Ошибка пополнения баланса');
        }
    };

    const handleOrder = async (dishId) => {
        try {
            const mealType = prompt('Тип питания (завтрак/обед):', 'обед');
            const paymentType = prompt('Тип оплаты (разовый/абонемент):', 'разовый');

            if (!mealType || !paymentType) return;

            await api.createOrder(dishId, mealType, paymentType);
            alert('Заказ создан успешно!');
            fetchOrders();
            fetchUserData();
        } catch (error) {
            alert(error.response?.data?.error || 'Ошибка создания заказа');
        }
    };

    return (
        <div className="student-panel">
            <div className="dashboard-header">
                <h2>Панель ученика</h2>
                <div className="balance-info">
                    <span className="balance-label">Баланс:</span>
                    <span className="balance-amount">{balance} ₽</span>
                </div>
            </div>

            <div className="tabs">
                <button
                    className={`tab ${activeTab === 'menu' ? 'active' : ''}`}
                    onClick={() => setActiveTab('menu')}
                >
                    📋 Меню
                </button>
                <button
                    className={`tab ${activeTab === 'orders' ? 'active' : ''}`}
                    onClick={() => setActiveTab('orders')}
                >
                    📦 Мои заказы
                </button>
                <button
                    className={`tab ${activeTab === 'profile' ? 'active' : ''}`}
                    onClick={() => setActiveTab('profile')}
                >
                    👤 Профиль
                </button>
                <button
                    className={`tab ${activeTab === 'topup' ? 'active' : ''}`}
                    onClick={() => setActiveTab('topup')}
                >
                    💰 Пополнить баланс
                </button>
            </div>

            <div className="tab-content">
                {activeTab === 'menu' && (
                    <div>
                        <h3>Меню столовой</h3>
                        <MenuList onOrder={handleOrder} />
                    </div>
                )}

                {activeTab === 'orders' && (
                    <div>
                        <h3>Мои заказы</h3>
                        <OrderList orders={orders} />
                    </div>
                )}

                {activeTab === 'profile' && (
                    <div>
                        <h3>Мой профиль</h3>
                        <Profile />
                    </div>
                )}

                {activeTab === 'topup' && (
                    <div className="topup-section">
                        <h3>Пополнение баланса</h3>
                        <div className="topup-form">
                            <div className="mb-3">
                                <label className="form-label">Сумма пополнения (руб.)</label>
                                <input
                                    type="number"
                                    className="form-control"
                                    value={topupAmount}
                                    onChange={(e) => setTopupAmount(parseInt(e.target.value))}
                                    min="1"
                                    max="10000"
                                />
                            </div>

                            <div className="quick-amounts mb-3">
                                <button className="btn btn-outline-primary" onClick={() => setTopupAmount(100)}>100 ₽</button>
                                <button className="btn btn-outline-primary" onClick={() => setTopupAmount(500)}>500 ₽</button>
                                <button className="btn btn-outline-primary" onClick={() => setTopupAmount(1000)}>1000 ₽</button>
                            </div>

                            <button className="btn btn-success w-100" onClick={handleTopup}>
                                Пополнить на {topupAmount} ₽
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default StudentPanel;