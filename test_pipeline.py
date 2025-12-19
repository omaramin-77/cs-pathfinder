from ai_helper import choose_field_from_answers

def run_test():
    sample_answers = {
        "1": {"question": "Do you enjoy building UIs?", "answer": "Yes"},
        "2": {"question": "Do you like working with data?", "answer": "Sometimes"},
        "3": {"question": "Do you enjoy backend work?", "answer": "No"}
    }

    print("Running test with sample data...")
    result = choose_field_from_answers(sample_answers)
    print("API returned:", result)

if __name__ == "__main__":
    run_test()