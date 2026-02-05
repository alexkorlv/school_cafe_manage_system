import React, { useState, useEffect } from 'react';
import api from '../services/api.js';
import { Bar, Pie } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement);

const AdminPanel = () => {
    const [activeTab, setActiveTab] = useState('dashboard');
    const [purchaseRequests, setPurchaseRequests] = useState([]);
    const [financialReport, setFinancialReport] = useState(null);
    const [nutritionReport, setNutritionReport] = useState(null);
    const [adminComment, setAdminComment] = useState('');

    useEffect(() => {
        fetchPurchaseRequests();
        fetchReports();
    }, []);

    const fetchPurchaseRequests = async () => {
        try {
            const response = await api.getPurchaseRequests();
            setPurchaseRequests(response.data);
        } catch (error) {
            console.error('Ошибка загрузки заявок:', error);
        }
    };

    const fetchReports = async () => {
        try {
            const financial = await api.getFinancialReport();
            const nutrition = await api.getNutritionReport();
            setFinancialReport(financial.data);
            setNutritionReport(nutrition.data);
        } catch (error) {
            console.error('Ошибка загрузки отчетов:', error);
        }
    };

    const handleProcessRequest = async (requestId, action) => {
        try {
            await api.processPurchaseRequest(requestId, action, adminComment);
            alert(`Заявка ${action === 'approve' ? 'утверждена' : 'отклонена'}`);
            fetchPurchaseRequests();
            setAdminComment('');
        } catch (error) {
            alert('Ошибка обработки заявки');
        }
    };


    const financialChartData = financialReport ? {
        labels: ['Общая выручка', 'Средний чек', 'Уникальные клиенты'],
        datasets: [{
            label: 'Финансовые показатели',
            data: [
                financialReport.summary.total_revenue || 0,
                financialReport.summary.avg_order_price || 0,
                financialReport.summary.unique_customers || 0
            ],
            backgroundColor: ['#36A2EB', '#FF6384', '#4BC0C0']
        }]
    } : null;

    const nutritionChartData = nutritionReport ? {
        labels: nutritionReport.popular_dishes?.slice(0, 5).map(d => d.name) || [],
        datasets: [{
            label: 'Количество заказов',
            data: nutritionReport.popular_dishes?.slice(0, 5).map(d => d.order_count) || [],
            backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF']
        }]
    } : null;

    return (
        <div className="admin-panel">
            <h2>Панель администратора</h2>

            <div className="tabs">
                <button className={`tab ${activeTab === 'dashboard' ? 'active' : ''}`} onClick={() => setActiveTab('dashboard')}>
                    📊 Дашборд
                </button>
                <button className={`tab ${activeTab === 'purchases' ? 'active' : ''}`} onClick={() => setActiveTab('purchases')}>
                    📝 Заявки на закупку
                </button>
                <button className={`tab ${activeTab === 'reports' ? 'active' : ''}`} onClick={() => setActiveTab('reports')}>
                    📈 Отчеты
                </button>
            </div>

            <div className="tab-content">
                {activeTab === 'dashboard' && (
                    <div className="dashboard">
                        <div className="row">
                            {financialReport && (
                                <div className="col-md-6">
                                    <div className="card">
                                        <div className="card-header">
                                            <h5>Финансовые показатели</h5>
                                        </div>
                                        <div className="card-body">
                                            <Bar data={financialChartData} options={{ responsive: true }} />
                                        </div>
                                    </div>
                                </div>
                            )}

                            {nutritionReport && (
                                <div className="col-md-6">
                                    <div className="card">
                                        <div className="card-header">
                                            <h5>Популярные блюда</h5>
                                        </div>
                                        <div className="card-body">
                                            <Pie data={nutritionChartData} options={{ responsive: true }} />
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {activeTab === 'purchases' && (
                    <div>
                        <h3>Заявки на закупку</h3>
                        {purchaseRequests.length === 0 ? (
                            <p className="text-muted">Нет заявок на рассмотрение</p>
                        ) : (
                            <div className="purchase-requests-admin">
                                {purchaseRequests.filter(req => req.status === 'pending').map(req => (
                                    <div key={req.id} className="request-card">
                                        <div className="request-header">
                                            <h5>Заявка #{req.id} от {req.cook_name}</h5>
                                            <span className="badge bg-warning">Ожидает</span>
                                        </div>
                                        <div className="request-body">
                                            <p><strong>Продукт:</strong> {req.product_name}</p>
                                            <p><strong>Количество:</strong> {req.quantity} {req.unit}</p>
                                            <p><strong>Причина:</strong> {req.reason}</p>
                                            <p><strong>Дата создания:</strong> {new Date(req.created_at).toLocaleString()}</p>
                                        </div>
                                        <div className="request-footer">
                                            <div className="mb-3">
                                                <label className="form-label">Комментарий администратора</label>
                                                <textarea
                                                    className="form-control"
                                                    rows="2"
                                                    value={adminComment}
                                                    onChange={(e) => setAdminComment(e.target.value)}
                                                    placeholder="Введите комментарий..."
                                                />
                                            </div>
                                            <div className="d-flex gap-2">
                                                <button
                                                    className="btn btn-success"
                                                    onClick={() => handleProcessRequest(req.id, 'approve')}
                                                >
                                                    Утвердить
                                                </button>
                                                <button
                                                    className="btn btn-danger"
                                                    onClick={() => handleProcessRequest(req.id, 'reject')}
                                                >
                                                    Отклонить
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                ))}

                                <h4 className="mt-5">История заявок</h4>
                                <div className="requests-history">
                                    {purchaseRequests.filter(req => req.status !== 'pending').map(req => (
                                        <div key={req.id} className="request-history-item">
                                            <div className="d-flex justify-content-between align-items-center">
                                                <div>
                                                    <strong>{req.product_name}</strong> - {req.quantity} {req.unit}
                                                    <div className="text-muted small">
                                                        {req.cook_name} • {new Date(req.created_at).toLocaleDateString()}
                                                    </div>
                                                </div>
                                                <span className={`badge ${req.status === 'approved' ? 'bg-success' : 'bg-danger'}`}>
                          {req.status === 'approved' ? 'Утверждена' : 'Отклонена'}
                        </span>
                                            </div>
                                            {req.admin_comment && (
                                                <div className="mt-2">
                                                    <small><strong>Комментарий:</strong> {req.admin_comment}</small>
                                                </div>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {activeTab === 'reports' && (
                    <div className="reports">
                        <div className="row">
                            <div className="col-md-6">
                                <div className="card">
                                    <div className="card-header">
                                        <h5>Финансовый отчет</h5>
                                    </div>
                                    <div className="card-body">
                                        {financialReport ? (
                                            <div>
                                                <div className="report-item">
                                                    <span>Общая выручка:</span>
                                                    <strong>{financialReport.summary.total_revenue || 0} ₽</strong>
                                                </div>
                                                <div className="report-item">
                                                    <span>Количество заказов:</span>
                                                    <strong>{financialReport.summary.total_orders || 0}</strong>
                                                </div>
                                                <div className="report-item">
                                                    <span>Средний чек:</span>
                                                    <strong>{financialReport.summary.avg_order_price?.toFixed(2) || 0} ₽</strong>
                                                </div>
                                                <div className="report-item">
                                                    <span>Уникальные клиенты:</span>
                                                    <strong>{financialReport.summary.unique_customers || 0}</strong>
                                                </div>
                                            </div>
                                        ) : (
                                            <p>Загрузка...</p>
                                        )}
                                    </div>
                                </div>
                            </div>

                            <div className="col-md-6">
                                <div className="card">
                                    <div className="card-header">
                                        <h5>Отчет по питанию</h5>
                                    </div>
                                    <div className="card-body">
                                        {nutritionReport ? (
                                            <div>
                                                <h6>Популярные блюда:</h6>
                                                <ul className="list-group">
                                                    {nutritionReport.popular_dishes?.slice(0, 5).map((dish, index) => (
                                                        <li key={index} className="list-group-item d-flex justify-content-between">
                                                            <span>{dish.name}</span>
                                                            <span className="badge bg-primary">{dish.order_count} заказов</span>
                                                        </li>
                                                    ))}
                                                </ul>
                                            </div>
                                        ) : (
                                            <p>Загрузка...</p>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default AdminPanel;