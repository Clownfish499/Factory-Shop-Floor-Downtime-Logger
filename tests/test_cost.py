"""
Test Cost Service & Duration Calculations
Covers Test Cases:
1. Cost calculation for 30 minutes = Rs. 25,000.
2. Cost calculation for 1 hour = Rs. 50,000.
3. Cost calculation for 90 minutes = Rs. 75,000.
4. Duration crossing midnight.
11. Rejecting end time earlier than start time.
"""
import pytest
from datetime import datetime
from services.cost_service import calculate_duration_seconds, calculate_estimated_cost

def test_cost_calculation_30_minutes():
    """Test 1: 30 minutes downtime at Rs. 50,000/hr = Rs. 25,000"""
    duration_30m = 30 * 60  # 1800 seconds
    cost = calculate_estimated_cost(duration_30m)
    assert cost == 25000.0

def test_cost_calculation_1_hour():
    """Test 2: 1 hour downtime at Rs. 50,000/hr = Rs. 50,000"""
    duration_1h = 60 * 60  # 3600 seconds
    cost = calculate_estimated_cost(duration_1h)
    assert cost == 50000.0

def test_cost_calculation_90_minutes():
    """Test 3: 90 minutes downtime at Rs. 50,000/hr = Rs. 75,000"""
    duration_90m = 90 * 60  # 5400 seconds
    cost = calculate_estimated_cost(duration_90m)
    assert cost == 75000.0

def test_duration_crossing_midnight():
    """Test 4: Elapsed duration calculation across midnight"""
    start_dt = datetime(2026, 11, 5, 23, 45, 0)
    end_dt = datetime(2026, 11, 6, 0, 15, 0)
    duration_secs = calculate_duration_seconds(start_dt, end_dt)
    assert duration_secs == 1800  # 30 minutes
    cost = calculate_estimated_cost(duration_secs)
    assert cost == 25000.0

def test_reject_end_time_earlier_than_start_time():
    """Test 11: End time earlier than start time raises ValueError"""
    start_dt = datetime(2026, 11, 5, 10, 0, 0)
    end_dt = datetime(2026, 11, 5, 9, 30, 0)
    with pytest.raises(ValueError, match="End timestamp cannot be earlier than start timestamp"):
        calculate_duration_seconds(start_dt, end_dt)
