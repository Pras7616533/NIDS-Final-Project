# **CHAPTER: TESTING**

---

## **1. Introduction**

Testing is a critical phase in software development that ensures the system works as expected.
In the **DeepNIDS (Network Intrusion Detection System)** project, testing is performed to validate functionality, accuracy, reliability, and usability of all modules.

---

## **2. Test Case Design**

Test cases are designed to verify each module of the system such as authentication, model execution, report generation, admin operations, and UI behavior.

---

## **3. Test Cases**

### **Test Case Format**

* Test Case ID
* Description
* Preconditions
* Test Steps
* Test Data
* Expected Result
* Status

---

### **3.1 Authentication Module Test Cases**

| Test Case ID | Description                        | Preconditions       | Test Steps                           | Test Data                                                  | Expected Result              | Status |
| ------------ | ---------------------------------- | ------------------- | ------------------------------------ | ---------------------------------------------------------- | ---------------------------- | ------ |
| TC-01        | Verify user signup                 | User not registered | Open Signup → Enter details → Submit | user1, [user1@gmail.com](mailto:user1@gmail.com), Test@123 | User registered successfully | Pass   |
| TC-02        | Verify login with valid data       | User exists         | Enter username & password → Login    | user1 / Test@123                                           | Redirect to Home page        | Pass   |
| TC-03        | Verify login with invalid password | User exists         | Enter wrong password → Login         | user1 / wrong123                                           | Error message displayed      | Pass   |

---

### **3.2 Home Page Test Cases**

| Test Case ID | Description           | Preconditions  | Test Steps               | Test Data | Expected Result                   | Status |
| ------------ | --------------------- | -------------- | ------------------------ | --------- | --------------------------------- | ------ |
| TC-04        | Verify Home page load | User logged in | Login → Navigate to Home | N/A       | Home page loads with project info | Pass   |

---

### **3.3 Models Module Test Cases**

| Test Case ID | Description              | Preconditions  | Test Steps             | Test Data      | Expected Result              | Status |
| ------------ | ------------------------ | -------------- | ---------------------- | -------------- | ---------------------------- | ------ |
| TC-05        | Display available models | User logged in | Open Models page       | N/A            | DNN, CNN, LSTM, AE displayed | Pass   |
| TC-06        | Run intrusion detection  | Model loaded   | Select model → Predict | Sample dataset | Prediction result shown      | Pass   |

---

### **3.4 Logs & Reports Test Cases**

| Test Case ID | Description         | Preconditions   | Test Steps              | Test Data | Expected Result         | Status |
| ------------ | ------------------- | --------------- | ----------------------- | --------- | ----------------------- | ------ |
| TC-07        | View logs           | Logs available  | Open Logs page          | N/A       | Logs displayed in table | Pass   |
| TC-08        | Export logs CSV     | Logs exist      | Click Export CSV        | N/A       | CSV file downloaded     | Pass   |
| TC-09        | Download PDF report | Model evaluated | Select model → Download | DNN       | PDF report generated    | Pass   |

---

### **3.5 Contact & Admin Module Test Cases**

| Test Case ID | Description          | Preconditions      | Test Steps          | Test Data            | Expected Result    | Status |
| ------------ | -------------------- | ------------------ | ------------------- | -------------------- | ------------------ | ------ |
| TC-10        | Submit contact form  | User logged in     | Fill form → Submit  | Name, Email, Message | Message saved      | Pass   |
| TC-11        | Admin views messages | Admin logged in    | Open Admin Messages | N/A                  | Messages displayed | Pass   |
| TC-12        | Mark message as read | New message exists | Click Mark Read     | Message ID           | Status updated     | Pass   |

---

### **3.6 UI & Logout Test Cases**

| Test Case ID | Description  | Preconditions  | Test Steps         | Test Data | Expected Result          | Status |
| ------------ | ------------ | -------------- | ------------------ | --------- | ------------------------ | ------ |
| TC-13        | Toggle theme | User logged in | Click Theme button | N/A       | Light/Dark theme applied | Pass   |
| TC-14        | Logout       | User logged in | Click Logout       | N/A       | Redirect to Login page   | Pass   |

---

## **4. Unit Testing**

### **4.1 Description**

Unit testing is performed to test individual modules of the system independently.

### **4.2 Unit Tested Modules**

* User Authentication module
* Data preprocessing functions
* Model prediction logic
* Evaluation metrics calculation
* Database CRUD operations

### **4.3 Result**

All individual modules performed correctly when tested independently.

---

## **5. System Testing**

### **5.1 Description**

System testing validates the complete integrated DeepNIDS system.

### **5.2 System Testing Scenarios**

* Login → Prediction → Report download
* Admin login → View logs → Export reports
* UI navigation and theme switching
* Error handling for invalid inputs

### **5.3 Result**

The system functioned as expected without any major defects.
