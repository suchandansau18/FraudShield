import os

import mysql.connector
from mysql.connector import Error

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
    "database": os.getenv("DB_NAME"),

    # Aiven requires SSL
    "ssl_disabled": False,

    # Connection timeout
    "connection_timeout": 15
}


# =========================================================
# VALIDATE DATABASE CONFIGURATION
# =========================================================

def validate_database_config():

    required_variables = [
        "DB_HOST",
        "DB_PORT",
        "DB_USER",
        "DB_PASSWORD",
        "DB_NAME"
    ]

    missing_variables = [
        variable
        for variable in required_variables
        if not os.getenv(variable)
    ]

    if missing_variables:

        raise RuntimeError(
            "Missing database environment variables: "
            + ", ".join(missing_variables)
        )


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():

    validate_database_config()

    try:

        connection = mysql.connector.connect(
            **DB_CONFIG
        )

        if not connection.is_connected():

            raise RuntimeError(
                "MySQL connection was not established."
            )

        return connection

    except Error as error:

        print(
            f"MySQL connection failed: {error}"
        )

        raise


# =========================================================
# GET SENDER HISTORY
# =========================================================

def get_sender_history(name_orig):

    connection = get_connection()

    cursor = connection.cursor(dictionary=True)

    try:

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

        return cursor.fetchall()

    finally:

        cursor.close()
        connection.close()


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

    try:

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

        return cursor.fetchall()

    finally:

        cursor.close()
        connection.close()


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

    try:

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

    finally:

        cursor.close()
        connection.close()


# =========================================================
# GET RECENT TRANSACTIONS
# =========================================================

def get_recent_transactions(limit=10):

    connection = get_connection()

    cursor = connection.cursor(dictionary=True)

    try:

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

        return cursor.fetchall()

    finally:

        cursor.close()
        connection.close()


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

    try:

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

        return cursor.rowcount

    finally:

        cursor.close()
        connection.close()