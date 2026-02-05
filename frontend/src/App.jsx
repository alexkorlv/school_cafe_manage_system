import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import 'bootstrap/dist/css/bootstrap.min.css';

import AuthForm from './components/AuthForm.jsx';
import StudentPanel from './components/StudentPanel.jsx';
import CookPanel from './components/CookPanel.jsx';
import AdminPanel from './components/AdminPanel.jsx';
import ProtectedRoute from './components/ProtectedRoute.jsx';
import Header from './components/Header';
import Footer from './components/Footer';

import './styles/App.css';

const App = () => {
    const user = JSON.parse(localStorage.getItem('user') || '{}');

    const getDefaultRoute = () => {
        if (!user.role && user.role !== 0) return '/login';

        switch(user.role) {
            case 0: return '/student';
            case 1: return '/cook';
            case 2: return '/admin';
            default: return '/login';
        }
    };

    return (
        <Router>
            <div className="app">
                <Header />

                <main className="main-content">
                    <Routes>
                        <Route path="/" element={<Navigate to={getDefaultRoute()} />} />
                        <Route path="/login" element={<AuthForm mode="login" />} />
                        <Route path="/register" element={<AuthForm mode="register" />} />

                        <Route path="/student" element={
                            <ProtectedRoute requiredRole={0}>
                                <StudentPanel />
                            </ProtectedRoute>
                        } />

                        <Route path="/cook" element={
                            <ProtectedRoute requiredRole={1}>
                                <CookPanel />
                            </ProtectedRoute>
                        } />

                        <Route path="/admin" element={
                            <ProtectedRoute requiredRole={2}>
                                <AdminPanel />
                            </ProtectedRoute>
                        } />

                        <Route path="/dashboard" element={
                            <ProtectedRoute>
                                <Navigate to={getDefaultRoute()} />
                            </ProtectedRoute>
                        } />

                        <Route path="*" element={<Navigate to="/" />} />
                    </Routes>
                </main>

                <Footer />
                <ToastContainer position="top-right" autoClose={3000} />
            </div>
        </Router>
    );
};

export default App;