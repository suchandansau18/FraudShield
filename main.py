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

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:8000",
        "http://localhost:8000"
    ],

    allow_credentials=True,

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

    result = predict_realtime_transaction(
        transaction.model_dump()
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
@app.get("/analytics")
def get_analytics():

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    # Total transactions
    cursor.execute("""
        SELECT COUNT(*) AS total_transactions
        FROM transactions
    """)
    total = cursor.fetchone()["total_transactions"] or 0


    # Fraud transactions
    cursor.execute("""
        SELECT COUNT(*) AS fraud_transactions
        FROM transactions
        WHERE decision = 'FRAUD'
    """)
    fraud = cursor.fetchone()["fraud_transactions"] or 0


    # Legitimate transactions
    cursor.execute("""
        SELECT COUNT(*) AS legitimate_transactions
        FROM transactions
        WHERE decision = 'LEGITIMATE'
    """)
    legitimate = cursor.fetchone()["legitimate_transactions"] or 0


    # Total transaction amount
    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0) AS total_amount
        FROM transactions
    """)
    total_amount = cursor.fetchone()["total_amount"] or 0


    # Average fraud probability
    cursor.execute("""
        SELECT COALESCE(AVG(fraud_probability), 0)
        AS average_fraud_probability
        FROM transactions
    """)
    avg_probability = (
        cursor.fetchone()["average_fraud_probability"]
        or 0
    )


    # Risk distribution
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


    # Transaction type distribution
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


    # Fraud rate
    fraud_rate = 0

    if total > 0:

        fraud_rate = (
            fraud / total
        ) * 100


    cursor.close()
    connection.close()


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