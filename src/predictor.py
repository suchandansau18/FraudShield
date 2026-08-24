import os
import pandas as pd

from xgboost import XGBClassifier

from .feature_engineering import (
    generate_realtime_features,
    add_transaction_type_features
)

from .database import save_transaction


# =========================================================
# MODEL PATH
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MODEL_FILE = os.path.join(
    BASE_DIR,
    "models_saved",
    "behaviour_aware_xgboost.json"
)


# =========================================================
# MODEL FEATURES
# =========================================================

FEATURE_COLUMNS = [

    "step",
    "amount",
    "oldbalanceOrg",
    "newbalanceOrig",
    "oldbalanceDest",
    "newbalanceDest",
    "isFlaggedFraud",

    "user_transaction_count_before",
    "previous_transaction_amount",
    "time_since_previous_transaction",
    "previous_average_amount",
    "amount_deviation",
    "amount_to_previous_average",
    "balance_depletion",
    "amount_to_balance_ratio",

    "receiver_transaction_count_before",
    "receiver_previous_amount",
    "receiver_transaction_frequency",

    "user_transfer_count_before",
    "user_cashout_count_before",

    "transaction_velocity",

    "type_CASH_IN",
    "type_CASH_OUT",
    "type_DEBIT",
    "type_PAYMENT",
    "type_TRANSFER"
]


# =========================================================
# LOAD XGBOOST MODEL
# =========================================================

model = XGBClassifier()

model.load_model(
    MODEL_FILE
)


# =========================================================
# REAL-TIME TRANSACTION PREDICTION
# =========================================================

def predict_realtime_transaction(transaction):

    # -----------------------------------------------------
    # 1. GET PREVIOUS HISTORY AND GENERATE FEATURES
    # -----------------------------------------------------

    features = generate_realtime_features(
        transaction
    )


    # -----------------------------------------------------
    # 2. ADD TRANSACTION TYPE FEATURES
    # -----------------------------------------------------

    features = add_transaction_type_features(
        features,
        transaction["type"]
    )


    # -----------------------------------------------------
    # 3. CREATE DATAFRAME
    # -----------------------------------------------------

    input_df = pd.DataFrame(
        [features]
    )


    # -----------------------------------------------------
    # 4. ENSURE CORRECT FEATURE ORDER
    # -----------------------------------------------------

    input_df = input_df.reindex(
        columns=FEATURE_COLUMNS,
        fill_value=0
    )


    # -----------------------------------------------------
    # 5. HANDLE MISSING VALUES
    # -----------------------------------------------------

    input_df = input_df.fillna(0)


    # -----------------------------------------------------
    # 6. PREDICT FRAUD PROBABILITY
    # -----------------------------------------------------

    probability = model.predict_proba(
        input_df
    )[0, 1]


    # -----------------------------------------------------
    # 7. FRAUD / LEGITIMATE DECISION
    # -----------------------------------------------------

    if probability >= 0.5:

        decision = "FRAUD"

    else:

        decision = "LEGITIMATE"


    # -----------------------------------------------------
    # 8. RISK LEVEL
    # -----------------------------------------------------

    if probability >= 0.8:

        risk_level = "HIGH"

    elif probability >= 0.5:

        risk_level = "MEDIUM"

    else:

        risk_level = "LOW"


    # -----------------------------------------------------
    # 9. SAVE TRANSACTION + PREDICTION RESULT TO MYSQL
    # -----------------------------------------------------

    save_transaction(
        transaction,
        fraud_probability=float(probability),
        decision=decision,
        risk_level=risk_level
    )


    # -----------------------------------------------------
    # 10. RETURN RESULT TO FASTAPI
    # -----------------------------------------------------

    return {

        "fraud_probability":
            float(probability),

        "decision":
            decision,

        "risk_level":
            risk_level
    }
# =========================================================
# PREDICT EXISTING TRANSACTION
# Used for processing old database records.
# IMPORTANT:
# This function does NOT create a new transaction.
# =========================================================

def predict_existing_transaction(transaction):

    # -----------------------------------------------------
    # 1. Generate behaviour-aware features
    # -----------------------------------------------------

    features = generate_realtime_features(
        transaction
    )


    # -----------------------------------------------------
    # 2. Add transaction type features
    # -----------------------------------------------------

    features = add_transaction_type_features(
        features,
        transaction["type"]
    )


    # -----------------------------------------------------
    # 3. Create DataFrame
    # -----------------------------------------------------

    input_df = pd.DataFrame(
        [features]
    )


    # -----------------------------------------------------
    # 4. Ensure correct feature order
    # -----------------------------------------------------

    input_df = input_df.reindex(
        columns=FEATURE_COLUMNS,
        fill_value=0
    )


    # -----------------------------------------------------
    # 5. Handle missing values
    # -----------------------------------------------------

    input_df = input_df.fillna(0)


    # -----------------------------------------------------
    # 6. Predict fraud probability
    # -----------------------------------------------------

    probability = model.predict_proba(
        input_df
    )[0, 1]


    # -----------------------------------------------------
    # 7. Decision
    # -----------------------------------------------------

    if probability >= 0.5:

        decision = "FRAUD"

    else:

        decision = "LEGITIMATE"


    # -----------------------------------------------------
    # 8. Risk level
    # -----------------------------------------------------

    if probability >= 0.8:

        risk_level = "HIGH"

    elif probability >= 0.5:

        risk_level = "MEDIUM"

    else:

        risk_level = "LOW"


    # -----------------------------------------------------
    # 9. Return prediction
    # -----------------------------------------------------

    return {

        "fraud_probability":
            float(probability),

        "decision":
            decision,

        "risk_level":
            risk_level
    }