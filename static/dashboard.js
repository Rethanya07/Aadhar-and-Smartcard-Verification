document.addEventListener("DOMContentLoaded", function () {
    fetch("/get_borrowers")
        .then(response => response.json())
        .then(data => {
            let tbody = document.getElementById("borrowers-data");
            tbody.innerHTML = "";
            data.forEach(row => {
                let tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>${row.id}</td>
                    <td>${row.name}</td>
                    <td>${row.aadhar_number}</td>
                    <td>${row.smartcard_number}</td>
                    <td>${row.status}</td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(error => console.error("Error fetching data:", error));
});
