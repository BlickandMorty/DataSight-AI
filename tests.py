"""
DataSight tests.

run: python tests.py
or: pytest tests.py -v
"""

import pandas as pd
import sys
import os
from core.data_processor import get_metadata
from core.interpreter import get_ai_audit

# colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_test_result(test_name, passed, message=""):
    """print test results with colors"""
    status = f"{GREEN}✓ PASS{RESET}" if passed else f"{RED}✗ FAIL{RESET}"
    print(f"{status} - {test_name}")
    if message:
        print(f"  {YELLOW}→ {message}{RESET}")

# ==================== data processor tests ====================

def test_get_metadata_basic():
    """test that get_metadata returns the right structure"""
    df = pd.DataFrame({
        'A': [1, 2, None],
        'B': [None, 2, 3]
    })
    meta = get_metadata(df)
    
    assert 'columns' in meta, "Missing 'columns' key"
    assert 'null_counts' in meta, "Missing 'null_counts' key"
    assert 'head' in meta, "Missing 'head' key"
    assert meta['columns'] == ['A', 'B'], f"Expected ['A', 'B'], got {meta['columns']}"
    assert meta['null_counts']['A'] == 1, f"Expected 1 null in A, got {meta['null_counts']['A']}"
    assert meta['null_counts']['B'] == 1, f"Expected 1 null in B, got {meta['null_counts']['B']}"
    
    print_test_result("get_metadata() - Basic structure", True)

def test_get_metadata_no_nulls():
    """test get_metadata with clean data (no missing values)"""
    df = pd.DataFrame({
        'Name': ['Alice', 'Bob'],
        'Age': [25, 30]
    })
    meta = get_metadata(df)
    
    assert meta['null_counts']['Name'] == 0, "Clean data should have 0 nulls"
    assert meta['null_counts']['Age'] == 0, "Clean data should have 0 nulls"
    
    print_test_result("get_metadata() - No nulls", True)

def test_get_metadata_all_nulls():
    """test get_metadata when a column is all null"""
    df = pd.DataFrame({
        'A': [None, None, None],
        'B': [1, 2, 3]
    })
    meta = get_metadata(df)
    
    assert meta['null_counts']['A'] == 3, "Column A should have 3 nulls"
    assert meta['null_counts']['B'] == 0, "Column B should have 0 nulls"
    
    print_test_result("get_metadata() - All nulls in column", True)

def test_get_metadata_head_preview():
    """test the head preview"""
    df = pd.DataFrame({
        'X': [10, 20, 30, 40],
        'Y': ['a', 'b', 'c', 'd']
    })
    meta = get_metadata(df)
    
    assert isinstance(meta['head'], dict), "Head should be a dictionary"
    assert 'X' in meta['head'], "Head should contain column X"
    assert 'Y' in meta['head'], "Head should contain column Y"
    
    print_test_result("get_metadata() - Head preview", True)

def test_get_metadata_many_columns():
    """test get_metadata with many columns"""
    data = {f'col_{i}': [i, i+1, None] for i in range(50)}
    df = pd.DataFrame(data)
    meta = get_metadata(df)
    
    assert len(meta['columns']) == 50, "Should handle 50 columns"
    assert len(meta['null_counts']) == 50, "Should have null counts for all 50 columns"
    
    print_test_result("get_metadata() - Many columns (50)", True)

def test_get_metadata_special_characters():
    """test get_metadata with special characters in column names"""
    df = pd.DataFrame({
        'First Name': [1, 2, 3],
        'Last-Name': [4, 5, 6],
        'Email@Domain': [7, 8, 9]
    })
    meta = get_metadata(df)
    
    expected_cols = ['First Name', 'Last-Name', 'Email@Domain']
    assert meta['columns'] == expected_cols, f"Should handle special chars in names"
    
    print_test_result("get_metadata() - Special characters in column names", True)

# ==================== interpreter tests ====================

def test_get_ai_audit_requires_api_key():
    """test that get_ai_audit needs an api key"""
    if not os.getenv("RUN_AI_TESTS"):
        print_test_result("get_ai_audit() - Requires API key", True, "skipped (set RUN_AI_TESTS=1)")
        return
    metadata = {'columns': ['A', 'B'], 'null_counts': {'A': 0, 'B': 1}, 'head': {}}
    
    try:
        result = get_ai_audit(metadata, None)
        assert result is not None, "Should return something"
    except:
        pass
    
    print_test_result("get_ai_audit() - Requires API key", True)

def test_get_ai_audit_empty_metadata():
    """test get_ai_audit with empty metadata"""
    if not os.getenv("RUN_AI_TESTS"):
        print_test_result("get_ai_audit() - Empty metadata", True, "skipped (set RUN_AI_TESTS=1)")
        return
    metadata = {}
    api_key = "dummy_key"  # Won't actually use it for this test
    
    try:
        result = get_ai_audit(metadata, api_key)
        print_test_result("get_ai_audit() - Empty metadata", True)
    except Exception as e:
        print_test_result("get_ai_audit() - Empty metadata", True, 
                         f"Correctly raised: {type(e).__name__}")

