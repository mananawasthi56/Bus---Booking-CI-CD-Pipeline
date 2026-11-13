
const API_URL = "http://127.0.0.1:8000";

const params = new URLSearchParams(window.location.search);
const tripId = Number(params.get("trip_id"));

let selectedSeat = null;
let currentTrip = null;
let bookedSeats = [];
let totalSeats = 0;

const $ = (id) => document.getElementById(id);

// Display messages
function showMessage(message, type = "info") {
    const box = $("message");
    box.textContent = message;
    box.className = "message " + type;
}

// API helper
async function apiRequest(endpoint, options = {}) {
    const token = localStorage.getItem("access_token");

    const headers = {
        "Content-Type": "application/json",
        ...(options.headers || {})
    };

    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }

    const response = await fetch(API_URL + endpoint, {
        ...options,
        headers
    });

    const text = await response.text();

    let data = null;

    if (text) {
        try {
            data = JSON.parse(text);
        } catch {
            data = text;
        }
    }

    if (!response.ok) {
        const detail =
            typeof data === "object" && data !== null
                ? data.detail || "Request failed"
                : data || "Request failed";

        throw new Error(
            Array.isArray(detail)
                ? detail.map(item => item.msg || JSON.stringify(item)).join(", ")
                : String(detail)
        );
    }

    return data;
}

// Load trip information
async function loadTrip() {
    try {
        const trip = await apiRequest(`/api/v1/trips/${tripId}`);

        currentTrip = trip;

        $("tripDetails").innerHTML = `
            <div class="trip-details">

                <div class="detail-item">
                    <span>From</span>
                    <strong>${escapeHTML(trip.source)}</strong>
                </div>

                <div class="detail-item">
                    <span>To</span>
                    <strong>${escapeHTML(trip.destination)}</strong>
                </div>

                <div class="detail-item">
                    <span>Departure</span>
                    <strong>${escapeHTML(
                        new Date(trip.departure_time).toLocaleString()
                    )}</strong>
                </div>

                <div class="detail-item">
                    <span>Fare</span>
                    <strong>₹${Number(trip.fare).toLocaleString("en-IN")}</strong>
                </div>

            </div>
        `;

        $("summaryFare").textContent = `₹${trip.fare}`;

    } catch (error) {
        $("tripDetails").innerHTML =
            `<p class="message error">Unable to load trip: ${escapeHTML(error.message)}</p>`;

        throw error;
    }
}

// Prevent HTML injection
function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
    })[char]);
}

// Normalize seat API response
function normalizeSeatData(data) {
    let booked = [];
    let available = [];
    let count = 0;

    if (Array.isArray(data)) {
        if (data.length && typeof data[0] === "object") {
            data.forEach(seat => {
                const number = Number(
                    seat.seat_number ?? seat.seat ?? seat.number
                );

                if (!Number.isFinite(number)) return;

                if (
                    seat.is_booked === true ||
                    seat.booked === true ||
                    seat.available === false ||
                    ["booked", "confirmed", "unavailable"].includes(
                        String(seat.status || "").toLowerCase()
                    )
                ) {
                    booked.push(number);
                } else {
                    available.push(number);
                }
            });

            count = data.length;
        } else {
            available = data.map(Number).filter(Number.isFinite);
            count = available.length;
        }
    } else if (data && typeof data === "object") {

        const bookedList =
            data.booked_seats ??
            data.booked ??
            [];

        const availableList =
            data.available_seats ??
            data.available ??
            [];

        booked = Array.isArray(bookedList)
            ? bookedList.map(item =>
                Number(
                    typeof item === "object"
                        ? item.seat_number ?? item.seat ?? item.number
                        : item
                )
            ).filter(Number.isFinite)
            : [];

        available = Array.isArray(availableList)
            ? availableList.map(item =>
                Number(
                    typeof item === "object"
                        ? item.seat_number ?? item.seat ?? item.number
                        : item
                )
            ).filter(Number.isFinite)
            : [];

        count = Number(
            data.total_seats ??
            data.total ??
            data.seat_count ??
            0
        );

        if (!count && available.length + booked.length) {
            count = available.length + booked.length;
        }
    }

    return {
        booked: [...new Set(booked)],
        available: [...new Set(available)],
        count
    };
}

