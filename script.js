async function submitExpense() {
    const amount = parseFloat(document.getElementById("amountInput").value);
    const category = document.getElementById("categoryInput").value;
    const description = document.getElementById("descriptionInput").value;

    const res = await fetch("/add_expense", {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ amount, category, description })
    });

    const data = await res.json();
    document.getElementById("status").innerText = data.status;
    loadExpenses();
}

async function loadExpenses() {
    const category = document.getElementById("categoryFilter").value;
    const res = await fetch(`/get_expenses?category=${category}`);
    const expenses = await res.json();

    const tbody = document.querySelector("#expenseTable tbody");
    tbody.innerHTML = "";
    expenses.forEach((row, index) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${index + 1}</td>
            <td>₹${row[1]}</td>
            <td>${row[2]}</td>
            <td>${row[3]}</td>
            <td>${row[4]}</td>
            <td><button onclick="deleteExpense(${row[0]})">Delete</button></td>
        `;
        tbody.appendChild(tr);
    });
}

async function deleteExpense(id) {
    const res = await fetch(`/delete_expense/${id}`, { method: "DELETE" });
    const data = await res.json();
    document.getElementById("status").innerText = data.status;
    loadExpenses();
}

async function saveSalary() {
    const salary = parseFloat(document.getElementById("salaryInput").value);
    const res = await fetch("/save_salary", {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ salary })
    });
    const data = await res.json();
    document.getElementById("status").innerText = data.status;
}

async function generateRecommendations() {
    const res = await fetch("/get_recommendations");
    const data = await res.json();
    const box = document.getElementById("recommendationBox");
    box.innerText = data.recommendations.join("\n");
}

function filterExpenses() {
    loadExpenses();
}

// Load expenses on page load
window.onload = loadExpenses;