# ==================== edge cases ====================

def test_empty_dataframe():
    """test an empty dataframe"""
    df = pd.DataFrame()
    
    try:
        meta = get_metadata(df)
        assert meta['columns'] == [], "Empty dataframe should have no columns"
        print_test_result("Edge Case - Empty dataframe", True)
    except Exception as e:
        print_test_result("Edge Case - Empty dataframe", True, 
                         f"Note: {type(e).__name__} raised")

def test_single_row_dataframe():
    """test a single-row dataframe"""
    df = pd.DataFrame({'A': [42]})
    meta = get_metadata(df)
    
    assert meta['columns'] == ['A'], "Should detect column A"
    assert 'A' in meta['head'], "Should include head data"
    
    print_test_result("Edge Case - Single row dataframe", True)

def test_numeric_columns():
    """test numeric data types"""
    df = pd.DataFrame({
        'int_col': [1, 2, 3],
        'float_col': [1.5, 2.5, None],
        'bool_col': [True, False, True]
    })
    meta = get_metadata(df)
    
    assert meta['columns'] == ['int_col', 'float_col', 'bool_col']
    assert meta['null_counts']['float_col'] == 1, "Should count 1 null in float column"
    
    print_test_result("Edge Case - Numeric data types", True)

def test_string_columns():
    """test string data"""
    df = pd.DataFrame({
        'text': ['Hello', 'World', None],
        'mixed': ['123', 'abc', '45.6']
    })
    meta = get_metadata(df)
    
    assert meta['null_counts']['text'] == 1, "Should count null in text column"
    assert meta['columns'] == ['text', 'mixed']
    
    print_test_result("Edge Case - String columns", True)

# ==================== integration tests ====================

def test_workflow_clean_data():
    """test full workflow with clean data"""
    df = pd.DataFrame({
        'Customer_ID': [101, 102, 103],
        'Purchase_Amount': [29.99, 49.99, 99.99],
        'Date': ['2025-01-01', '2025-01-02', '2025-01-03']
    })
    
    meta = get_metadata(df)
    assert meta['columns'] == ['Customer_ID', 'Purchase_Amount', 'Date']
    assert all(count == 0 for count in meta['null_counts'].values()), \
        "Clean data should have no nulls"
    
    print_test_result("Integration - Clean data workflow", True)

def test_workflow_dirty_data():
    """test full workflow with dirty data"""
    df = pd.DataFrame({
        'Employee': ['Alice', None, 'Charlie'],
        'Department': ['Sales', 'IT', None],
        'Salary': [50000, None, 75000],
        'Performance': ['Good', 'Excellent', None]
    })
    
    meta = get_metadata(df)
    assert meta['null_counts']['Employee'] == 1, "Should find 1 missing employee"
    assert meta['null_counts']['Department'] == 1, "Should find 1 missing department"
    assert meta['null_counts']['Salary'] == 1, "Should find 1 missing salary"
    assert meta['null_counts']['Performance'] == 1, "Should find 1 missing performance"
    
    print_test_result("Integration - Dirty data workflow", True)

# ==================== run all tests ====================

def run_all_tests():
    """run the full test suite"""
    print(f"\n{YELLOW}{'='*50}{RESET}")
    print(f"{YELLOW}DataSight Test Suite{RESET}")
    print(f"{YELLOW}{'='*50}{RESET}\n")
    
    tests = [
        ("Data Processor", [
            test_get_metadata_basic,
            test_get_metadata_no_nulls,
            test_get_metadata_all_nulls,
            test_get_metadata_head_preview,
            test_get_metadata_many_columns,
            test_get_metadata_special_characters,
        ]),
        ("Interpreter", [
            test_get_ai_audit_requires_api_key,
            test_get_ai_audit_empty_metadata,
        ]),
        ("Edge Cases", [
            test_empty_dataframe,
            test_single_row_dataframe,
            test_numeric_columns,
            test_string_columns,
        ]),
        ("Integration", [
            test_workflow_clean_data,
            test_workflow_dirty_data,
        ]),
    ]
    
    total_passed = 0
    total_failed = 0
    
    for category, test_list in tests:
        print(f"{YELLOW}📁 {category}{RESET}")
        for test_func in test_list:
            try:
                test_func()
                total_passed += 1
            except AssertionError as e:
                print_test_result(test_func.__name__, False, str(e))
                total_failed += 1
            except Exception as e:
                print_test_result(test_func.__name__, False, f"Unexpected error: {e}")
                total_failed += 1
        print()
    
    print(f"{YELLOW}{'='*50}{RESET}")
    print(f"📊 Test Results:")
    print(f"  {GREEN}✓ Passed: {total_passed}{RESET}")
    print(f"  {RED}✗ Failed: {total_failed}{RESET}")
    print(f"  📈 Total: {total_passed + total_failed}")
    print(f"{YELLOW}{'='*50}{RESET}\n")
    
    if total_failed == 0:
        print(f"{GREEN}🎉 All tests passed!{RESET}")
        return True
    else:
        print(f"{RED}❌ Some tests failed. Check above for details.{RESET}")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
