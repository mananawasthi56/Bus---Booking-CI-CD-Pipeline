
document.addEventListener("DOMContentLoaded", function () {

    const message = document.getElementById("message");
    const bookingsList = document.getElementById("bookingsList");

    if (!requireLogin()) {
        return;
    }

    // LOAD BOOKINGS
    async function loadBookings() {
        message.textContent = "Loading your bookings...";
        bookingsList.innerHTML = "";

        try {
            const bookings = await apiRequest("/api/v1/bookings/");

            if (bookings.length === 0) {
                message.textContent = "No bookings found.";
                return;
            }

            message.textContent = `${bookings.length} booking(s) found.`;

            bookings.forEach(function (booking) {

                const card = document.createElement("div");
                card.className = "trip-card";

                const heading = document.createElement("h3");
                heading.textContent = `Booking #${booking.id}`;

                const seat = document.createElement("p");
                seat.textContent = `Seat Number: ${booking.seat_number}`;

                const trip = document.createElement("p");
                trip.textContent = `Trip ID: ${booking.trip_id}`;

                const status = document.createElement("p");
                status.textContent =
                    `Status: ${booking.status.toUpperCase()}`;

                status.className =
                    booking.status === "confirmed"
                        ? "status-confirmed"
                        : "status-cancelled";

                card.append(heading, seat, trip, status);

                if (booking.status === "confirmed") {

                    const cancelButton = document.createElement("button");

                    cancelButton.className = "btn-danger";
                    cancelButton.textContent = "Cancel Booking";

                    cancelButton.addEventListener("click", function () {
                        cancelBooking(booking.id);
                    });

                    card.appendChild(cancelButton);
                }

                bookingsList.appendChild(card);
            });

        } catch (error) {
            message.textContent = error.message;
        }
    }


    // CANCEL BOOKING
    async function cancelBooking(bookingId) {

        const confirmation = confirm(
            "Are you sure you want to cancel this booking?"
        );

        if (!confirmation) {
            return;
        }

        message.textContent = "Cancelling booking...";

        try {
            await apiRequest(
                `/api/v1/bookings/${bookingId}/cancel`,
                {
                    method: "PATCH"
                }
            );

            message.textContent = "Booking cancelled successfully.";

            await loadBookings();

        } catch (error) {
            message.textContent = error.message;
        }
    }

    loadBookings();
});
