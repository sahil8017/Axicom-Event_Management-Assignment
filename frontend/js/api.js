// API Utility Functions for Event Management System

const API_BASE = '/api';

// Get auth token from localStorage
function getToken() {
    return localStorage.getItem('authToken');
}

// Set auth token
function setToken(token) {
    localStorage.setItem('authToken', token);
}

// Clear auth data
function clearAuth() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
}

// Get current user
function getCurrentUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
}

// Set current user
function setCurrentUser(user) {
    localStorage.setItem('user', JSON.stringify(user));
}

// API request helper
async function apiRequest(endpoint, method = 'GET', data = null) {
    const headers = {
        'Content-Type': 'application/json'
    };

    const token = getToken();
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const options = {
        method,
        headers
    };

    if (data && method !== 'GET') {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        const result = await response.json();

        if (!response.ok) {
            // Handle validation errors (422) which have array of errors
            let errorMessage = 'Request failed';
            if (result.detail) {
                if (typeof result.detail === 'string') {
                    errorMessage = result.detail;
                } else if (Array.isArray(result.detail)) {
                    // Pydantic validation errors
                    errorMessage = result.detail.map(err => {
                        const field = err.loc ? err.loc.join('.') : 'field';
                        return `${field}: ${err.msg}`;
                    }).join(', ');
                } else if (typeof result.detail === 'object') {
                    errorMessage = JSON.stringify(result.detail);
                }
            }
            throw new Error(errorMessage);
        }

        return result;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Auth API
const authAPI = {
    login: (email, password) => apiRequest('/auth/login', 'POST', { email, password }),
    register: (data) => apiRequest('/auth/register', 'POST', data),
    registerVendor: (data) => apiRequest('/auth/register-vendor', 'POST', data),
    getMe: () => apiRequest('/auth/me')
};

// Admin API
const adminAPI = {
    listUsers: () => apiRequest('/admin/users'),
    createUser: (data) => apiRequest('/admin/users', 'POST', data),
    updateUser: (id, data) => apiRequest(`/admin/users/${id}`, 'PUT', data),
    deleteUser: (id) => apiRequest(`/admin/users/${id}`, 'DELETE'),
    listVendors: () => apiRequest('/admin/vendors'),
    updateVendor: (id, data) => apiRequest(`/admin/vendors/${id}`, 'PUT', data),
    updateMembership: (id, data) => apiRequest(`/admin/memberships/${id}`, 'PUT', data),
    activateAllVendors: () => apiRequest('/admin/memberships/activate-all', 'PUT'),
    // Product approval
    listItems: () => apiRequest('/admin/items'),
    approveItem: (id) => apiRequest(`/admin/items/${id}/approve`, 'PUT'),
    rejectItem: (id) => apiRequest(`/admin/items/${id}/reject`, 'PUT'),
    deleteItem: (id) => apiRequest(`/admin/items/${id}`, 'DELETE')
};

// Vendor API
const vendorAPI = {
    getProfile: () => apiRequest('/vendor/profile'),
    listItems: () => apiRequest('/vendor/items'),
    addItem: (data) => apiRequest('/vendor/items', 'POST', data),
    updateItem: (id, data) => apiRequest(`/vendor/items/${id}`, 'PUT', data),
    deleteItem: (id) => apiRequest(`/vendor/items/${id}`, 'DELETE'),
    listRequests: () => apiRequest('/vendor/requests'),
    updateRequest: (id, data) => apiRequest(`/vendor/requests/${id}`, 'PUT', data)
};

// User API
const userAPI = {
    listVendors: (category = '') => apiRequest(`/user/vendors${category ? `?category=${category}` : ''}`),
    getVendorItems: (vendorId) => apiRequest(`/user/vendors/${vendorId}/items`),
    listItems: (category = '') => apiRequest(`/user/items${category ? `?category=${category}` : ''}`),
    getCart: () => apiRequest('/user/cart'),
    addToCart: (data) => apiRequest('/user/cart', 'POST', data),
    removeFromCart: (id) => apiRequest(`/user/cart/${id}`, 'DELETE'),
    clearCart: () => apiRequest('/user/cart', 'DELETE'),
    listOrders: () => apiRequest('/user/orders'),
    createOrder: (data) => apiRequest('/user/orders', 'POST', data),
    cancelOrder: (id) => apiRequest(`/user/orders/${id}/cancel`, 'PUT'),
    payOrder: (id) => apiRequest(`/user/orders/${id}/pay`, 'PUT'),
    listGuests: () => apiRequest('/user/guests'),
    addGuest: (data) => apiRequest('/user/guests', 'POST', data),
    updateGuest: (id, data) => apiRequest(`/user/guests/${id}`, 'PUT', data),
    deleteGuest: (id) => apiRequest(`/user/guests/${id}`, 'DELETE')
};

// Check if user is authenticated
function isAuthenticated() {
    return !!getToken();
}

// Redirect based on role
function redirectToRoleDashboard(role) {
    switch (role) {
        case 'admin':
            window.location.href = '/admin';
            break;
        case 'vendor':
            window.location.href = '/vendor';
            break;
        case 'user':
            window.location.href = '/user';
            break;
        default:
            window.location.href = '/login';
    }
}

// Protect route - redirect to login if not authenticated
function requireAuth(requiredRole = null) {
    if (!isAuthenticated()) {
        window.location.href = '/login';
        return false;
    }

    const user = getCurrentUser();
    if (requiredRole && user.role !== requiredRole) {
        redirectToRoleDashboard(user.role);
        return false;
    }

    return true;
}

// Show alert message
function showAlert(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;

    const container = document.querySelector('.container') || document.body;
    container.insertBefore(alertDiv, container.firstChild);

    setTimeout(() => alertDiv.remove(), 3000);
}

// Format date
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Format currency
function formatCurrency(amount) {
    return '$' + parseFloat(amount).toFixed(2);
}

// Get status badge class
function getStatusBadge(status) {
    const statusLower = status.toLowerCase();
    if (['active', 'approved', 'confirmed', 'completed'].includes(statusLower)) {
        return 'badge-active';
    } else if (['inactive', 'rejected', 'cancelled', 'failed'].includes(statusLower)) {
        return 'badge-inactive';
    } else {
        return 'badge-pending';
    }
}
