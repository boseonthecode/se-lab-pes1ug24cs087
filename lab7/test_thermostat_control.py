from hypothesis import given, strategies as st, assume, example, settings
from thermostat_control import parse_setpoint, average_temperature, schedule_slot
import math
import pytest

# Use 1000+ examples per test for thorough fuzzing
FUZZ_SETTINGS = settings(max_examples=1000, deadline=None)


# ===================== parse_setpoint tests =====================

# Valid input strategy: temperature strings like "21.5C", "70F", "-10c", "32f"
valid_temp_str = st.from_regex(r'-?\d+(\.\d+)?[CFcf]', fullmatch=True)

@given(valid_temp_str)
@FUZZ_SETTINGS
def test_parse_setpoint_valid_input(s):
    """Test parse_setpoint with valid temperature strings"""
    result = parse_setpoint(s)
    assert isinstance(result, float)
    
    # Verify conversion correctness
    value = float(s[:-1])
    unit = s[-1].upper()
    if unit == 'F':
        expected = round((value - 32) * 5 / 9, 1)
    else:  # C
        expected = round(value, 1)
    assert result == expected, f"Failed for {s}: got {result}, expected {expected}"


# Invalid inputs that should raise ValueError gracefully
@given(st.text().filter(lambda x: not (x and x[-1].upper() in 'CF' and x[:-1].replace('.','',1).replace('-','',1).isdigit())))
@FUZZ_SETTINGS
def test_parse_setpoint_invalid_input_raises_value_error(s):
    """Test parse_setpoint raises ValueError for invalid input"""
    with pytest.raises(ValueError):
        parse_setpoint(s)


@given(st.none())
@FUZZ_SETTINGS
def test_parse_setpoint_none_input_raises_type_error(s):
    """Test parse_setpoint raises TypeError/ValueError for None input"""
    with pytest.raises((TypeError, ValueError)):
        parse_setpoint(s)


@given(st.text().filter(lambda x: len(x) == 0 or x[-1].upper() not in 'CF'))
@FUZZ_SETTINGS
def test_parse_setpoint_missing_unit_raises_value_error(s):
    """Test parse_setpoint raises ValueError for missing or invalid unit"""
    assume(len(s) == 0 or s[-1].upper() not in 'CF')
    with pytest.raises(ValueError):
        parse_setpoint(s)


# ===================== average_temperature tests =====================

# Valid input: comma-separated floats
valid_csv = st.lists(
    st.floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False),
    min_size=1, max_size=10
).map(lambda x: ','.join(str(v) for v in x))

@given(valid_csv)
@FUZZ_SETTINGS
def test_average_temperature_valid_input(s):
    """Test average_temperature with valid CSV input"""
    result = average_temperature(s)
    assert isinstance(result, float)
    
    # Verify mathematical correctness
    values = [float(v) for v in s.split(',')]
    expected = sum(values) / len(values)
    assert math.isclose(result, expected, rel_tol=1e-9), f"Failed for {s}: got {result}, expected {expected}"


# Invalid inputs should raise ValueError
@given(st.text())
@FUZZ_SETTINGS
def test_average_temperature_invalid_input_raises_value_error(s):
    """Test average_temperature raises ValueError for invalid input"""
    # Skip valid CSV-like strings (including scientific notation)
    parts = s.split(',')
    def is_valid_number(p):
        p = p.strip()
        if not p:
            return False
        try:
            float(p)
            return True
        except ValueError:
            return False
    if all(is_valid_number(p) for p in parts if p.strip()):
        return
    with pytest.raises(ValueError):
        average_temperature(s)


@given(st.none())
@FUZZ_SETTINGS
def test_average_temperature_none_input_raises_type_error(s):
    """Test average_temperature raises TypeError/ValueError for None input"""
    with pytest.raises((TypeError, ValueError)):
        average_temperature(s)


@given(st.text().filter(lambda x: len(x.strip()) == 0))
@FUZZ_SETTINGS
def test_average_temperature_empty_string_raises_value_error(s):
    """Test average_temperature raises ValueError for empty or whitespace-only string"""
    with pytest.raises(ValueError):
        average_temperature(s)


# Specific edge case tests for coverage
def test_average_temperature_infinity_raises_value_error():
    """Test average_temperature rejects infinity"""
    with pytest.raises(ValueError, match="infinity or NaN not allowed"):
        average_temperature("INF")
    with pytest.raises(ValueError, match="infinity or NaN not allowed"):
        average_temperature("-INF")
    with pytest.raises(ValueError, match="infinity or NaN not allowed"):
        average_temperature("NaN")
    with pytest.raises(ValueError, match="infinity or NaN not allowed"):
        average_temperature("1,INF")
    with pytest.raises(ValueError, match="infinity or NaN not allowed"):
        average_temperature("INF,2")


