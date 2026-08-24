from src.predictor import predict_realtime_transaction


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


result = predict_realtime_transaction(transaction)


print("Prediction Result:")
print(result)

print("\nFraud Probability:",
      result["fraud_probability"])

print("Decision:",
      result["decision"])

print("Risk Level:",
      result["risk_level"])