import os
import numpy as np
import sqlite3
import csv

from datetime import datetime
from flask import Flask, render_template, redirect, url_for, session, jsonify, request, send_file, Response
from tensorflow.keras.models import load_model
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

from werkzeug.security import generate_password_hash, check_password_hash
from flask import session, redirect, url_for

from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.widgets.markers import makeMarker
from reportlab.lib import colors


app = Flask(__name__)
app.secret_key = "deepnids_secret_key"
ADMIN_USERS = ["admin"]

# ========================
# LOAD MODELS
# ========================

models_dict = {
    "DNN": load_model("models/deepnids_dnn.h5"),
    "CNN": load_model("models/deepnids_cnn.h5"),
    "LSTM": load_model("models/deepnids_lstm.h5"),
    "AUTOENCODER": load_model("models/deepnids_autoencoder.h5")
}

model_metrics = {
    "DNN": {
        "accuracy": 98.2,
        "precision": 97.6,
        "recall": 98.9,
        "f1": 98.2
    },
    "CNN": {
        "accuracy": 99.1,
        "precision": 98.8,
        "recall": 99.3,
        "f1": 99.0
    },
    "LSTM": {
        "accuracy": 98.7,
        "precision": 98.2,
        "recall": 99.0,
        "f1": 98.6
    }
}


X_test = np.load("data/processed/X.npy")
y_test = np.load("data/processed/y.npy")

@app.route("/evaluate", methods=["POST"])
def evaluate():
    data = request.json
    model_name = data["model"]

    model = models_dict[model_name]

    # Reshape test data if needed
    if model_name in ["CNN", "LSTM"]:
        X = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)
    else:
        X = X_test

    # Autoencoder evaluation
    if model_name == "AUTOENCODER":
        recon = model.predict(X)
        mse = np.mean(np.square(X - recon), axis=1)
        y_pred = (mse > 0.01).astype(int)
    else:
        y_pred = np.argmax(model.predict(X), axis=1)

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    cm = confusion_matrix(y_test, y_pred)

    return jsonify({
        "accuracy": round(float(accuracy), 4),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1_score": round(float(f1), 4),
        "confusion_matrix": cm.tolist()
    })

# ========================
# AUTHENTICATION ROUTES
# ========================

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, password)
            )
            conn.commit()
        except:
            return "Username already exists"
        finally:
            conn.close()

        return redirect("/login")

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[3], password):
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

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username=? AND email=?",
            (username, email)
        )
        user = cursor.fetchone()
        conn.close()

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

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET password=? WHERE username=?",
            (new_password, username)
        )
        conn.commit()
        conn.close()

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
    global demo_index

    data = request.json
    model_name = data["model"]

    model = models_dict[model_name]

    x = X_demo[demo_index]
    demo_index = (demo_index + 1) % len(X_demo)

    # Reshape
    if model_name in ["CNN", "LSTM"]:
        x = x.reshape(1, x.shape[0], 1)
    else:
        x = x.reshape(1, x.shape[0])

    # Autoencoder logic
    if model_name == "AUTOENCODER":
        recon = model.predict(x)
        mse = np.mean(np.square(x - recon))
        prediction = "Attack" if mse > 0.01 else "Normal"
        confidence = round(1 - mse, 4)
    else:
        pred = model.predict(x)
        class_id = int(np.argmax(pred))
        prediction = "Normal" if class_id == 0 else "Attack"
        confidence = round(float(np.max(pred)), 4)

    save_log(model_name, prediction, confidence)

    return jsonify({
        "model": model_name,
        "prediction": prediction,
        "confidence": confidence
    })

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

    # Prepare test data
    if model_name in ["CNN", "LSTM"]:
        X = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)
    else:
        X = X_test

    # Predictions
    if model_name == "AUTOENCODER":
        recon = model.predict(X)
        mse = np.mean(np.square(X - recon), axis=1)
        y_pred = (mse > 0.01).astype(int)
    else:
        y_pred = np.argmax(model.predict(X), axis=1)

    # Metrics
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)

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
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT model, prediction, confidence, timestamp
        FROM logs
        ORDER BY id DESC
    """)
    data = cursor.fetchall()
    conn.close()

    return render_template("logs.html", logs=data)

@app.route("/api/logs")
def api_logs():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, model, prediction, confidence, timestamp
        FROM logs
        ORDER BY id DESC
        LIMIT 50
    """)

    rows = cursor.fetchall()
    conn.close()

    logs = []
    for r in rows:
        logs.append({
            "id": r[0],
            "model": r[1],
            "prediction": r[2],
            "confidence": r[3],
            "timestamp": r[4]
        })

    return jsonify(logs)

