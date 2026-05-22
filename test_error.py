import sys

# add to path
sys.path.insert(0, r"c:\Users\subhankar nath\Desktop\Legal-Tech")

# Configure basic logging to see details
import logging
logging.basicConfig(level=logging.INFO)

from apps.worker.tasks.generate_counter_offer import generate_counter_offer_task

def main():
    clause_id = "77352e66-12ff-4b1d-a51f-e14b9ec85f09"
    print(f"Testing synchronously with clause_id={clause_id}")
    try:
        # Run without Celery, executing the task directly in this process synchronously
        # We do generate_counter_offer_task.run so it does not trigger Celery retry raises
        res = generate_counter_offer_task.run(clause_id)
        print("Success!", res)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
