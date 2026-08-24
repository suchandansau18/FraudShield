import numpy as np
import pandas as pd

from .database import (
    get_user_history,
    get_receiver_history
)


# Transaction types used by the XGBoost model
TRANSACTION_TYPES = [
    "CASH_IN",
    "CASH_OUT",
    "DEBIT",
    "PAYMENT",
    "TRANSFER"
]


def generate_realtime_features(transaction):

    user = transaction["nameOrig"]
    receiver = transaction["nameDest"]

    step = transaction["step"]
    amount = transaction["amount"]
    transaction_type = transaction["type"]


    # =========================================================
    # 1. GET SENDER HISTORY FROM MYSQL
    # =========================================================

    user_hist = get_user_history(user)

    user_transaction_count_before = len(user_hist)


    # =========================================================
    # 2. SENDER PREVIOUS TRANSACTION FEATURES
    # =========================================================

    if len(user_hist) > 0:

        previous_transaction_amount = (
            user_hist[-1]["amount"]
        )

        previous_step = (
            user_hist[-1]["step"]
        )

        time_since_previous_transaction = (
            step - previous_step
        )

        previous_average_amount = np.mean(
            [
                x["amount"]
                for x in user_hist
            ]
        )

    else:

        previous_transaction_amount = np.nan

        time_since_previous_transaction = np.nan

        previous_average_amount = np.nan


    # =========================================================
    # 3. AMOUNT BEHAVIOUR
    # =========================================================

    if pd.notna(previous_average_amount):

        amount_deviation = (
            amount - previous_average_amount
        )

        if previous_average_amount != 0:

            amount_to_previous_average = (
                amount / previous_average_amount
            )

        else:

            amount_to_previous_average = 0

    else:

        amount_deviation = np.nan

        amount_to_previous_average = np.nan


    # =========================================================
    # 4. GET RECEIVER HISTORY FROM MYSQL
    # =========================================================

    receiver_hist = get_receiver_history(
        receiver
    )

    receiver_transaction_count_before = (
        len(receiver_hist)
    )


    # =========================================================
    # 5. RECEIVER HISTORY FEATURES
    # =========================================================

    if len(receiver_hist) > 0:

        receiver_previous_amount = (
            receiver_hist[-1]["amount"]
        )

        first_receiver_step = (
            receiver_hist[0]["step"]
        )

        receiver_transaction_frequency = (
            len(receiver_hist)
            /
            max(
                step - first_receiver_step,
                1
            )
        )

    else:

        receiver_previous_amount = np.nan

        receiver_transaction_frequency = np.nan


    # =========================================================
    # 6. USER TRANSACTION TYPE BEHAVIOUR
    # =========================================================

    user_transfer_count_before = sum(
        1
        for x in user_hist
        if x["transaction_type"] == "TRANSFER"
    )


    user_cashout_count_before = sum(
        1
        for x in user_hist
        if x["transaction_type"] == "CASH_OUT"
    )


    # =========================================================
    # 7. TRANSACTION VELOCITY
    # =========================================================

    transaction_velocity = len(user_hist)


    # =========================================================
    # 8. BALANCE FEATURES
    # =========================================================

    oldbalance_org = transaction[
        "oldbalanceOrg"
    ]

    newbalance_orig = transaction[
        "newbalanceOrig"
    ]

    oldbalance_dest = transaction[
        "oldbalanceDest"
    ]

    newbalance_dest = transaction[
        "newbalanceDest"
    ]


    balance_depletion = (
        oldbalance_org
        -
        newbalance_orig
    )


    if oldbalance_org > 0:

        amount_to_balance_ratio = (
            amount / oldbalance_org
        )

    else:

        amount_to_balance_ratio = 0


    # =========================================================
    # 9. CREATE BEHAVIOURAL FEATURES
    # =========================================================

    features = {

        "step": step,

        "amount": amount,

        "oldbalanceOrg": oldbalance_org,

        "newbalanceOrig": newbalance_orig,

        "oldbalanceDest": oldbalance_dest,

        "newbalanceDest": newbalance_dest,

        "isFlaggedFraud":
            transaction.get(
                "isFlaggedFraud",
                0
            ),

        "user_transaction_count_before":
            user_transaction_count_before,

        "previous_transaction_amount":
            previous_transaction_amount,

        "time_since_previous_transaction":
            time_since_previous_transaction,

        "previous_average_amount":
            previous_average_amount,

        "amount_deviation":
            amount_deviation,

        "amount_to_previous_average":
            amount_to_previous_average,

        "balance_depletion":
            balance_depletion,

        "amount_to_balance_ratio":
            amount_to_balance_ratio,

        "receiver_transaction_count_before":
            receiver_transaction_count_before,

        "receiver_previous_amount":
            receiver_previous_amount,

        "receiver_transaction_frequency":
            receiver_transaction_frequency,

        "user_transfer_count_before":
            user_transfer_count_before,

        "user_cashout_count_before":
            user_cashout_count_before,

        "transaction_velocity":
            transaction_velocity
    }


    return features


# =============================================================
# TRANSACTION TYPE FEATURES
# =============================================================

def add_transaction_type_features(
    features,
    transaction_type
):

    for transaction_type_name in TRANSACTION_TYPES:

        features[
            f"type_{transaction_type_name}"
        ] = (
            1
            if transaction_type
            ==
            transaction_type_name
            else 0
        )

    return features