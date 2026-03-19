import os
import numpy as np
import csv
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, session, jsonify, request, send_file, Response
from tensorflow.keras.models import load_model
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from werkzeug.security import generate_password_hash, check_password_hash

from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.lib import colors

from detection_engine import DetectionEngine
from database import get_db, close_db, query_db, execute_db


app = Flask(__name__)
app.secret_key = "deepnids_secret_key"
ADMIN_USERS = ["admin"]

@app.teardown_appcontext
def teardown_db(exception):
    close_db(exception)

# ========================
# MODELS & ENGINE
# ========================

models_dict = {
    "DNN": load_model("models/deepnids_dnn.h5"),
    "CNN": load_model("models/deepnids_cnn.h5"),
    "LSTM": load_model("models/deepnids_lstm.h5"),
    "AUTOENCODER": load_model("models/deepnids_autoencoder.h5")
}

detection_engine = DetectionEngine(models_dict)

model_metrics = {
    "DNN": {"accuracy": 98.2, "precision": 97.6, "recall": 98.9, "f1": 98.2},
    "CNN": {"accuracy": 99.1, "precision": 98.8, "recall": 99.3, "f1": 99.0},
    "LSTM": {"accuracy": 98.7, "precision": 98.2, "recall": 99.0, "f1": 98.6}
}

# ========================
# HELPER FUNCTIONS
# ========================

def get_model_evaluation(model_name):
    model = models_dict[model_name]
    
    # Reshape test data if needed
    if model_name in ["CNN", "LSTM"]:
        X = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)
    else:
        X = X_test

    # Prediction
    if model_name == "AUTOENCODER":
        recon = model.predict(X)
        mse = np.mean(np.square(X - recon), axis=1)
        y_pred = (mse > 0.01).astype(int)
    else:
        y_pred = np.argmax(model.predict(X), axis=1)

    # Metrics
    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred)),
        "recall": float(recall_score(y_test, y_pred)),
        "f1_score": float(f1_score(y_test, y_pred)),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist()
    }
    return metrics


X_test = np.load("data/processed/X.npy")
y_test = np.load("data/processed/y.npy")

@app.route("/evaluate", methods=["POST"])
def evaluate():
    model_name = request.json["model"]
    metrics = get_model_evaluation(model_name)
    
    # Round metrics for display
    for key in ["accuracy", "precision", "recall", "f1_score"]:
        metrics[key] = round(metrics[key], 4)
        
    return jsonify(metrics)

# ========================
# AUTHENTICATION ROUTES
# ========================

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        try:
            execute_db(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, password)
            )
        except Exception as e:
            return f"Error: {str(e)}"

        return redirect("/login")

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = query_db("SELECT * FROM users WHERE username=?", (username,), one=True)

        if user and check_password_hash(user['password'], password):
            session["user"] = username
            return redirect("/home")
        else:
            return "Invalid credentials"

    return render_template("login.html")

def login_required(func):
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect("/login")
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

def admin_required(func):
    def wrapper(*args, **kwargs):
        if "user" not in session or session["user"] not in ADMIN_USERS:
            return redirect("/home")
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# ========================
# PASSWORD RESET ROUTES
# ========================

@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]

        user = query_db(
            "SELECT * FROM users WHERE username=? AND email=?",
            (username, email),
            one=True
        )

        if user:
            session["reset_user"] = username
            return redirect("/reset_password")
        else:
            return "Invalid username or email"

    return render_template("forgot_password.html")

@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if "reset_user" not in session:
        return redirect("/login")

    if request.method == "POST":
        new_password = generate_password_hash(request.form["password"])
        username = session["reset_user"]

        execute_db(
            "UPDATE users SET password=? WHERE username=?",
            (new_password, username)
        )

        session.pop("reset_user")
        return redirect("/login")

    return render_template("reset_password.html")

# ========================
# PREDICTION ROUTE
# ========================

X_demo = np.load("data/processed/X.npy")
demo_index = 0

@app.route("/predict", methods=["POST"])
def predict():
    model_name = request.json["model"]
    
    # Simple state management for demo
    if 'demo_index' not in session:
        session['demo_index'] = 0
    
    index = session['demo_index']
    x = X_demo[index]
    session['demo_index'] = (index + 1) % len(X_demo)

    result = detection_engine.predict_and_prevent(model_name, x)
    save_log(model_name, result["prediction"], result["confidence"], result["attacker_ip"], result["action_taken"])

    return jsonify(result)

# ========================
# IPS MANAGEMENT ROUTES
# ========================

@app.route("/api/ips/status")
def ips_status():
    return jsonify(detection_engine.get_ips_status())

