# **KEY FEATURES IMPLEMENTED**

---

## **1. User Authentication and Authorization**

The system provides secure user authentication using a login and signup mechanism. Passwords are stored in encrypted (hashed) format to ensure security. Session-based authentication restricts unauthorized access to protected modules.

---

## **2. Multi-Model Intrusion Detection**

DeepNIDS supports multiple deep learning models including:

* Deep Neural Network (DNN)
* Convolutional Neural Network (CNN)
* Long Short-Term Memory (LSTM)
* Autoencoder

Users can select any model to perform intrusion detection on network traffic data.

---

## **3. Data Preprocessing Module**

Raw network traffic data is preprocessed using:

* Data cleaning
* Feature normalization
* Encoding of categorical attributes

This ensures compatibility with deep learning models and improves prediction accuracy.

---

## **4. Real-Time Intrusion Detection**

The system performs real-time prediction on network data and classifies traffic as **Normal** or **Attack**. Confidence scores are also displayed to indicate prediction reliability.

---

## **5. Model Performance Evaluation**

Each model is evaluated using standard metrics:

* Accuracy
* Precision
* Recall
* F1-Score
* Confusion Matrix

These metrics help in assessing detection efficiency and false positive rates.

---

## **6. Model Comparison Dashboard**

A dedicated comparison module allows users and administrators to analyze and compare the performance of different models visually, enabling informed model selection.

---

## **7. Logging and Monitoring**

All prediction activities are logged with:

* Model name
* Prediction result
* Confidence score
* Timestamp

This enables tracking, auditing, and future analysis.

---

## **8. Report Generation and Export**

The system supports downloading detailed evaluation reports in:

* PDF format
* CSV format

Reports include performance metrics and confusion matrices for offline reference.

---

## **9. Admin Panel and Message Management**

An admin module allows administrators to:

* View user-submitted messages
* Mark messages as read
* Delete messages
* Monitor system usage

---

## **10. Responsive User Interface**

The web interface is fully responsive and user-friendly. Features include:

* Sidebar navigation
* Card-based layouts
* Light and Dark theme support

---

## **11. Theme Customization**

Users can switch between light and dark modes. Theme preference is stored locally to maintain UI consistency across sessions.

---

## **12. Secure Database Management**

SQLite is used for efficient and lightweight database management, ensuring fast data access and secure storage.

---

## **13. Error Handling and Validation**

Robust error handling mechanisms ensure system stability by managing invalid inputs, authentication failures, and database exceptions gracefully.

---

## **14. Scalability and Modularity**

The modular architecture allows easy extension of features such as adding new models, integrating APIs, or upgrading the database.
