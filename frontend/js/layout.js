function renderSidebar(activePage) {
    const pages = [
        { name: "Dashboard", file: "dashboard.html" },
        { name: "Products", file: "products.html" },
        { name: "Inventory", file: "inventory.html" },
        { name: "Orders", file: "orders.html" },
        { name: "Employees", file: "employees.html", ownerOnly: true }
    ];

    return `
        <div class="sidebar">
            <div class="brand">SpiceFlow</div>
            <nav>
                ${pages.map(p => `
                    <a href="${p.file}" class="${p.file === activePage ? 'active' : ''}" ${p.ownerOnly ? 'data-owner-only="true"' : ''}>
                        ${p.name}
                    </a>
                `).join("")}
            </nav>
            <div class="logout-link">
                <a href="#" id="logout-btn">Log out</a>
            </div>
        </div>
    `;
}

async function initLayout(activePage) {
    requireAuth();

    document.getElementById("sidebar-container").innerHTML = renderSidebar(activePage);
    document.getElementById("logout-btn").addEventListener("click", (e) => {
        e.preventDefault();
        logout();
    });

    try {
        const user = await apiRequest("/auth/me");

        if (user.role_name === "Customer") {
            logout();
            return null;
        }

        if (user.role_name !== "Owner") {
            document.querySelectorAll('[data-owner-only="true"]').forEach(el => el.remove());
        }

        return user;
    } catch (err) {
        logout();
        return null;
    }
}