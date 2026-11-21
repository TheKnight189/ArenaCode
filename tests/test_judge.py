"""
Unit and integration tests for CodeArena Judge system.
Verifies:
- Code execution in Sandbox / Native Jail
- Syntax and compile error handling
- AST code similarity calculation (Winnowing / AST analysis)
- Academic integrity: Hidden test case masking ('[Dữ liệu ẩn trong kỳ thi]' and '[Kết quả ẩn trong kỳ thi]')
"""

import os
import sys
import unittest
from unittest.mock import patch

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.judge import execute_code, evaluate_submission, compute_similarity, detect_off_topic, PROBLEM_HARNESS


class TestCodeExecution(unittest.TestCase):
    """Tests for raw code execution via execute_code."""

    def test_execute_valid_code(self):
        """Verify normal Python code executes successfully."""
        code = "print(100 + 200)"
        result = execute_code(code, language="python")
        self.assertEqual(result["status"], "Success")
        self.assertEqual(result["exit_code"], 0)
        self.assertIn("300", result["stdout"])

    def test_execute_with_stdin(self):
        """Verify Python code correctly reads from stdin."""
        code = "name = input()\nprint(f'Hello, {name}!')"
        result = execute_code(code, language="python", stdin="CodeArena")
        self.assertEqual(result["status"], "Success")
        self.assertEqual(result["exit_code"], 0)
        self.assertIn("Hello, CodeArena!", result["stdout"])

    def test_execute_runtime_error(self):
        """Verify Python runtime error (e.g. division by zero) is handled properly."""
        code = "x = 10 / 0"
        result = execute_code(code, language="python")
        self.assertEqual(result["status"], "Runtime Error")
        self.assertNotEqual(result["exit_code"], 0)
        self.assertIn("ZeroDivisionError", result["stderr"])

    def test_execute_multiline_logic(self):
        """Verify complex multi-line functions and data structures."""
        code = """
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)

print(fib(7))
"""
        result = execute_code(code, language="python")
        self.assertEqual(result["status"], "Success")
        self.assertEqual(result["exit_code"], 0)
        self.assertIn("13", result["stdout"])


class TestSyntaxCompileError(unittest.TestCase):
    """Tests for syntax error and compile error handling."""

    def test_syntax_error_in_execute_code(self):
        """Verify execute_code catches Python syntax errors as Compile Error."""
        code = "def invalid_syntax(:"
        result = execute_code(code, language="python")
        self.assertEqual(result["status"], "Compile Error")
        self.assertEqual(result["exit_code"], 1)
        self.assertIn("Compile Error", result["stderr"])
        self.assertIn("SyntaxError", result["stderr"])

    def test_syntax_error_in_evaluate_submission(self):
        """Verify evaluate_submission flags syntax error submission with status 'Compile Error'."""
        code = "def two_sum(nums, target\n    return []"
        result = evaluate_submission("CA-101", code, language="python")
        self.assertEqual(result["status"], "Compile Error")
        self.assertIn("Compile Error", result["stderr"])


class TestASTSimilarity(unittest.TestCase):
    """Tests for AST similarity computation and plagiarism detection."""

    def test_identical_code_similarity(self):
        """Identical code snippets must yield 100% similarity."""
        code1 = "def solve(a, b):\n    return a + b"
        code2 = "def solve(a, b):\n    return a + b"
        sim = compute_similarity(code1, code2)
        self.assertEqual(sim, 100.0)

    def test_empty_code_similarity(self):
        """Empty code must yield 0% similarity."""
        self.assertEqual(compute_similarity("", "print(1)"), 0.0)
        self.assertEqual(compute_similarity("print(1)", ""), 0.0)
        self.assertEqual(compute_similarity("", ""), 0.0)

    def test_renamed_variables_high_similarity(self):
        """Code with renamed variables should retain high AST/Token similarity."""
        code1 = "def sum_two(x, y):\n    total = x + y\n    return total"
        code2 = "def add_numbers(num1, num2):\n    res = num1 + num2\n    return res"
        sim = compute_similarity(code1, code2)
        self.assertGreaterEqual(sim, 60.0)

    def test_different_code_lower_similarity(self):
        """Functionally and structurally distinct codes should yield lower similarity than identical codes."""
        code1 = "x = [1, 2, 3]\nfor i in x:\n    print(i)"
        code2 = "class DatabaseConnection:\n    def connect(self):\n        pass"
        sim = compute_similarity(code1, code2)
        self.assertLess(sim, 60.0)


