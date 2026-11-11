import math


def parse_setpoint(text):
    """Parse temperature string like '21.5C' or '70F' and return Celsius as float."""
    if not text or not isinstance(text, str):
        raise ValueError("Input must be a non-empty string")
    
    if len(text) < 2:
        raise ValueError("Input must have at least a value and unit (e.g., '21C')")
    
    unit = text[-1].upper()
    if unit not in ('C', 'F'):
        raise ValueError("Unit must be 'C' or 'F'")
    
    value_str = text[:-1]
    try:
        value = float(value_str)
    except ValueError:
        raise ValueError(f"Invalid temperature value: '{value_str}'")
    
    if unit == 'F':
        value = (value - 32) * 5 / 9
    
    return round(value, 1)


def average_temperature(readings_csv):
    """Compute average of comma-separated temperature readings."""
    if not readings_csv or not isinstance(readings_csv, str):
        raise ValueError("Input must be a non-empty string")
    
    readings_csv = readings_csv.strip()
    if not readings_csv:
        raise ValueError("Input cannot be empty or whitespace only")
    
    parts = readings_csv.split(',')
    values = []
    for part in parts:
        part = part.strip()
        if not part:
            raise ValueError("Empty reading in CSV")
        try:
            val = float(part)
            if not math.isfinite(val):
                raise ValueError(f"Invalid temperature reading: '{part}' (infinity or NaN not allowed)")
            values.append(val)
        except ValueError as e:
            if "Invalid temperature reading" in str(e):
                raise
            raise ValueError(f"Invalid temperature reading: '{part}'")
    
    if not values:
        raise ValueError("No valid readings provided")
    
    return sum(values) / len(values)


def schedule_slot(time_text):
    """Label time slot as 'day HH:MM' or 'night HH:MM' based on hour (< 6 = night)."""
    if not time_text or not isinstance(time_text, str):
        raise ValueError("Input must be a non-empty string")
    
    if ':' not in time_text:
        raise ValueError("Time must be in HH:MM format")
    
    parts = time_text.split(':')
    if len(parts) != 2:
        raise ValueError("Time must be in HH:MM format")
    
    hour_str, minute_str = parts
    
    try:
        hour = int(hour_str)
    except ValueError:
        raise ValueError(f"Invalid hour: '{hour_str}'")
    
    try:
        minute = int(minute_str)
    except ValueError:
        raise ValueError(f"Invalid minute: '{minute_str}'")
    
    if not (0 <= hour <= 23):
        raise ValueError(f"Hour must be 0-23, got {hour}")
    
    if not (0 <= minute <= 59):
        raise ValueError(f"Minute must be 0-59, got {minute}")
    
    # Zero-pad minute for consistent output
    minute_formatted = f"{minute:02d}"
    
    if hour < 6:
        return f'night {minute_formatted}'
    return f'day {minute_formatted}'


def main():
    print("==== Running parse_setpoint ====")
    user_input = input("Enter a setpoint (e.g. 21.5C or 70F): ")
    try:
        result = parse_setpoint(user_input)
        print("Setpoint in Celsius:", result)
    except ValueError as e:
        print("Error:", e)

    print("\n==== Running average_temperature ====")
    user_input = input("Enter sensor readings as CSV (e.g. 20.5,21,22.5): ")
    try:
        result = average_temperature(user_input)
        print("Average Temperature:", result)
    except ValueError as e:
        print("Error:", e)

    print("\n==== Running schedule_slot ====")
    user_input = input("Enter a time as HH:MM (e.g. 07:30): ")
    try:
        result = schedule_slot(user_input)
        print("Schedule Slot:", result)
    except ValueError as e:
        print("Error:", e)


if __name__ == "__main__":
    main()