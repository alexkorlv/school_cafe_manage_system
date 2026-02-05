import React, { useState, useEffect } from 'react';
import api from '../services/api.js';

const CookPanel = () => {
    const [activeTab, setActiveTab] = useState('orders');
    const [pendingOrders, setPendingOrders] = useState([]);
    const [purchaseRequests, setPurchaseRequests] = useState([]);
    const [newRequest, setNewRequest] = useState({
        product_name: '',
        quantity: '',
        unit: 'кг',
        reason: ''
    });

    useEffect(() => {
        fetchPendingOrders();
        fetchPurchaseRequests();
    }, []);

    const fetchPendingOrders = async () => {
        try {
            const response = await api.getAllOrders();
            const pending = response.data.filter(order => order.status === 'pending');
            setPendingOrders(pending);
        } catch (error) {
            console.error('Ошибка загрузки заказов:', error);
        }
    };

    const fetchPurchaseRequests = async () => {
        try {
            const response = await api.getPurchaseRequests();
            setPurchaseRequests(response.data);
        } catch (error) {
            console.error('Ошибка загрузки заявок:', error);
        }
    };

    const handleMarkServed = async (orderId) => {
        try {
            await api.markOrderServed(orderId);
            alert('Заказ отмечен как выданный');
            fetchPendingOrders();
        } catch (error) {
            alert('Ошибка обновления статуса');
        }
    };

    const handleCreatePurchaseRequest = async () => {
        try {
            await api.createPurchaseRequest(newRequest);
            alert('Заявка на закупку создана');
            setNewRequest({ product_name: '', quantity: '', unit: 'кг', reason: '' });
            fetchPurchaseRequests();
        } catch (error) {
            alert('Ошибка создания заявки');
        }
    };

    return (
        <div className="cook-panel">
            <h2>Панель повара</h2>

            <div className="tabs">
                <button className={`tab ${activeTab === 'orders' ? 'active' : ''}`} onClick={() => setActiveTab('orders')}>
                    🍽️ Заказы
                </button>
                <button className={`tab ${activeTab === 'purchases' ? 'active' : ''}`} onClick={() => setActiveTab('purchases')}>
                    📝 Заявки на закупку
                </button>
            </div>

            <div className="tab-content">
                {activeTab === 'orders' && (
                    <div>
                        <h3>Ожидающие заказы</h3>
                        {pendingOrders.length === 0 ? (
                            <p className="text-muted">Нет ожидающих заказов</p>
                        ) : (
                            <div className="orders-list">
                                {pendingOrders.map(order => (
                                    <div key={order.id} className="order-card">
                                        <div className="order-header">
                                            <h5>Заказ #{order.id}</h5>
                                            <span className="badge bg-warning">{order.status}</span>
                                        </div>
                                        <div className="order-body">
                                            <p><strong>Блюдо:</strong> {order.dish_name}</p>
                                            <p><strong>Ученик:</strong> {order.user_name}</p>
                                            <p><strong>Сумма:</strong> {order.price} ₽</p>
                                            <p><strong>Дата:</strong> {new Date(order.order_date).toLocaleString()}</p>
                                        </div>
                                        <div className="order-footer">
                                            <button
                                                className="btn btn-success"
                                                onClick={() => handleMarkServed(order.id)}
                                            >
                                                Отметить как выданный
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}

                {activeTab === 'purchases' && (
                    <div className="row">
                        <div className="col-md-6">
                            <h3>Мои заявки</h3>
                            {purchaseRequests.length === 0 ? (
                                <p className="text-muted">Нет созданных заявок</p>
                            ) : (
                                <div className="purchase-list">
                                    {purchaseRequests.map(req => (
                                        <div key={req.id} className={`purchase-card status-${req.status}`}>
                                            <h6>{req.product_name}</h6>
                                            <p><strong>Количество:</strong> {req.quantity} {req.unit}</p>
                                            <p><strong>Статус:</strong>
                                                <span className={`status-badge ${req.status}`}>
                          {req.status === 'pending' ? 'Ожидает' :
                              req.status === 'approved' ? 'Утверждена' : 'Отклонена'}
                        </span>
                                            </p>
                                            {req.admin_comment && (
                                                <p><strong>Комментарий:</strong> {req.admin_comment}</p>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>

                        <div className="col-md-6">
                            <h3>Новая заявка</h3>
                            <div className="new-request-form">
                                <div className="mb-3">
                                    <label className="form-label">Название продукта</label>
                                    <input
                                        type="text"
                                        className="form-control"
                                        value={newRequest.product_name}
                                        onChange={(e) => setNewRequest({...newRequest, product_name: e.target.value})}
                                    />
                                </div>

                                <div className="row mb-3">
                                    <div className="col">
                                        <label className="form-label">Количество</label>
                                        <input
                                            type="number"
                                            className="form-control"
                                            value={newRequest.quantity}
                                            onChange={(e) => setNewRequest({...newRequest, quantity: e.target.value})}
                                            min="1"
                                        />
                                    </div>
                                    <div className="col">
                                        <label className="form-label">Единица измерения</label>
                                        <select
                                            className="form-select"
                                            value={newRequest.unit}
                                            onChange={(e) => setNewRequest({...newRequest, unit: e.target.value})}
                                        >
                                            <option value="кг">кг</option>
                                            <option value="л">л</option>
                                            <option value="шт">шт</option>
                                            <option value="уп">уп</option>
                                        </select>
                                    </div>
                                </div>

                                <div className="mb-3">
                                    <label className="form-label">Причина закупки</label>
                                    <textarea
                                        className="form-control"
                                        rows="3"
                                        value={newRequest.reason}
                                        onChange={(e) => setNewRequest({...newRequest, reason: e.target.value})}
                                    />
                                </div>

                                <button
                                    className="btn btn-primary w-100"
                                    onClick={handleCreatePurchaseRequest}
                                    disabled={!newRequest.product_name || !newRequest.quantity}
                                >
                                    Создать заявку
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default CookPanel;