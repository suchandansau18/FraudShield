from src.database import (
    get_user_history,
    get_receiver_history
)


print("Sender history:")
user_history = get_user_history("C100")

for transaction in user_history:
    print(transaction)


print("\nReceiver history:")
receiver_history = get_receiver_history("M100")

for transaction in receiver_history:
    print(transaction)