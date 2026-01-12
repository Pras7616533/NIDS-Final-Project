let normalCount = 0;
let attackCount = 0;

const ctx = document.getElementById("resultChart").getContext("2d");

const chart = new Chart(ctx, {
    type: "bar",
    data: {
        labels: ["Normal", "Attack"],
        datasets: [{
            label: "Prediction Count",
            data: [normalCount, attackCount]
        }]
    }
});

function runDetection() {
    const model = document.getElementById("model").value;

    fetch("/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model: model })
    })
        .then(res => res.json())
        .then(data => {

            document.getElementById("result").innerText =
                `Result: ${data.prediction}`;

            document.getElementById("confidence").innerText =
                `Model: ${data.model} | Confidence: ${data.confidence}`;

            if (data.prediction === "Normal") normalCount++;
            else attackCount++;

            chart.data.datasets[0].data = [normalCount, attackCount];
            chart.update();
        });

    fetch("/evaluate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model: model })
    })
        .then(res => res.json())
        .then(metrics => {

            document.getElementById("acc").innerText = metrics.accuracy;
            document.getElementById("prec").innerText = metrics.precision;
            document.getElementById("rec").innerText = metrics.recall;
            document.getElementById("f1").innerText = metrics.f1_score;

            const cm = metrics.confusion_matrix;
            document.getElementById("cm00").innerText = cm[0][0];
            document.getElementById("cm01").innerText = cm[0][1];
            document.getElementById("cm10").innerText = cm[1][0];
            document.getElementById("cm11").innerText = cm[1][1];
        });

}

function downloadPDF() {
    const model = document.getElementById("model").value;

    fetch("/download_report", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ model: model })
    })
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = model + "_evaluation_report.pdf";
        document.body.appendChild(a);
        a.click();
        a.remove();

        showToast();   // ✅ SHOW POPUP
    });
}

function showToast() {
    const toast = document.getElementById("toast");
    toast.classList.add("show");

    setTimeout(() => {
        toast.classList.remove("show");
    }, 3000);
}
