# AI-Powered System for Continuous Glucose Monitoring and Automated Insulin Delivery

This repository presents an AI-powered time-series prediction system designed for diabetes management. The project focuses on predicting short-term future blood glucose levels using Continuous Glucose Monitoring (CGM) data, with the long-term goal of supporting automated and intelligent insulin delivery decisions.

The system experiments with multiple sequential modeling approaches, including GRU, LSTM, and Hidden Markov Models (HMM), and evaluates them using metrics with clinical relevance. In addition to the machine learning pipeline, the repository includes system design artifacts and mobile UI mockups to demonstrate real-world usability.

---

## Project Objectives

* Analyze real-time and historical glucose readings from CGM sensors
* Predict short-term future glucose levels using deep learning models
* Compare current readings with predicted values to detect potential risks
* Provide understandable insights and alerts to help users make better decisions
* Present results through a clean and simple mobile application interface

---

## System Overview

Glucora consists of three main layers:

1. Data Layer

   * CGM sensor data (time-series glucose readings)
   * Preprocessing and normalization of glucose values

2. AI & Analytics Layer

   * Deep learning models (GRU / LSTM-based architectures)
   * Time-series prediction of future glucose levels
   * Performance evaluation using metrics such as RMSE

3. Application Layer

   * Mobile app UI mockups demonstrating user interaction
   * Clear visualization of glucose trends and predictions
   * Feedback and alerts presented from the user’s perspective

---

## Models Used

* GRU-based time-series prediction model
* Hybrid GRU/LSTM architecture (project-specific design)
* Focus on short-horizon glucose forecasting

Evaluation Metrics:

* RMSE for prediction accuracy
* Comparison between actual and predicted glucose values

---

## Repository Structure

```
Ai-Powered-System-for-Continuous-Glucose-Monitoring-and-Automated-Insulin-Delivery/
│
├── Modeling/
│   ├── GRU, LSTM, and HMM notebooks
│   └── fine-tuning experiments on real patient data
│
├── Preprocessing/
│   ├── CGM data cleaning and normalization
│   └── feature engineering pipelines
│
├── Parsing Real Time Data from Apple Watch/
│   └── Apple Watch data preprocessing attempts
│
├── simglucose-Simulation-backend-master/
│   └── glucose–insulin simulation environment
│
├── Diagrams/
│   ├── UML diagrams
│   ├── sequence diagrams
│   └── system architecture diagrams
│
├── Glucora UI/
│   ├── mobile application mockups
│   ├── UI screenshots
│   └── user flow designs
│
├── Proposal phase documents/
│   └── initial project proposal and planning files
│
├── LICENSE
└── README.md
```
## Glucora UI (Mockups)

The `Glucora UI` folder showcases the mobile application mockups designed for this project. These screens demonstrate:

- User onboarding and dashboard
- Real-time glucose readings
- Predicted glucose trends and future insights
- Visual alerts for potential hypo/hyperglycemia risks

The UI is designed with simplicity and clarity in mind, focusing on ease of use for daily glucose monitoring.

### UI Screenshots Preview

Below are sample screenshots from the mobile application mockups included in this repository:

**Splash Screen**
The splash screen represents the initial launch of the application. It establishes the application identity and serves as a brief transition while the system prepares user data and AI services.

![Splash Screen Screenshot](Glucora%20UI/Splash%20Screen.png)

**User Authentication – Sign In**
The sign-in screen allows returning users to securely access their account. The design is intentionally simple to reduce friction and allow fast access to glucose insights.
![Sing-in Screenshot](Glucora%20UI/Signin.png)

**User Authentication – Sign Up**
The sign-up screen enables new users to create an account and enter essential information required for personalized glucose monitoring and prediction.
![Sign-up Screenshot](Glucora%20UI/Sign%20up.png)

**Main Application Interface (Dashboard)**
The dashboard is the core of the application. It provides a consolidated view of:

* Current glucose level

* Recent glucose trends

* System status and AI prediction indicators

All critical information is available on a single screen to minimize navigation and allow users to quickly understand their condition.

**AI Prediction & Glucose Trend Analysis**
This screen focuses on AI-driven glucose forecasting. Predicted future glucose levels are displayed alongside historical readings, allowing users to compare current values with expected trends and identify potential risks early.

The model operates in the background, while the UI translates predictions into an understandable visual format.

**Recommendations & Insights**
Based on the predicted glucose trajectory, the system generates contextual insights and recommendations. This screen explains why an alert or recommendation was generated, helping users understand the reasoning behind the AI output.
![Various Homepage Screenshots](Glucora%20UI/App%20interfaces.png)


**User Profile**
The profile screen allows users to view and manage their personal information. This data supports personalization of predictions and ensures the AI model aligns with individual user characteristics.
![User Profile Screenshot](Glucora%20UI/Profile.png)


**Notifications & Alerts**
The notifications screen displays AI-generated alerts related to potential hypo- or hyperglycemic events. Each notification is concise, informative, and action-oriented, clearly communicating the detected issue and its urgency.

Notifications are triggered by comparing real-time glucose readings with predicted future values.
![Alerts](Glucora%20UI/Notifications.png)

> All screenshots are available in the `Glucora UI` directory and are intended to demonstrate the proposed user experience rather than a fully implemented application.

---

## How the System Works (High Level Flow)

1. CGM sensor generates glucose readings
2. Data is preprocessed and fed into the AI model
3. The model predicts future glucose levels
4. Current and predicted values are compared
5. Insights and alerts are generated
6. Results are displayed to the user via the mobile app UI

---

## Technologies Used

- Python
- NumPy, Pandas
- TensorFlow / Keras
- Time-series deep learning models (GRU, LSTM)
- UI/UX design tools for mobile mockups

---

## Academic Context

This project is developed as part of a graduation project in Artificial Intelligence. It focuses on applying machine learning techniques to a real-world healthcare problem while emphasizing system design, explainability, and user experience.

---

## Future Work

- Real-time deployment with live CGM devices
- Personalized models per user
- Improved alert logic based on trends and rate of change
- Full mobile application implementation

---

## Authors

- Malak Mohamed Abd-EL Razeq – Artificial Intelligence Student
- Yahia Tamer – Artificial Intelligence Student
- Nouran Hassan – Artificial Intelligence Student
- Roaa Khaled – Artificial Intelligence Student
- Daniel Michel – Artificial Intelligence Student

---

## ⚠️ Disclaimer

Glucora is a research and educational project. It is not intended to replace professional medical advice or clinical decision-making.