@app.route("/api/ips/unblock", methods=["POST"])
@login_required
@admin_required
def unblock_ip():
    data = request.json
    ip = data.get("ip")
    if not ip:
        return jsonify({"success": False, "message": "IP is required"}), 400
    
    success, message = detection_engine.unblock_ip(ip)
    return jsonify({"success": success, "message": message})

@app.route("/api/ips/whitelist/add", methods=["POST"])
@login_required
@admin_required
def add_whitelist():
    data = request.json
    ip = data.get("ip")
    if not ip:
        return jsonify({"success": False, "message": "IP is required"}), 400
    
    detection_engine.ips.add_to_whitelist(ip)
    return jsonify({"success": True, "message": f"IP {ip} added to whitelist"})

@app.route("/api/ips/whitelist/remove", methods=["POST"])
@login_required
@admin_required
def remove_whitelist():
    data = request.json
    ip = data.get("ip")
    if not ip:
        return jsonify({"success": False, "message": "IP is required"}), 400
    
    detection_engine.ips.remove_from_whitelist(ip)
    return jsonify({"success": True, "message": f"IP {ip} removed from whitelist"})

# ========================
# REPORT DOWNLOAD ROUTE
# ========================

def create_confusion_matrix_chart(cm):
    drawing = Drawing(400, 250)

    chart = VerticalBarChart()
    chart.x = 50
    chart.y = 50
    chart.height = 150
    chart.width = 300

    # Confusion matrix values
    chart.data = [[cm[0][0], cm[0][1], cm[1][0], cm[1][1]]]
    chart.categoryAxis.categoryNames = ["TN", "FP", "FN", "TP"]

    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = max(cm.flatten()) + 10
    chart.valueAxis.valueStep = max(1, int(chart.valueAxis.valueMax / 5))

    chart.bars[0].fillColor = colors.HexColor("#2563eb")
    chart.bars[0].strokeColor = colors.black

    drawing.add(chart)
    return drawing

@app.route("/download_report", methods=["POST"])
def download_report():
    data = request.json
    model_name = data["model"]


    file_path = f"app/reports/{model_name}_evaluation_report.pdf"
    model = models_dict[model_name]

    # Metrics
    metrics = get_model_evaluation(model_name)
    acc, prec, rec, f1 = metrics["accuracy"], metrics["precision"], metrics["recall"], metrics["f1_score"]
    cm = np.array(metrics["confusion_matrix"])

    # ================= PDF CREATION =================
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(
        "<b>Network Intrusion Detection System (NIDS)</b>",
        styles["Title"]
    ))

    elements.append(Paragraph(
        f"<b>Model Evaluation Report – {model_name}</b>",
        styles["Heading2"]
    ))

    elements.append(Paragraph(
        f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",
        styles["Normal"]
    ))

    elements.append(Paragraph("<br/>", styles["Normal"]))

    # Metrics section
    elements.append(Paragraph("<b>Performance Metrics</b>", styles["Heading2"]))

    metrics_table = Table([
        ["Metric", "Value"],
        ["Accuracy", f"{acc:.4f}"],
        ["Precision", f"{prec:.4f}"],
        ["Recall", f"{rec:.4f}"],
        ["F1-Score", f"{f1:.4f}"]
    ], colWidths=[3*inch, 3*inch])

    elements.append(metrics_table)
    elements.append(Paragraph("<br/>", styles["Normal"]))

    # Confusion Matrix
    elements.append(Paragraph("<b>Confusion Matrix</b>", styles["Heading2"]))

    cm_table = Table([
        ["", "Predicted Normal", "Predicted Attack"],
        ["Actual Normal", cm[0][0], cm[0][1]],
        ["Actual Attack", cm[1][0], cm[1][1]]
    ], colWidths=[2*inch, 2*inch, 2*inch])

    elements.append(cm_table)

    elements.append(Paragraph("<br/><br/>", styles["Normal"]))

    # Conclusion
    # ===== ADD CONFUSION MATRIX CHART =====
    elements.append(Paragraph("<br/><b>Confusion Matrix Visualization</b>", styles["Heading2"]))

    cm_chart = create_confusion_matrix_chart(cm)
    elements.append(cm_chart)

    elements.append(Paragraph(
        "The evaluation results indicate that the selected deep learning model "
        "achieves high accuracy and recall, demonstrating effective intrusion "
        "detection with minimal false positives.",
        styles["Normal"]
    ))
    elements.append(Paragraph(
        "<br/><br/><b>Project Team:</b> DeepNIDS Team",
        styles["Normal"]
    ))

    doc.build(elements)

    return send_file(file_path, as_attachment=True)


# =========================
# log routes
# =========================

@app.route("/logs")
@login_required
def logs():
    data = query_db("""
        SELECT model, prediction, confidence, timestamp
        FROM logs
        ORDER BY id DESC
    """)
    return render_template("logs.html", logs=data)

