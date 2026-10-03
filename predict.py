from laya import Router
import time

# Initialize the router
router = Router(preload=True)

# Define state and questions
state = "Hi, we were billed twice for March. Please refund the duplicate today."
questions = {
    "department": {
        "type": "choice",
        "instructions": "Which department should handle this?",
        "criteria": {"billing": "Refunds and invoices", "tech": "Technical support"}
    },
    "urgency": {
        "type": "score",
        "instructions": "How urgent is this?",
        "criteria": ["Low", "Medium", "High"]
    }
}

# Perform the prediction
print(f"Running prediction for state: '{state}'...")
start_time = time.time()
result = router.predict(state, questions)
end_time = time.time()
print(f"\nFirst prediction (Cold Start) took {end_time - start_time:.4f} seconds")

start_time_2 = time.time()
result_2 = router.predict(state, questions)
end_time_2 = time.time()
print(f"Second prediction (Warm Start) took {end_time_2 - start_time_2:.4f} seconds")

import json
print("\nPrediction Result:")
print(json.dumps(result, indent=2))
