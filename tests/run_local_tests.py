import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import test files
import test_scoring_agent
import test_email_utils

def run_test_module(module):
    print(f"\nRunning tests in {module.__name__}...")
    test_funcs = [getattr(module, name) for name in dir(module) if name.startswith("test_") and callable(getattr(module, name))]
    
    passed = 0
    failed = 0
    for func in test_funcs:
        try:
            func()
            print(f"  [OK] {func.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  [FAIL] {func.__name__}: Assertion failed")
            failed += 1
        except Exception as e:
            print(f"  [ERROR] {func.__name__}: {e}")
            failed += 1
            
    return passed, failed

if __name__ == "__main__":
    print("=" * 60)
    print("Zero-Dependency Local Unit Test Suite")
    print("=" * 60)
    
    p1, f1 = run_test_module(test_scoring_agent)
    p2, f2 = run_test_module(test_email_utils)
    
    total_passed = p1 + p2
    total_failed = f1 + f2
    
    print("\n" + "=" * 60)
    print("TEST RUN SUMMARY")
    print("=" * 60)
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    print("=" * 60)
    
    if total_failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)
