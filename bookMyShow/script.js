const API = "https://lxcq6b9zd9.execute-api.ap-south-1.amazonaws.com";

let selected = null;

async function loadSeats() {
    const response = await fetch(`${API}/seats`);
    const seats = await response.json();
    const container = document.getElementById("seatContainer");

    container.innerHTML = "";

    seats.forEach(seat => {
        const div = document.createElement("div");
        div.innerHTML = seat.seatNumber;
        div.classList.add("seat");

        if (seat.status == "available") {
            div.classList.add("available");

            div.onclick = () => {
                selected = seat.seatNumber;

                document.querySelectorAll(".seat").forEach(
                    s => s.classList.remove("selected")
                );

                div.classList.add("selected");
            };
        } else {
            div.classList.add("booked");
        }

        container.appendChild(div);
    });
}

async function bookSeat() {
    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;

    const response = await fetch(`${API}/book`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            name: name,
            email: email,
            seat: selected
        })
    });

    const data = await response.json();
    alert(data.message);
    loadSeats();
}

loadSeats();