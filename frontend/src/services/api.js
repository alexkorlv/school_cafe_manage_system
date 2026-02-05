import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: true,
});


api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);


api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

export default {
    healthCheck: () => api.get('/health'),


    testApi: () => api.get('/test'),


    login: (username, password) =>
        api.post('/auth/login', { username, password }),

    register: (data) =>
        api.post('/auth/register', data),


    getProfile: () =>
        api.get('/user/profile'),

    updateProfile: (data) =>
        api.put('/user/profile', data),


    getMenu: (category) =>
        api.get(`/menu${category ? `?category=${category}` : ''}`),

    getDish: (id) =>
        api.get(`/menu/${id}`),


    createOrder: (dishId, mealType, paymentType) =>
        api.post('/orders', { dish_id: dishId, meal_type: mealType, payment_type: paymentType }),

    getMyOrders: () =>
        api.get('/orders/my'),

    getAllOrders: () =>
        api.get('/orders/all'),

    markOrderServed: (orderId) =>
        api.post(`/orders/${orderId}/mark-served`),


    topupBalance: (amount) =>
        api.post('/balance/topup', { amount }),

    createSubscription: (data) =>
        api.post('/subscriptions', data),


    createReview: (dishId, rating, comment) =>
        api.post('/reviews', { dish_id: dishId, rating, comment }),


    createPurchaseRequest: (data) =>
        api.post('/purchases', data),

    getPurchaseRequests: () =>
        api.get('/purchases'),

    processPurchaseRequest: (requestId, action, comment) => {
        if (action === 'approve') {
            return api.post(`/purchases/${requestId}/approve`, { comment });
        } else if (action === 'reject') {
            return api.post(`/purchases/${requestId}/reject`, { comment });
        }
        return Promise.reject(new Error('Invalid action'));
    },


    getFinancialReport: () =>
        api.get('/reports/summary'),

    getNutritionReport: () =>
        api.get('/reports/detailed'),


    testDoubleOrder: () =>
        api.post('/test/double-order'),
};