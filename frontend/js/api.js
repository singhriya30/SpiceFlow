const API_BASE_URL = "http://127.0.0.1:8000";

async function apiRequest(endpoint, method = "GET", body = null) {
    const token = localStorage.getItem("access_token");

    const headers = {
        "Content-Type": "application/json"
    };

    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const options = {
        method,
        headers
    };

    if (body) {
        options.body = JSON.stringify(body);
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, options);

    if (response.status === 401 || response.status === 403) {
        const data = await response.json().catch(() => null);
        if (response.status === 401 || (data && data.detail && data.detail.includes("deactivated"))) {
            localStorage.removeItem("access_token");
            window.location.href = "login.html";
            return;
        }
        throw new Error(data && data.detail ? data.detail : "Access denied");
    }

    if (!response.ok) {
        const data = await response.json().catch(() => null);
        throw new Error(data && data.detail ? data.detail : `Request failed with status ${response.status}`);
    }

    if (response.status === 204) {
        return null;
    }

    return response.json();
}