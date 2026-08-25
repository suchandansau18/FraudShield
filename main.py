from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.predictor import predict_realtime_transaction
from src.database import get_recent_transactions
from src.database import get_connection


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="AI Payment Fraud Detection System",
    description=(
        "Real-time AI-powered digital payment "
        "fraud detection API"
    ),
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "https://fraudshield-frontend-bqor.onrender.com"
    ],

    allow_credentials=False,

    allow_methods=["*"],

    allow_headers=["*"],
)


# =========================================================
# TRANSACTION INPUT MODEL
# =========================================================

class Transaction(BaseModel):

    step: int

    type: str

    amount: float

    nameOrig: str

    oldbalanceOrg: float

    newbalanceOrig: float

    nameDest: str

    oldbalanceDest: float

    newbalanceDest: float

    isFlaggedFraud: int = 0


# =========================================================
# HOME ENDPOINT
# =========================================================

@app.get("/")
def home():

    return {
        "message": "AI Payment Fraud Detection API is running",
        "version": "1.0.0"
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "fraud-detection-api"
    }


# =========================================================
# FRAUD PREDICTION ENDPOINT
# =========================================================

@app.post("/predict")
def predict(transaction: Transaction):

    data = transaction.model_dump()

    # =====================================================
    # TRANSACTION CONSISTENCY VALIDATION
    # =====================================================

    amount = data["amount"]

    sender_old = data["oldbalanceOrg"]
    sender_new = data["newbalanceOrig"]

    receiver_old = data["oldbalanceDest"]
    receiver_new = data["newbalanceDest"]


    # -----------------------------------------------------
    # CHECK 1: NEGATIVE VALUES
    # -----------------------------------------------------

    if (
        amount < 0
        or sender_old < 0
        or sender_new < 0
        or receiver_old < 0
        or receiver_new < 0
    ):

        return {
            "fraud_probability": 1.0,
            "fraud_probability_percent": 100.0,
            "decision": "INVALID TRANSACTION",
            "risk_level": "HIGH",
            "validation_status": "FAILED",
            "validation_message": (
                "Transaction amount or balance "
                "cannot be negative."
            )
        }


    # -----------------------------------------------------
    # CHECK 2: SENDER HAS ENOUGH BALANCE
    # -----------------------------------------------------

    if amount > sender_old:

        return {
            "fraud_probability": 1.0,
            "fraud_probability_percent": 100.0,
            "decision": "INVALID TRANSACTION",
            "risk_level": "HIGH",
            "validation_status": "FAILED",
            "validation_message": (
                "Transaction amount exceeds sender's "
                "available balance."
            )
        }


    # -----------------------------------------------------
    # CHECK 3: SENDER BALANCE CONSISTENCY
    # -----------------------------------------------------

    expected_sender_new = sender_old - amount

    if abs(sender_new - expected_sender_new) > 0.01:

        return {
            "fraud_probability": 1.0,
            "fraud_probability_percent": 100.0,
            "decision": "INVALID TRANSACTION",
            "risk_level": "HIGH",
            "validation_status": "FAILED",
            "validation_message": (
                "Sender balance is inconsistent "
                "with the transaction amount."
            )
        }


    # -----------------------------------------------------
    # CHECK 4: RECEIVER BALANCE CONSISTENCY
    # -----------------------------------------------------

    expected_receiver_new = receiver_old + amount

    if abs(receiver_new - expected_receiver_new) > 0.01:

        return {
            "fraud_probability": 1.0,
            "fraud_probability_percent": 100.0,
            "decision": "INVALID TRANSACTION",
            "risk_level": "HIGH",
            "validation_status": "FAILED",
            "validation_message": (
                "Receiver balance is inconsistent "
                "with the transaction amount."
            )
        }


    # =====================================================
    # AI FRAUD DETECTION
    # =====================================================

    result = predict_realtime_transaction(data)


    # =====================================================
    # ADD VALIDATION INFORMATION
    # =====================================================

    result["validation_status"] = "PASSED"

    result["validation_message"] = (
        "Transaction balance information is consistent."
    )


    return result


# =========================================================
# RECENT TRANSACTIONS ENDPOINT
# =========================================================

@app.get("/transactions")
def recent_transactions():

    transactions = get_recent_transactions(10)

    return {
        "transactions": transactions
    }


# =========================================================
# ANALYTICS ENDPOINT
# =========================================================

@app.get("/analytics")
def get_analytics():

    connection = get_connection()

    cursor = connection.cursor(dictionary=True)


    # =====================================================
    # TOTAL TRANSACTIONS
    # =====================================================

    cursor.execute("""
        SELECT COUNT(*) AS total_transactions
        FROM transactions
    """)

    total = (
        cursor.fetchone()["total_transactions"]
        or 0
    )


    # =====================================================
    # FRAUD TRANSACTIONS
    # =====================================================

    cursor.execute("""
        SELECT COUNT(*) AS fraud_transactions
        FROM transactions
        WHERE decision = 'FRAUD'
    """)

    fraud = (
        cursor.fetchone()["fraud_transactions"]
        or 0
    )


    # =====================================================
    # LEGITIMATE TRANSACTIONS
    # =====================================================

    cursor.execute("""
        SELECT COUNT(*) AS legitimate_transactions
        FROM transactions
        WHERE decision = 'LEGITIMATE'
    """)

    legitimate = (
        cursor.fetchone()["legitimate_transactions"]
        or 0
    )


    # =====================================================
    # TOTAL TRANSACTION AMOUNT
    # =====================================================

    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0) AS total_amount
        FROM transactions
    """)

    total_amount = (
        cursor.fetchone()["total_amount"]
        or 0
    )


    # =====================================================
    # AVERAGE FRAUD PROBABILITY
    # =====================================================

    cursor.execute("""
        SELECT
            COALESCE(
                AVG(fraud_probability),
                0
            ) AS average_fraud_probability
        FROM transactions
    """)

    avg_probability = (
        cursor.fetchone()["average_fraud_probability"]
        or 0
    )


    # =====================================================
    # RISK DISTRIBUTION
    # =====================================================

    cursor.execute("""
        SELECT
            risk_level,
            COUNT(*) AS count
        FROM transactions
        GROUP BY risk_level
    """)

    risk_rows = cursor.fetchall()


    risk_distribution = {
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0
    }


    for row in risk_rows:

        risk = row["risk_level"]

        if risk in risk_distribution:

            risk_distribution[risk] = row["count"]


    # =====================================================
    # TRANSACTION TYPE DISTRIBUTION
    # =====================================================

    cursor.execute("""
        SELECT
            transaction_type,
            COUNT(*) AS count
        FROM transactions
        GROUP BY transaction_type
    """)

    type_rows = cursor.fetchall()


    transaction_types = {}


    for row in type_rows:

        transaction_types[
            row["transaction_type"]
        ] = row["count"]


    # =====================================================
    # FRAUD RATE
    # =====================================================

    fraud_rate = 0


    if total > 0:

        fraud_rate = (
            fraud / total
        ) * 100


    # =====================================================
    # CLOSE DATABASE CONNECTION
    # =====================================================

    cursor.close()

    connection.close()


    # =====================================================
    # RETURN ANALYTICS
    # =====================================================

    return {

        "total_transactions":
            total,

        "fraud_transactions":
            fraud,

        "legitimate_transactions":
            legitimate,

        "fraud_rate":
            round(
                fraud_rate,
                2
            ),

        "total_transaction_amount":
            float(
                total_amount
            ),

        "average_fraud_probability":
            float(
                avg_probability
            ),

        "risk_distribution":
            risk_distribution,

        "transaction_types":
            transaction_types

    }