// Load seat availability
async function loadSeats() {
    try {
        const data = await apiRequest(
            `/api/v1/trips/${tripId}/seats`
        );

        const result = normalizeSeatData(data);

        bookedSeats = result.booked;

        if (currentTrip && Number(currentTrip.total_seats) > 0) {
            totalSeats = Number(currentTrip.total_seats);
        } else if (result.count > 0) {
            totalSeats = result.count;
        } else if (result.available.length || result.booked.length) {
            totalSeats = Math.max(
                ...result.available,
                ...result.booked
            );
        } else {
            throw new Error("Seat availability response format is not recognized.");
        }

        renderSeats();

    } catch (error) {
        $("seatGrid").innerHTML =
            `<p class="loading">Unable to load seats: ${escapeHTML(error.message)}</p>`;

        throw error;
    }
}

// Draw seats
function renderSeats() {
    const grid = $("seatGrid");

    grid.innerHTML = "";

    for (let seat = 1; seat <= totalSeats; seat++) {

        const button = document.createElement("button");

        button.type = "button";
        button.textContent = seat;
        button.className = "seat";

        const isBooked = bookedSeats.includes(seat);

        if (isBooked) {
            button.classList.add("booked");
            button.disabled = true;
            button.title = "Already booked";
        } else {
            button.addEventListener("click", () => selectSeat(seat));
        }

        if (selectedSeat === seat && !isBooked) {
            button.classList.add("selected");
        }

        grid.appendChild(button);
    }

    if (selectedSeat && bookedSeats.includes(selectedSeat)) {
        selectedSeat = null;
    }

    updateSummary();
}

// Select seat
function selectSeat(seat) {
    if (bookedSeats.includes(seat)) return;

    selectedSeat = seat;

    renderSeats();
}

// Update summary
function updateSummary() {
    $("selectedSeat").textContent = selectedSeat
        ? `Selected seat: ${selectedSeat}`
        : "Please select a seat.";

    $("summarySeat").textContent = selectedSeat ?? "Choose a seat";

    $("confirmBooking").disabled = !selectedSeat;
}

// Confirm booking
async function confirmBooking() {

    if (!selectedSeat) {
        showMessage("Please select a seat first.", "error");
        return;
    }

    const button = $("confirmBooking");

    const token = localStorage.getItem("access_token");

    if (!token) {
        showMessage("Please login before booking.", "error");
        return;
    }

    const seatToBook = selectedSeat;

    button.disabled = true;
    button.textContent = "Processing...";

    try {

        await apiRequest("/api/v1/bookings/", {
            method: "POST",
            body: JSON.stringify({
                trip_id: tripId,
                seat_number: seatToBook
            })
        });

        showMessage(
            `Booking confirmed successfully! Your seat number is ${seatToBook}.`,
            "success"
        );

        selectedSeat = null;

        await loadSeats();

    } catch (error) {

        showMessage(
            "Booking failed: " + error.message,
            "error"
        );

        try {
            await loadSeats();
        } catch (refreshError) {
            console.error("Seat refresh failed:", refreshError);
        }

    } finally {
        button.textContent = "Confirm Booking →";
        button.disabled = !selectedSeat;
    }
}

// Initialize page
async function initializeBookingPage() {

    $("confirmBooking").addEventListener("click", confirmBooking);

    if (!Number.isInteger(tripId) || tripId <= 0) {
        showMessage(
            "Invalid Trip ID. Please go back to the homepage and search for a valid trip.",
            "error"
        );

        $("tripDetails").textContent = "Invalid trip.";
        $("seatGrid").textContent = "No trip selected.";
        return;
    }

    if (!localStorage.getItem("access_token")) {
        showMessage("Please login before booking.", "error");

        setTimeout(() => {
            window.location.href = "login.html";
        }, 1500);

        return;
    }

    try {
        await loadTrip();
        await loadSeats();

    } catch (error) {
        showMessage(error.message, "error");
    }
}

initializeBookingPage();
