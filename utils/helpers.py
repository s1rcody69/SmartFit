from datetime import date, datetime


def format_date(date_str: str) -> str:
    """
    Converts '2026-05-01' to 'May 01, 2026'.
    Returns original string if formatting fails.
    """
    try:
        d = date.fromisoformat(date_str)
        return d.strftime("%B %d, %Y")
    except Exception:
        return date_str or "N/A"


def days_until(date_str: str) -> int:
    """
    Returns how many days until a given date.
    Negative means already passed.
    """
    try:
        target = date.fromisoformat(date_str)
        return (target - date.today()).days
    except Exception:
        return 0


def membership_status_color(days_left: int) -> str:
    """
    Returns a colour based on how many days left
    on a membership.
    """
    if days_left < 0:
        return "#e94560"   # Red — expired
    elif days_left <= 7:
        return "#f39c12"   # Orange — expiring soon
    else:
        return "#2ecc71"   # Green — active


def validate_email(email: str) -> bool:
    """Basic email format check."""
    return "@" in email and "." in email.split("@")[-1]


def validate_phone(phone: str) -> bool:
    """Checks phone is at least 10 digits."""
    digits = [c for c in phone if c.isdigit()]
    return len(digits) >= 10


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """Returns BMI rounded to 1 decimal place."""
    if height_cm <= 0:
        return 0.0
    return round(weight_kg / ((height_cm / 100) ** 2), 1)


def bmi_category(bmi: float) -> str:
    """Returns the BMI category label."""
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal Weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"


def current_timestamp() -> str:
    """Returns current datetime as a formatted string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def truncate(text: str, max_len: int = 40) -> str:
    """Shortens long strings for table display."""
    if not text:
        return ""
    return text if len(text) <= max_len else text[:max_len - 3] + "..."