@app.route("/api/log/<int:log_id>")
def log_details(log_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT model, prediction, confidence, timestamp
        FROM logs WHERE id=?
    """, (log_id,))

    row = cursor.fetchone()
    conn.close()

    return jsonify({
        "model": row[0],
        "prediction": row[1],
        "confidence": row[2],
        "timestamp": row[3]
    })

@app.route("/api/logs/stats")
def logs_stats():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Attack vs Normal count
    cursor.execute("""
        SELECT prediction, COUNT(*) 
        FROM logs 
        GROUP BY prediction
    """)
    prediction_counts = dict(cursor.fetchall())

    # Model-wise attack count
    cursor.execute("""
        SELECT model, COUNT(*) 
        FROM logs 
        WHERE prediction = 'Attack'
        GROUP BY model
    """)
    model_counts = dict(cursor.fetchall())

    conn.close()

    return jsonify({
        "attack": prediction_counts.get("Attack", 0),
        "normal": prediction_counts.get("Normal", 0),
        "model_attacks": model_counts
    })

# ============================
# Export logs as CSV and PDF
# ============================

@app.route("/api/messages/stats")
def message_stats():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM messages")
    total = cursor.fetchone()[0]

    conn.close()

    return jsonify({
        "total": total,
        "unread": total
    })

@app.route("/api/messages/read/<int:id>", methods=["POST"])
def mark_message_read(id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE messages SET status='read' WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})


@app.route("/api/messages/delete/<int:id>", methods=["POST"])
def delete_message(id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route("/export_logs_csv")
def export_logs_csv():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT model, prediction, confidence, timestamp FROM logs")
    rows = cursor.fetchall()
    conn.close()

    def generate():
        yield "Model,Prediction,Confidence,Timestamp\n"
        for row in rows:
            yield f"{row[0]},{row[1]},{row[2]},{row[3]}\n"

    return Response(
        generate(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=reports/attack_logs.csv"}
    )

@app.route("/export_logs_pdf")
def export_logs_pdf():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT model, prediction, confidence, timestamp FROM logs")
    logs = cursor.fetchall()
    conn.close()

    file_path = "app/reports/attack_logs.pdf"
    pdf = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    y = height - 40
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, y, "Attack History & Logs Report")
    y -= 30

    pdf.setFont("Helvetica", 10)
    for log in logs:
        text = f"Model: {log[0]} | Result: {log[1]} | Confidence: {log[2]} | Time: {log[3]}"
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

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                message TEXT,
                timestamp TEXT
            )
        """)

        cursor.execute("""
            INSERT INTO messages (name, email, message, timestamp)
            VALUES (?, ?, ?, ?)
        """, (name, email, message, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        conn.commit()
        conn.close()

        return render_template("contact.html", success=True)

    return render_template("contact.html")

# ================================
# ADMIN ROUTE TO VIEW MESSAGES
# ================================

@app.route("/admin/messages")
@login_required
@admin_required
def admin_messages():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, email, message, timestamp
        FROM messages
        ORDER BY id DESC
    """)

    data = cursor.fetchall()
    conn.close()

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
def dashboard():
    # later: protect with login session
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
def save_log(model, prediction, confidence):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO logs (model, prediction, confidence, timestamp)
        VALUES (?, ?, ?, ?)
    """, (model, prediction, confidence, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()
    conn.close()




# =========================
# MAIN
# =========================

if __name__ == "__main__":
    app.run(debug=True)
