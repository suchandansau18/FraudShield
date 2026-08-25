import os

import mysql.connector

from dotenv import load_dotenv

load_dotenv()


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}


# =========================================================
# DATABASE CONNECTION
# =========================================================
def get_connection():

    connection = mysql.connector.connect(
        **DB_CONFIG,
        ssl_disabled=False
    )

    return connection



# =========================================================
# GET SENDER HISTORY
# =========================================================

def get_sender_history(name_orig):

    connection = get_connection()

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            step,
            amount,
            transaction_type
        FROM transactions
        WHERE name_orig = %s
        ORDER BY step ASC
    """

    cursor.execute(
        query,
        (name_orig,)
    )

    history = cursor.fetchall()

    cursor.close()
    connection.close()

    return history


# =========================================================
# GET USER HISTORY
# =========================================================

def get_user_history(name_orig):

    return get_sender_history(name_orig)


# =========================================================
# GET RECEIVER HISTORY
# =========================================================

def get_receiver_history(name_dest):

    connection = get_connection()

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            step,
            amount
        FROM transactions
        WHERE name_dest = %s
        ORDER BY step ASC
    """

    cursor.execute(
        query,
        (name_dest,)
    )

    history = cursor.fetchall()

    cursor.close()
    connection.close()

    return history


# =========================================================
# SAVE TRANSACTION + PREDICTION RESULT
# =========================================================

def save_transaction(
    transaction,
    fraud_probability=None,
    decision=None,
    risk_level=None
):

    connection = get_connection()

    cursor = connection.cursor()

    query = """
        INSERT INTO transactions (
            step,
            transaction_type,
            amount,
            name_orig,
            old_balance_orig,
            new_balance_orig,
            name_dest,
            old_balance_dest,
            new_balance_dest,
            is_flagged_fraud,
            fraud_probability,
            decision,
            risk_level
        )
        VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s
        )
    """

    values = (
        transaction["step"],
        transaction["type"],
        transaction["amount"],
        transaction["nameOrig"],
        transaction["oldbalanceOrg"],
        transaction["newbalanceOrig"],
        transaction["nameDest"],
        transaction["oldbalanceDest"],
        transaction["newbalanceDest"],
        transaction.get("isFlaggedFraud", 0),
        fraud_probability,
        decision,
        risk_level
    )

    cursor.execute(
        query,
        values
    )

    connection.commit()

    cursor.close()
    connection.close()


# =========================================================
# GET RECENT TRANSACTIONS
# =========================================================

def get_recent_transactions(limit=10):

    connection = get_connection()

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            id,
            step,
            transaction_type,
            amount,
            name_orig,
            name_dest,

            old_balance_orig,
            new_balance_orig,
            old_balance_dest,
            new_balance_dest,

            fraud_probability,
            decision,
            risk_level,
            created_at

        FROM transactions

        ORDER BY id DESC

        LIMIT %s
    """

    cursor.execute(
        query,
        (limit,)
    )

    transactions = cursor.fetchall()

    cursor.close()

    connection.close()

    return transactions
# =========================================================
# UPDATE EXISTING TRANSACTION PREDICTION
# =========================================================

def update_transaction_prediction(
    transaction_id,
    fraud_probability,
    decision,
    risk_level
):

    connection = get_connection()

    cursor = connection.cursor()

    query = """
        UPDATE transactions

        SET
            fraud_probability = %s,
            decision = %s,
            risk_level = %s

        WHERE id = %s
    """

    cursor.execute(
        query,
        (
            float(fraud_probability),
            decision,
            risk_level,
            transaction_id
        )
    )

    connection.commit()

    updated_rows = cursor.rowcount

    cursor.close()

    connection.close()

    return updated_rows