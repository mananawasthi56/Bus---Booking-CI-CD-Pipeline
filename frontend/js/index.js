
document.addEventListener("DOMContentLoaded", function () {

    const loginLink = document.getElementById("loginLink");
    const registerLink = document.getElementById("registerLink");
    const bookingLink = document.getElementById("bookingLink");
    const userName = document.getElementById("userName");
    const logoutBtn = document.getElementById("logoutBtn");

    // DISPLAY USER LOGIN STATUS
    const user = getUser();

    if (getToken() && user) {
        loginLink.hidden = true;
        registerLink.hidden = true;
        bookingLink.hidden = false;
        logoutBtn.hidden = false;

        userName.textContent = "Welcome, " + user.full_name;

        if (user.role === "admin") {
            const adminLink = document.createElement("a");
            adminLink.href = "admin.html";
            adminLink.textContent = "Admin Dashboard";
            document.querySelector(".nav-links").appendChild(adminLink);
        }
    }

    // LOGOUT
    logoutBtn.addEventListener("click", logout);

    // SET MINIMUM JOURNEY DATE
    const travelDateInput = document.getElementById("travelDate");

    const today = new Date();
    const localToday = new Date(
        today.getTime() - today.getTimezoneOffset() * 60000
    ).toISOString().split("T")[0];

    travelDateInput.min = localToday;

    // SEARCH BUSES
    document.getElementById("searchForm").addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();

            const source = document.getElementById("source").value.trim();
            const destination =
                document.getElementById("destination").value.trim();
            const travelDate = travelDateInput.value;

            const results = document.getElementById("tripResults");
            const message = document.getElementById("searchMessage");

            results.innerHTML = "";
            message.textContent = "Searching buses...";

            if (source.toLowerCase() === destination.toLowerCase()) {
                message.textContent =
                    "Source and destination cannot be the same.";
                return;
            }

            const params = new URLSearchParams({
                source: source,
                destination: destination
            });

            if (travelDate) {
                params.append("travel_date", travelDate);
            }

            try {
                const trips = await apiRequest(
                    `/api/v1/trips/search?${params.toString()}`
                );

                if (trips.length === 0) {
                    message.textContent =
                        "No buses found for this route.";
                    return;
                }

                message.textContent =
                    `${trips.length} bus trip(s) found.`;

                trips.forEach(function (trip) {

                    const card = document.createElement("div");
                    card.className = "trip-card";

                    const heading = document.createElement("h3");
                    heading.textContent =
                        `${trip.source} → ${trip.destination}`;

                    const departure = document.createElement("p");
                    departure.textContent =
                        `Departure: ${new Date(
                            trip.departure_time
                        ).toLocaleString()}`;

                    const fare = document.createElement("p");
                    fare.textContent = `Fare: ₹${trip.fare}`;

                    const button = document.createElement("button");
                    button.className = "btn-primary";
                    button.textContent = "Book Seat";

                    button.addEventListener("click", function () {

                        if (!getToken()) {
                            window.location.href = "login.html";
                            return;
                        }

                        window.location.href =
                            `booking.html?trip_id=${encodeURIComponent(trip.id)}`;
                    });

                    card.append(heading, departure, fare, button);
                    results.appendChild(card);
                });

            } catch (error) {
                message.textContent = error.message;
            }
        }
    );
});