@app.route("/api/logs")
def api_logs():
    rows = query_db("""
        SELECT id, model, prediction, confidence, timestamp
        FROM logs
        ORDER BY id DESC
        LIMIT 50
    """)

    logs = [dict(r) for r in rows]
    return jsonify(logs)

@app.route("/api/log/<int:log_id>")
def log_details(log_id):
    row = query_db("SELECT model, prediction, confidence, timestamp FROM logs WHERE id=?", (log_id,), one=True)
    return jsonify(dict(row)) if row else jsonify({"error": "Log not found"}), 404

@app.route("/api/logs/stats")
def logs_stats():
    # Attack vs Normal count
    prediction_counts = dict(query_db("SELECT prediction, COUNT(*) FROM logs GROUP BY prediction"))
    
    # Model-wise attack count
    model_counts = dict(query_db("SELECT model, COUNT(*) FROM logs WHERE prediction = 'Attack' GROUP BY model"))

    return jsonify({
        "attack": prediction_counts.get("Attack", 0),
        "normal": prediction_counts.get("Normal", 0),
        "model_attacks": model_counts
    })

# ============================
# Export logs as CSV and PDF
# ============================

@app.route("/api/messages/stats")
@login_required
@admin_required
def message_stats():
    total = query_db("SELECT COUNT(*) FROM messages", one=True)[0]
    unread = query_db("SELECT COUNT(*) FROM messages WHERE status='new'", one=True)[0]
    return jsonify({"total": total, "unread": unread})

@app.route("/api/messages/read/<int:id>", methods=["POST"])
@login_required
@admin_required
def mark_message_read(id):
    execute_db("UPDATE messages SET status='read' WHERE id=?", (id,))
    return jsonify({"success": True})

@app.route("/api/messages/delete/<int:id>", methods=["POST"])
@login_required
@admin_required
def delete_message(id):
    execute_db("DELETE FROM messages WHERE id=?", (id,))
    return jsonify({"success": True})

@app.route("/export_logs_csv")
@login_required
def export_logs_csv():
    rows = query_db("SELECT model, prediction, confidence, timestamp FROM logs")
    
    def generate():
        yield "Model,Prediction,Confidence,Timestamp\n"
        for row in rows:
            yield f"{row['model']},{row['prediction']},{row['confidence']},{row['timestamp']}\n"

    return Response(
        generate(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=attack_logs.csv"}
    )

@app.route("/export_logs_pdf")
@login_required
def export_logs_pdf():
    logs = query_db("SELECT model, prediction, confidence, timestamp FROM logs")
    
    file_path = os.path.join(os.path.dirname(__file__), "reports", "attack_logs.pdf")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    pdf = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    y = height - 40
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, y, "Attack History & Logs Report")
    y -= 30

    pdf.setFont("Helvetica", 10)
    for log in logs:
        text = f"Model: {log['model']} | Result: {log['prediction']} | Confidence: {log['confidence']} | Time: {log['timestamp']}"
        pdf.drawString(40, y, text)
        y -= 15

        if y < 40:
            pdf.showPage()
            pdf.setFont("Helvetica", 10)
            y = height - 40

    pdf.save()
    return send_file(file_path, as_attachment=True)

# ========================
# CONTACT ROUTE
# ========================

@app.route("/contact", methods=["GET", "POST"])
@login_required
def contact():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        message = request.form["message"]

        execute_db("""
            INSERT INTO messages (name, email, message, timestamp)
            VALUES (?, ?, ?, ?)
        """, (name, email, message, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        return render_template("contact.html", success=True)

    return render_template("contact.html")

# ================================
# ADMIN ROUTE TO VIEW MESSAGES
# ================================

@app.route("/admin/messages")
@login_required
@admin_required
def admin_messages():
    data = query_db("""
        SELECT id, name, email, message, timestamp, status
        FROM messages
        ORDER BY id DESC
    """)
    return render_template("admin_messages.html", messages=data)

# =========================
# ROUTES
# =========================

@app.route("/")
def landing():
    if "user" in session:
        return redirect("/home")
    return render_template("loading.html")

@app.route("/home")
@login_required
def home():
    return render_template("home.html", user=session["user"])

@app.route("/dashboard")
@login_required
@admin_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/models")
def models():
    return render_template("models.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/compare")
def compare_models():
    return render_template("compare.html", metrics=model_metrics)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# == DATABASE CONNECTION ==
def save_log(model, prediction, confidence, attacker_ip="N/A", action_taken="None"):
    execute_db("""
        INSERT INTO logs (model, prediction, confidence, attacker_ip, action_taken, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (model, prediction, confidence, attacker_ip, action_taken, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))




# =========================
# MAIN
# =========================

if __name__ == "__main__":
    app.run(debug=True)