class TestHiddenTestCaseMasking(unittest.TestCase):
    """
    Tests ensuring academic integrity:
    Hidden test cases must have raw inputs and expected outputs masked as:
    - input: '[Dữ liệu ẩn trong kỳ thi]'
    - expected: '[Kết quả ẩn trong kỳ thi]'
    While public test cases retain their raw values.
    """

    MASKED_INPUT = "[Dữ liệu ẩn trong kỳ thi]"
    MASKED_EXPECTED = "[Kết quả ẩn trong kỳ thi]"

    def test_hidden_masking_ca101(self):
        """Test CA-101 submission returns masked test_details for hidden test cases."""
        code = """
def two_sum(nums, target):
    lookup = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in lookup:
            return [lookup[complement], i]
        lookup[num] = i
    return []
"""
        result = evaluate_submission("CA-101", code, language="python")
        test_details = result.get("test_details", [])
        self.assertGreater(len(test_details), 0, "test_details should not be empty")

        hidden_cases = [t for t in test_details if t.get("hidden")]
        visible_cases = [t for t in test_details if not t.get("hidden")]

        self.assertGreater(len(hidden_cases), 0, "CA-101 must have hidden test cases")
        self.assertGreater(len(visible_cases), 0, "CA-101 must have visible test cases")

        # Verify hidden cases are strictly masked
        for t in hidden_cases:
            self.assertEqual(
                t["input"],
                self.MASKED_INPUT,
                f"Hidden test case #{t['id']} input was not masked: {t['input']}"
            )
            self.assertEqual(
                t["expected"],
                self.MASKED_EXPECTED,
                f"Hidden test case #{t['id']} expected output was not masked: {t['expected']}"
            )

        # Verify visible cases are NOT masked
        for t in visible_cases:
            self.assertNotEqual(
                t["input"],
                self.MASKED_INPUT,
                f"Visible test case #{t['id']} input should not be masked"
            )
            self.assertNotEqual(
                t["expected"],
                self.MASKED_EXPECTED,
                f"Visible test case #{t['id']} expected output should not be masked"
            )

    def test_hidden_masking_ca102(self):
        """Test CA-102 (Reverse String) also masks hidden cases appropriately."""
        code = "def reverse_string(s):\n    return s[::-1]"
        result = evaluate_submission("CA-102", code, language="python")
        test_details = result.get("test_details", [])

        hidden_cases = [t for t in test_details if t.get("hidden")]
        visible_cases = [t for t in test_details if not t.get("hidden")]

        self.assertGreater(len(hidden_cases), 0)
        self.assertGreater(len(visible_cases), 0)

        for t in hidden_cases:
            self.assertEqual(t["input"], self.MASKED_INPUT)
            self.assertEqual(t["expected"], self.MASKED_EXPECTED)

        for t in visible_cases:
            self.assertNotEqual(t["input"], self.MASKED_INPUT)
            self.assertNotEqual(t["expected"], self.MASKED_EXPECTED)

    def test_hidden_masking_custom_database_problem(self):
        """Verify masking logic when problem is resolved from database / custom problem dict."""
        mock_problem = {
            "id": "CUSTOM-999",
            "title": "Custom Test Problem",
            "testCases": [
                {"input": "public_in_1", "expected": "public_out_1", "hidden": False},
                {"input": "hidden_in_2", "expected": "hidden_out_2", "hidden": True},
                {"input": "hidden_in_3", "expected": "hidden_out_3", "hidden": True},
            ]
        }

        with patch("backend.database.get_problem_by_id_db", return_value=mock_problem):
            code = "print('dummy solution')"
            result = evaluate_submission("CUSTOM-999", code, language="python")
            test_details = result.get("test_details", [])

            self.assertEqual(len(test_details), 3)

            # Test 1: Public
            self.assertFalse(test_details[0]["hidden"])
            self.assertEqual(test_details[0]["input"], "public_in_1")
            self.assertEqual(test_details[0]["expected"], "public_out_1")

            # Test 2: Hidden
            self.assertTrue(test_details[1]["hidden"])
            self.assertEqual(test_details[1]["input"], self.MASKED_INPUT)
            self.assertEqual(test_details[1]["expected"], self.MASKED_EXPECTED)

            # Test 3: Hidden
            self.assertTrue(test_details[2]["hidden"])
            self.assertEqual(test_details[2]["input"], self.MASKED_INPUT)
            self.assertEqual(test_details[2]["expected"], self.MASKED_EXPECTED)


class TestOffTopicDetection(unittest.TestCase):
    """Tests for AI off-topic and wrong problem detection."""

    def test_hardcoded_output(self):
        result = detect_off_topic("print(42)", "CA-101", "Two Sum", "Find two numbers", [], "twoSum")
        self.assertTrue(result["is_off_topic"])
        self.assertGreaterEqual(result["confidence"], 0.9)
        self.assertIn("chỉ in kết quả cứng", result["reason"])

    def test_wrong_function_name(self):
        code = (
            "def bubbleSort(arr):\n"
            "    for i in range(len(arr)):\n"
            "        for j in range(len(arr)-1):\n"
            "            if arr[j] > arr[j+1]:\n"
            "                arr[j], arr[j+1] = arr[j+1], arr[j]\n"
            "    return arr"
        )
        result = detect_off_topic(
            code, "CA-101", "Two Sum", "Find two numbers that add up to target", ["bubbleSort"], "twoSum"
        )
        self.assertTrue(result["is_off_topic"])
        self.assertGreaterEqual(result["confidence"], 0.7)
        self.assertLessEqual(result["confidence"], 0.85)

    def test_correct_code(self):
        code = (
            "def twoSum(nums, target):\n"
            "    d = {}\n"
            "    for i, x in enumerate(nums):\n"
            "        if target - x in d:\n"
            "            return [d[target-x], i]\n"
            "        d[x] = i"
        )
        result = detect_off_topic(code, "CA-101", "Two Sum", "Find two numbers", ["twoSum"], "twoSum")
        self.assertFalse(result["is_off_topic"])
        self.assertLess(result["confidence"], 0.5)

    def test_empty_or_trivial_code(self):
        result = detect_off_topic("x = 1\ny = 2", "CA-101", "Two Sum", "Find two numbers", [], "twoSum")
        self.assertTrue(result["is_off_topic"])
        self.assertGreaterEqual(result["confidence"], 0.9)
        self.assertIn("quá ngắn", result["reason"])

    def test_evaluate_submission_warning_annotated(self):
        code = "print(42)"
        res = evaluate_submission("CA-101", code, language="python")
        self.assertIn("[Cảnh báo lệch đề]", res["ai_rubric"])


if __name__ == "__main__":
    unittest.main()
