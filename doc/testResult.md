# **TESTING RESULTS**

---

## **1. Introduction**

Testing results summarize the outcomes obtained after executing all planned test cases on the **DeepNIDS (Network Intrusion Detection System)**. The objective of this phase is to confirm that the system meets functional, performance, and usability requirements.

---

## **2. Test Execution Summary**

All test cases were executed under controlled conditions using valid and invalid inputs to verify system behavior.

| Parameter                 | Result |
| ------------------------- | ------ |
| Total Test Cases Designed | 14     |
| Test Cases Executed       | 14     |
| Test Cases Passed         | 14     |
| Test Cases Failed         | 0      |
| Success Rate              | 100%   |

---

## **3. Module-Wise Testing Results**

---

### **3.1 Authentication Module**

* User registration was completed successfully with valid inputs.
* Login functionality worked correctly for valid credentials.
* Invalid login attempts were properly handled with error messages.
* Password hashing ensured secure authentication.

**Result:** ✔ Passed

---

### **3.2 Home Page & Navigation**

* Home page loaded correctly after login.
* Sidebar navigation redirected to appropriate pages.
* Unauthorized users were prevented from accessing protected pages.

**Result:** ✔ Passed

---

### **3.3 Models & Prediction Module**

* All deep learning models (DNN, CNN, LSTM, Autoencoder) loaded successfully.
* Predictions were generated accurately for test data.
* Confidence scores were displayed correctly.

**Result:** ✔ Passed

---

### **3.4 Model Evaluation & Comparison**

* Accuracy, Precision, Recall, F1-Score were computed correctly.
* Confusion matrix was generated without errors.
* Model comparison page displayed metrics correctly.

**Result:** ✔ Passed

---

### **3.5 Logs & Reports Module**

* Detection logs were stored correctly in the database.
* Logs were displayed accurately on the logs page.
* CSV and PDF export functionalities worked as expected.

**Result:** ✔ Passed

---

### **3.6 Admin Module**

* Admin was able to view all user messages.
* Messages could be marked as read and deleted.
* Admin-only access control worked correctly.

**Result:** ✔ Passed

---

### **3.7 UI & Theme Module**

* Light and Dark themes switched correctly.
* User theme preference persisted across sessions.
* UI layout remained consistent in both themes.

**Result:** ✔ Passed

---

## **4. Performance Evaluation Result**

The trained deep learning models were evaluated using standard performance metrics:

* **Accuracy**
* **Precision**
* **Recall**
* **F1-Score**
* **Confusion Matrix**

The models achieved **high accuracy and recall**, indicating effective intrusion detection with minimal false positives.

---

## **5. Defects Summary**

| Defect ID | Description               | Status |
| --------- | ------------------------- | ------ |
| N/A       | No critical defects found | Closed |

---

## **6. Conclusion**

All test cases executed successfully, and no critical defects were identified during the testing phase. The DeepNIDS system is stable, secure, and ready for deployment.
