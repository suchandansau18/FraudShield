from src.feature_engineering import (
    generate_realtime_features,
    add_transaction_type_features
)


transaction = {
    "step": 2,
    "type": "CASH_OUT",
    "amount": 500,
    "nameOrig": "C100",
    "oldbalanceOrg": 4000,
    "newbalanceOrig": 3500,
    "nameDest": "M100",
    "oldbalanceDest": 1000,
    "newbalanceDest": 1500,
    "isFlaggedFraud": 0
}


features = generate_realtime_features(
    transaction
)


features = add_transaction_type_features(
    features,
    transaction["type"]
)


print("Generated features:")
print(features)

print("\nNumber of features:")
print(len(features))