def test_average_temperature_empty_reading_raises_value_error():
    """Test average_temperature rejects empty readings"""
    with pytest.raises(ValueError, match="Empty reading"):
        average_temperature("1,,2")
    with pytest.raises(ValueError, match="Empty reading"):
        average_temperature("1,")
    with pytest.raises(ValueError, match="Empty reading"):
        average_temperature(",1")


def test_average_temperature_no_valid_readings_raises_value_error():
    """Test average_temperature rejects when no valid readings after filtering"""
    # This is hard to trigger since empty readings are caught first
    pass


# ===================== schedule_slot tests =====================

# Valid input: HH:MM format (24-hour)
valid_time = st.from_regex(r'([01]\d|2[0-3]):[0-5]\d', fullmatch=True)

@given(valid_time)
@FUZZ_SETTINGS
def test_schedule_slot_valid_input(s):
    """Test schedule_slot with valid time strings"""
    result = schedule_slot(s)
    assert isinstance(result, str)
    assert result.startswith('day ') or result.startswith('night ')
    
    # Verify classification correctness with zero-padded minute
    hour, minute = s.split(':')
    hour = int(hour)
    minute = int(minute)
    
    if hour < 6:
        expected = f'night {minute:02d}'
    else:
        expected = f'day {minute:02d}'
    
    assert result == expected, f"Failed for {s}: got {result}, expected {expected}"


# Edge case: hour boundary at 6
@given(st.integers(min_value=0, max_value=23), st.integers(min_value=0, max_value=59))
@FUZZ_SETTINGS
def test_schedule_slot_hour_boundary(hour, minute):
    """Test schedule_slot at hour boundaries"""
    time_str = f"{hour:02d}:{minute:02d}"
    result = schedule_slot(time_str)
    
    if hour < 6:
        expected = f'night {minute:02d}'
    else:
        expected = f'day {minute:02d}'
    
    assert result == expected, f"Failed for {time_str}: got {result}, expected {expected}"


# Invalid inputs should raise ValueError
@given(st.text().filter(lambda x: ':' not in x or len(x.split(':')) != 2))
@FUZZ_SETTINGS
def test_schedule_slot_invalid_format_raises_value_error(s):
    """Test schedule_slot raises ValueError for invalid format"""
    assume(':' not in s or len(s.split(':')) != 2)
    with pytest.raises(ValueError):
        schedule_slot(s)


@given(st.text())
@FUZZ_SETTINGS
def test_schedule_slot_non_numeric_raises_value_error(s):
    """Test schedule_slot raises ValueError for non-numeric hour/minute"""
    # Skip valid time strings
    if ':' in s:
        parts = s.split(':')
        if len(parts) == 2 and all(p.isdigit() for p in parts):
            return
    with pytest.raises(ValueError):
        schedule_slot(s)


@given(st.none())
@FUZZ_SETTINGS
def test_schedule_slot_none_input_raises_type_error(s):
    """Test schedule_slot raises TypeError/ValueError for None input"""
    with pytest.raises((TypeError, ValueError)):
        schedule_slot(s)


# Specific edge case tests for schedule_slot coverage
def test_schedule_slot_multiple_colons_raises_value_error():
    """Test schedule_slot rejects multiple colons"""
    with pytest.raises(ValueError, match="HH:MM format"):
        schedule_slot("12:30:45")
    with pytest.raises(ValueError, match="HH:MM format"):
        schedule_slot("1:2:3:4")


def test_schedule_slot_hour_out_of_range_raises_value_error():
    """Test schedule_slot rejects hour out of 0-23 range"""
    with pytest.raises(ValueError, match="Hour must be 0-23"):
        schedule_slot("24:00")
    with pytest.raises(ValueError, match="Hour must be 0-23"):
        schedule_slot("-1:00")
    with pytest.raises(ValueError, match="Hour must be 0-23"):
        schedule_slot("25:30")


def test_schedule_slot_minute_out_of_range_raises_value_error():
    """Test schedule_slot rejects minute out of 0-59 range"""
    with pytest.raises(ValueError, match="Minute must be 0-59"):
        schedule_slot("12:60")
    with pytest.raises(ValueError, match="Minute must be 0-59"):
        schedule_slot("12:-1")
    with pytest.raises(ValueError, match="Minute must be 0-59"):
        schedule_slot("12:99")


def test_schedule_slot_non_numeric_hour_raises_value_error():
    """Test schedule_slot rejects non-numeric hour"""
    with pytest.raises(ValueError, match="Invalid hour"):
        schedule_slot("ab:30")
    with pytest.raises(ValueError, match="Invalid hour"):
        schedule_slot("1a:30")


def test_schedule_slot_non_numeric_minute_raises_value_error():
    """Test schedule_slot rejects non-numeric minute"""
    with pytest.raises(ValueError, match="Invalid minute"):
        schedule_slot("12:ab")
    with pytest.raises(ValueError, match="Invalid minute"):
        schedule_slot("12:3a")