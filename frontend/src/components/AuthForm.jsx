import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api.js';

const AuthForm = ({ mode = 'login' }) => {
    const [formData, setFormData] = useState({
        username: '',
        password: '',
        full_name: '',
        class_name: '',
        role: 0 // 0=ученик
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            if (mode === 'login') {
                const response = await api.login(formData.username, formData.password);
                localStorage.setItem('token', response.data.access_token);
                localStorage.setItem('user', JSON.stringify(response.data.user));
                navigate('/dashboard');
            } else {
                await api.register(formData);
                alert('Регистрация успешна! Теперь войдите в систему.');
                navigate('/login');
            }
        } catch (err) {
            setError(err.response?.data?.error || 'Ошибка соединения');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-form">
            <h2>{mode === 'login' ? 'Вход в систему' : 'Регистрация'}</h2>

            {error && <div className="alert alert-danger">{error}</div>}

            <form onSubmit={handleSubmit}>
                <div className="mb-3">
                    <label htmlFor="username" className="form-label">Логин</label>
                    <input
                        type="text"
                        className="form-control"
                        id="username"
                        name="username"
                        value={formData.username}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div className="mb-3">
                    <label htmlFor="password" className="form-label">Пароль</label>
                    <input
                        type="password"
                        className="form-control"
                        id="password"
                        name="password"
                        value={formData.password}
                        onChange={handleChange}
                        required
                    />
                </div>

                {mode === 'register' && (
                    <>
                        <div className="mb-3">
                            <label htmlFor="full_name" className="form-label">ФИО</label>
                            <input
                                type="text"
                                className="form-control"
                                id="full_name"
                                name="full_name"
                                value={formData.full_name}
                                onChange={handleChange}
                                required
                            />
                        </div>

                        <div className="mb-3">
                            <label htmlFor="class_name" className="form-label">Класс</label>
                            <input
                                type="text"
                                className="form-control"
                                id="class_name"
                                name="class_name"
                                value={formData.class_name}
                                onChange={handleChange}
                            />
                        </div>
                    </>
                )}

                <button
                    type="submit"
                    className="btn btn-primary w-100"
                    disabled={loading}
                >
                    {loading ? 'Загрузка...' : (mode === 'login' ? 'Войти' : 'Зарегистрироваться')}
                </button>
            </form>

            {mode === 'login' ? (
                <p className="mt-3 text-center">
                    Нет аккаунта? <a href="/register">Зарегистрироваться</a>
                </p>
            ) : (
                <p className="mt-3 text-center">
                    Есть аккаунт? <a href="/login">Войти</a>
                </p>
            )}
        </div>
    );
};

export default AuthForm;