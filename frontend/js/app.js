
const API_URL = "http://127.0.0.1:8000";

// GET SAVED TOKEN
function getToken() {
    return localStorage.getItem("access_token");
}

// GET SAVED USER
function getUser() {
    const savedUser = localStorage.getItem("user");

    if (!savedUser) {
        return null;
    }

    try {
        return JSON.parse(savedUser);
    } catch {
        localStorage.removeItem("user");
        return null;
    }
}

// CHECK LOGIN
function requireLogin() {
    if (!getToken()) {
        window.location.href = "login.html";
        return false;
    }

    return true;
}

// CHECK ADMIN
function requireAdmin() {
    const user = getUser();

    if (!getToken() || !user || user.role !== "admin") {
        window.location.href = "login.html";
        return false;
    }

    return true;
}

// LOGOUT
function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");

    window.location.href = "login.html";
}

// API REQUEST WITH AUTHENTICATION
async function apiRequest(endpoint, options = {}) {
    const headers = {
        ...(options.headers || {})
    };

    if (getToken()) {
        headers["Authorization"] = `Bearer ${getToken()}`;
    }

    const response = await fetch(
        `${API_URL}${endpoint}`,
        {
            ...options,
            headers
        }
    );

    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.detail || "Something went wrong"
        );
    }

    return data;
}
