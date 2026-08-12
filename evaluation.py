def evaluate_response(response):
    if not response or len(response):
        return "Poor"
    elif "error" in response.lower():
        return "Review"
    else:
        return "Good"
    