"""
Cost Calculation Service
Business Rule BR-11:
Estimated downtime cost = elapsed duration in hours * Rs. 50,000.
"""

HOURLY_RATE = 50000.0  # Rs. 50,000 / hour

def calculate_duration_seconds(start_time, end_time):
    """
    Calculates duration in seconds between two datetime objects.
    Ensures start_time <= end_time.
    """
    if start_time > end_time:
        raise ValueError("End timestamp cannot be earlier than start timestamp.")
    delta = end_time - start_time
    return int(delta.total_seconds())

def calculate_estimated_cost(duration_seconds, hourly_rate=HOURLY_RATE):
    """
    Calculates estimated downtime cost in Indian Rupees (INR).
    Cost = (duration_seconds / 3600.0) * hourly_rate
    """
    if duration_seconds < 0:
        raise ValueError("Duration seconds cannot be negative.")
    hours = duration_seconds / 3600.0
    return round(hours * hourly_rate, 2)

def format_currency_inr(amount):
    """Formats float/int into Rs. currency string representation."""
    if amount is None:
        return "N/A"
    return f"Rs. {amount:,.2f}"

def format_duration(seconds):
    """Formats duration seconds into HH:MM:SS or readable text."""
    if seconds is None:
        return "Open / Ongoing"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours}h {minutes}m {secs}s"
