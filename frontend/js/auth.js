function saveToken(token) {
    localStorage.setItem("access_token", token);
}

function getToken() {
    return localStorage.getItem("access_token");
}

function logout() {
    localStorage.removeItem("access_token");
    window.location.href = "login.html";
}

function isLoggedIn() {
    return !!getToken();
}

function requireAuth() {
    if (!isLoggedIn()) {
        window.location.href = "login.html";
    }
}

async function requireRole(allowedRoles) {
    try {
        const user = await apiRequest("/auth/me");
        if (!allowedRoles.includes(user.role_name)) {
            alert("You do not have permission to view this page.");
            window.location.href = "dashboard.html";
            return null;
        }
        return user;
    } catch (err) {
        logout();
        return null;
    }
}