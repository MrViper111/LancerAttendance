let users = [];

async function fetchUsers() {
    try {
        const response = await fetch('/api/get_users');
        if (!response.ok) throw new Error('Failed to fetch members');

        const jsonData = await response.json();
        users = jsonData.response;
        console.log(jsonData);
    } catch (error) {
        console.error('Error fetching members:', error);
    }
}

async function createUserCard(user) {
    const card = document.createElement("div");
    card.className = "container1 inline-container";

    const critical = document.createElement("div")
    critical.className = "inline-container";

    const header = document.createElement("div")
    header.innerHTML = "<b>#1</b> " + user.name + " <span class='lesser'>(" + user.position + ")</span>"

    const score = document.createElement("div")
    score.innerHTML = "Score: <b>" + user.score + "</b>"

    const email = document.createElement("div")
    email.innerHTML = "<span class='lesser'>" + user.email + "</span>"

    critical.appendChild(header);

    card.appendChild(header);
    card.appendChild(score);
    card.appendChild(email);

    return card;
}

function renderUsers(data) {
    const container = document.getElementById("user-container");

    data.forEach(async user => {
        console.log(user);
        const card = await createUserCard(user);
        container.appendChild(card);
    });
}

document.addEventListener("DOMContentLoaded", async () => {
    console.log("stuff is being done");
    await fetchUsers();
    renderUsers(users);
});
