# 🛡️ FraudShield

## AI-Based Behaviour-Aware Real-Time Payment Fraud Detection System

FraudShield is an AI-powered payment fraud detection system designed to analyze digital payment transactions in real time and identify potentially fraudulent behaviour.

The system combines machine learning, behavioural analysis, transaction validation, REST APIs, database storage, and an interactive web dashboard into a complete end-to-end fraud detection platform.
![FraudShield Dashboard](./fraudshield-dashboard.png)

---

## 🚀 Live Demo

🌐 **Frontend:**  
https://fraudshield-frontend-bqor.onrender.com/

🔗 **Backend API:**  
https://fraudshield-vvs5.onrender.com/

📚 **API Documentation:**  
https://fraudshield-vvs5.onrender.com/docs

---

## ✨ Key Features

- 🔍 Real-time payment fraud detection
- 🤖 XGBoost-based fraud classification
- 🧠 Behaviour-aware transaction analysis
- 📊 26 machine-learning features
- ⚠️ Risk-level classification
- 💡 Explainable risk factors
- ✅ Transaction validation
- 🗄️ MySQL database integration
- ⚡ FastAPI REST API
- 📈 Transaction analytics dashboard
- 🌐 Cloud deployment
- 🔐 Database-backed transaction history

---

## 🧠 Machine Learning

FraudShield uses an **XGBoost classifier** for payment fraud detection.

The system incorporates behavioural features such as:

- Previous transaction amount
- Previous average transaction amount
- Time since previous transaction
- Amount deviation
- Amount-to-previous-average ratio
- Balance depletion
- Amount-to-balance ratio
- Receiver transaction history
- Receiver transaction frequency
- User transfer count
- User cash-out count
- Transaction velocity
- Transaction type features

These features allow the system to analyze not only the current transaction but also the transaction behaviour of the sender and receiver.

---

## 📊 Model Performance

The current deployed dashboard reports:

| Metric | Result |
|---|---:|
| ROC-AUC | **99.997%** |
| PR-AUC | **99.80%** |
| ML Features | **26** |

> Performance metrics are based on the project's model evaluation and should be interpreted in the context of the PaySim dataset and its class distribution.

---

## 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │    Web Dashboard    │
                    │   HTML/CSS/JS       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     FastAPI API     │
                    │     /predict        │
                    └──────────┬──────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
                ▼                             ▼
       ┌─────────────────┐          ┌─────────────────┐
       │ Behaviour-Aware │          │   Transaction   │
       │   Feature       │          │   Validation    │
       │   Engineering   │          └─────────────────┘
       └────────┬────────┘
                │
                ▼
       ┌─────────────────┐
       │ XGBoost Model   │
       │ Fraud Classifier│
       └────────┬────────┘
                │
                ▼
       ┌─────────────────┐
       │ Risk Assessment │
       │ LOW/MEDIUM/HIGH │
       └────────┬────────┘
                │
                ▼
       ┌─────────────────┐
       │    MySQL DB     │
       │ Transaction Data│
       └─────────────────┘
