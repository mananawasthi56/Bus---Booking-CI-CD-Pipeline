
document.addEventListener("DOMContentLoaded", function () {

    const message = document.getElementById("message");

    // CHECK ADMIN ACCESS
    if (!requireAdmin()) {
        return;
    }

    // LOAD DASHBOARD STATISTICS
    async function loadDashboard() {

        message.textContent = "Loading dashboard...";

        try {
            const data = await apiRequest(
                "/api/v1/admin/dashboard/stats"
            );

            document.getElementById("totalUsers").textContent =
                data.total_users;

            document.getElementById("totalBuses").textContent =
                data.total_buses;

            document.getElementById("totalTrips").textContent =
                data.total_trips;

            document.getElementById("totalBookings").textContent =
                data.total_bookings;

            document.getElementById("confirmedBookings").textContent =
                data.confirmed_bookings;

            document.getElementById("cancelledBookings").textContent =
                data.cancelled_bookings;

            document.getElementById("totalRevenue").textContent =
                "₹" + Number(data.total_revenue).toLocaleString("en-IN");

            message.textContent = "Dashboard updated successfully.";

        } catch (error) {
            message.textContent = error.message;

            if (error.message.toLowerCase().includes("admin")) {
                window.location.href = "index.html";
            }
        }
    }

    // REFRESH DASHBOARD
    document.getElementById("refreshBtn").addEventListener(
        "click",
        loadDashboard
    );

    loadDashboard();
});
