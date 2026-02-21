# **CODE IMPLEMENTATION REPORT**

---

## **1. Introduction**

The code implementation phase involves converting the system design and architecture into a working software solution.
In the **DeepNIDS (Deep Learning–Based Network Intrusion Detection System)** project, the implementation integrates machine learning models with a web-based interface using Python and Flask.

---

## **2. Technology Stack Used**

* **Programming Language:** Python 3.10
* **Backend Framework:** Flask
* **Machine Learning Framework:** TensorFlow & Keras
* **Database:** SQLite
* **Frontend:** HTML5, CSS3, JavaScript
* **Reporting:** ReportLab (PDF), CSV
* **Development Tool:** Visual Studio Code

---

## **3. Project Structure**

```
NIDS-Project/
│
├── app/
│   ├── app.py
│   ├── database.db
│
├── models/
│   ├── deepnids_dnn.h5
│   ├── deepnids_cnn.h5
│   ├── deepnids_lstm.h5
│   └── deepnids_autoencoder.h5
│
├── data/
│   └── processed/
│       ├── X.npy
│       └── y.npy
│
├── templates/
│   ├── login.html
│   ├── home.html
│   ├── models.html
│   ├── logs.html
│   ├── admin_messages.html
│   └── about.html
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
└── reports/
```

---

## **4. Backend Code Implementation**

### **4.1 Flask Application (`app.py`)**

* Handles routing and request processing
* Manages user sessions and authentication
* Connects machine learning models with UI
* Controls database interactions

**Key Functionalities Implemented:**

* User Signup and Login
* Model Selection and Prediction
* Evaluation Metrics Calculation
* PDF and CSV Report Generation
* Admin Message Management

---

### **4.2 Model Loading and Prediction**

```python
models_dict = {
    "DNN": load_model("models/deepnids_dnn.h5"),
    "CNN": load_model("models/deepnids_cnn.h5"),
    "LSTM": load_model("models/deepnids_lstm.h5"),
    "AUTOENCODER": load_model("models/deepnids_autoencoder.h5")
}
```

* Models are loaded once during application startup
* Predictions are performed dynamically based on selected model

---

### **4.3 Evaluation Metrics Implementation**

The following metrics are computed using Scikit-learn:

* Accuracy
* Precision
* Recall
* F1-Score
* Confusion Matrix

```python
accuracy_score(y_test, y_pred)
precision_score(y_test, y_pred)
recall_score(y_test, y_pred)
f1_score(y_test, y_pred)
```

---

## **5. Database Implementation**

### **5.1 SQLite Database**

SQLite is used for lightweight data storage.

**Tables Implemented:**

* `users` – stores login credentials
* `logs` – stores detection results
* `messages` – stores contact form messages

Database operations are implemented using SQL queries within Flask routes.

---

## **6. Frontend Code Implementation**

### **6.1 HTML Templates**

* Structured using Jinja2 templating
* Dynamic content rendering from backend
* Separate pages for each module

### **6.2 CSS Styling**

* Light and Dark theme support
* Responsive layout
* Card-based UI design

### **6.3 JavaScript**

* Theme toggling
* Dynamic data fetching using Fetch API
* Button click handlers for admin actions

---

## **7. Report Generation Implementation**

### **7.1 PDF Report Generation**

* Implemented using **ReportLab**
* Includes model metrics and confusion matrix
* Downloadable by users

### **7.2 CSV Export**

* Logs exported in CSV format
* Useful for offline analysis

---

## **8. Security Implementation**

* Passwords stored using hashed format (`Werkzeug`)
* Session-based authentication
* Admin-only routes protected

---

## **9. Error Handling**

* Invalid login credentials handled gracefully
* Missing inputs validated
* Database exceptions managed using try-except blocks

---

## **10. Result of Implementation**

* All modules integrated successfully
* Real-time predictions and evaluations achieved
* System operates smoothly without runtime errors

---

## **11. Conclusion**

The code implementation of DeepNIDS successfully integrates deep learning models with a secure and user-friendly web application. The system effectively detects network intrusions, evaluates model performance, and generates detailed reports.
