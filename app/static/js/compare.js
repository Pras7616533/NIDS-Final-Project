const metrics = {{ metrics | tojson }};

const labels = Object.keys(metrics);
const accuracy = labels.map(m => metrics[m].accuracy);
const precision = labels.map(m => metrics[m].precision);
const recall = labels.map(m => metrics[m].recall);
const f1 = labels.map(m => metrics[m].f1);

new Chart(document.getElementById("modelChart"), {
    type: "bar",
    data: {
        labels: labels,
        datasets: [
            { label: "Accuracy", data: accuracy },
            { label: "Precision", data: precision },
            { label: "Recall", data: recall },
            { label: "F1 Score", data: f1 }
        ]
    },
    options: {
        responsive: true,
        scales: {
            y: { beginAtZero: false }
        }
    }
});