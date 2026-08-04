import re
NAME_RE = re.compile(r"^[A-Za-z\s.'&-]{2,100}$")
PERSON_NAME_RE = re.compile(r"^[A-Za-z\s.'-]{2,100}$")
CODE_RE = re.compile(r"^[A-Za-z0-9\-_]{1,20}$")
SYMBOL_RE = re.compile(r"^[A-Za-z]{1,10}$")
PHONE_RE = re.compile(r"^[6-9]\d{9}$")
LOCATION_RE = re.compile(r"^[A-Za-z0-9\s,\-/#]{2,100}$")
QUANTITY_RE = re.compile(r"^\d+$")


def validate_required(value, label="This field"):
    if value is None or value.strip() == "":
        return f"{label} is required."
    return None


def validate_name(value, label="Name"):
    if value is None or value.strip() == "":
        return f"{label} is required."
    if not NAME_RE.match(value.strip()):
        return f"{label} must be 2-100 characters, letters only."
    return None

def validate_person_name(value, label="Name"):
    if value is None or value.strip() == "":
        return f"{label} is required."
    if not PERSON_NAME_RE.match(value.strip()):
        return f"{label} must be 2-100 characters, letters only."
    return None


def validate_optional_person_name(value, label="Name"):
  
    if value is None or value.strip() == "":
        return None
    if not PERSON_NAME_RE.match(value.strip()):
        return f"{label} must be letters only."
    return None


def validate_code(value, label="Code"):
  
    if value is None or value.strip() == "":
        return None
    if not CODE_RE.match(value.strip()):
        return f"{label} may only contain letters, numbers, - and _ (max 20 chars)."
    return None


def validate_symbol(value, label="Symbol"):
    if value is None or value.strip() == "":
        return None
    if not SYMBOL_RE.match(value.strip()):
        return f"{label} must be letters only (max 10 characters)."
    return None


def validate_phone(value, label="Phone"):
    if value is None or value.strip() == "":
        return None
    if not PHONE_RE.match(value.strip()):
        return f"{label} must be a valid 10-digit mobile number."
    return None


def validate_location(value, label="Location"):
    if value is None or value.strip() == "":
        return None
    v = value.strip()
    if len(v) < 2 or len(v) > 100:
        return f"{label} must be 2-100 characters."
    if not LOCATION_RE.match(v):
        return f"{label} contains invalid characters."
    return None


def validate_quantity(value, label="Quantity"):
    if value is None or value.strip() == "":
        return f"{label} is required."
    v = value.strip()
    if not QUANTITY_RE.match(v):
        return f"{label} must be a whole number."
    if int(v) <= 0:
        return f"{label} must be greater than 0."
    return None


def validate_free_text(value, label="This field", min_len=2, max_len=100):
    if value is None or value.strip() == "":
        return f"{label} is required."
    v = value.strip()
    if len(v) < min_len or len(v) > max_len:
        return f"{label} must be {min_len}-{max_len} characters."
    return None


def validate_positive_int(value, label="This field"):
    if value is None or value.strip() == "":
        return f"{label} is required."
    try:
        if int(value.strip()) <= 0:
            return f"{label} is invalid."
    except ValueError:
        return f"{label} is invalid."
    return None


def validate_password(value, label="Password", min_len=6):
  
    if value is None or value == "":
        return f"{label} is required."
    if len(value) < min_len:
        return f"{label} must be at least {min_len} characters."
    return None


def first_error(*errors):
    for e in errors:
        if e:
            return e
    return None