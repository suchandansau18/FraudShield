import mysql.connector

from src.predictor import predict_existing_transaction
from src.database import (
    get_connection,
    update_transaction_prediction
)


# =========================================================
# PROCESS OLD UNPROCESSED TRANSACTIONS
# =========================================================

def process_old_transactions():

    connection = get_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    # -----------------------------------------------------
    # Get only transactions that have no prediction yet
    # -----------------------------------------------------

    cursor.execute("""
        SELECT *
        FROM transactions
        WHERE fraud_probability IS NULL
           OR decision IS NULL
           OR risk_level IS NULL
        ORDER BY id
    """)

    transactions = cursor.fetchall()

    cursor.close()
    connection.close()


    if not transactions:

        print(
            "No unprocessed transactions found."
        )

        return


    print(
        f"\nFound {len(transactions)} "
        "unprocessed transactions.\n"
    )


    processed = 0


    # =====================================================
    # PROCESS EACH EXISTING TRANSACTION
    # =====================================================

    for transaction in transactions:

        transaction_id = transaction["id"]

        print(
            f"Processing transaction "
            f"ID {transaction_id}..."
        )


        # -------------------------------------------------
        # Convert database column names to the format
        # expected by predictor.py
        # -------------------------------------------------

        prediction_transaction = {

            "step":
                transaction["step"],

            "type":
                transaction["transaction_type"],

            "amount":
                transaction["amount"],

            "nameOrig":
                transaction["name_orig"],

            "oldbalanceOrg":
                transaction["old_balance_orig"]
                or 0,

            "newbalanceOrig":
                transaction["new_balance_orig"]
                or 0,

            "nameDest":
                transaction["name_dest"],

            "oldbalanceDest":
                transaction["old_balance_dest"]
                or 0,

            "newbalanceDest":
                transaction["new_balance_dest"]
                or 0,

            "isFlaggedFraud":
                transaction["is_flagged_fraud"]
                or 0
        }


        try:

            # ---------------------------------------------
            # Run the EXISTING XGBoost prediction.
            #
            # This function DOES NOT save a new row.
            # ---------------------------------------------

            result = predict_existing_transaction(
                prediction_transaction
            )


            # ---------------------------------------------
            # Update the existing database row
            # ---------------------------------------------

            updated_rows = (
                update_transaction_prediction(

                    transaction_id,

                    result[
                        "fraud_probability"
                    ],

                    result[
                        "decision"
                    ],

                    result[
                        "risk_level"
                    ]
                )
            )


            if updated_rows == 1:

                processed += 1

                print(
                    f"  Probability: "
                    f"{result['fraud_probability']:.6f}"
                )

                print(
                    f"  Decision: "
                    f"{result['decision']}"
                )

                print(
                    f"  Risk: "
                    f"{result['risk_level']}"
                )

                print(
                    "  ✓ Database updated\n"
                )

            else:

                print(
                    "  ⚠ Database row was not updated\n"
                )


        except Exception as error:

            print(
                f"  ✗ Error processing "
                f"ID {transaction_id}"
            )

            print(
                f"  {error}\n"
            )


    # =====================================================
    # FINAL RESULT
    # =====================================================

    print(
        "========================================"
    )

    print(
        f"Successfully processed: "
        f"{processed}/{len(transactions)}"
    )

    print(
        "========================================"
    )


# =========================================================
# RUN SCRIPT
# =========================================================

if __name__ == "__main__":

    process_old_transactions()