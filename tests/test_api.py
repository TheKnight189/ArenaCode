"""
Integration and API tests for CodeArena REST API using FastAPI TestClient.
Verifies:
- /api/health (System status, database health, sandbox engine)
- /api/auth/login (Authentication, valid login, invalid credentials, validation)
- /api/problems (Problem catalog, problem details, 404 handling)
- /api/submissions (Submission retrieval with limit and offset pagination, validation boundaries)
"""

import os
import sys
import unittest

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from backend.main import app


class TestHealthAPI(unittest.TestCase):
    """Tests for GET /api/health."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health_endpoint_success(self):
        """Verify health check returns status 200 with operational metrics."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data.get("status"), "healthy")
        self.assertIn("service", data)
        self.assertIn("database", data)
        self.assertIn("sandbox_engine", data)
        self.assertTrue(data.get("db_details", {}).get("connected", False))


class TestAuthAPI(unittest.TestCase):
    """Tests for POST /api/auth/login."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_login_success(self):
        """Verify valid admin login returns 200, auth token, and user info."""
        payload = {
            "email": "admin@haui.edu.vn",
            "password": "admin"
        }
        response = self.client.post("/api/auth/login", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("token", data)
        self.assertIn("user", data)
        self.assertEqual(data["user"]["email"], "admin@haui.edu.vn")
        self.assertEqual(data["user"]["role"], "Admin")

    def test_login_invalid_password(self):
        """Verify login fails with 401 when password is incorrect."""
        payload = {
            "email": "admin@haui.edu.vn",
            "password": "incorrect_password_123"
        }
        response = self.client.post("/api/auth/login", json=payload)
        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.json())

    def test_login_nonexistent_email(self):
        """Verify login fails with 401 when email does not exist."""
        payload = {
            "email": "nonexistent.user@haui.edu.vn",
            "password": "some_password"
        }
        response = self.client.post("/api/auth/login", json=payload)
        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.json())

    def test_login_validation_error(self):
        """Verify login returns 422 when body is malformed or missing required fields."""
        response = self.client.post("/api/auth/login", json={"email": "only_email@haui.edu.vn"})
        self.assertEqual(response.status_code, 422)


class TestProblemsAPI(unittest.TestCase):
    """Tests for GET /api/problems and GET /api/problems/{problem_id}."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_get_problems_list(self):
        """Verify GET /api/problems returns catalog of available problems."""
        response = self.client.get("/api/problems")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsInstance(data, dict)
        self.assertGreater(len(data), 0, "Problem catalog should not be empty")
        self.assertIn("CA-101", data)

        sample_problem = data["CA-101"]
        self.assertEqual(sample_problem["id"], "CA-101")
        self.assertIn("name", sample_problem)
        self.assertIn("diff", sample_problem)

    def test_get_problem_by_id_success(self):
        """Verify GET /api/problems/{id} returns full problem details."""
        response = self.client.get("/api/problems/CA-101")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["id"], "CA-101")
        self.assertIn("name", data)
        self.assertIn("desc", data)

    def test_get_problem_by_id_not_found(self):
        """Verify GET /api/problems/{id} returns 404 for nonexistent problem."""
        response = self.client.get("/api/problems/UNKNOWN_PROBLEM_99999")
        self.assertEqual(response.status_code, 404)


class TestSubmissionsPaginationAPI(unittest.TestCase):
    """Tests for GET /api/submissions with pagination (limit and offset)."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_get_submissions_unpaginated(self):
        """Verify GET /api/submissions without query params returns full list."""
        response = self.client.get("/api/submissions")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsInstance(data, list)

    def test_get_submissions_limit(self):
        """Verify limit parameter restricts number of returned submissions."""
        response = self.client.get("/api/submissions?limit=1")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsInstance(data, list)
        self.assertLessEqual(len(data), 1)

    def test_get_submissions_limit_and_offset(self):
        """Verify limit and offset slice the submission dataset accurately."""
        all_resp = self.client.get("/api/submissions")
        self.assertEqual(all_resp.status_code, 200)
        all_subs = all_resp.json()

        if len(all_subs) >= 2:
            # First item via limit=1, offset=0
            resp_p1 = self.client.get("/api/submissions?limit=1&offset=0")
            self.assertEqual(resp_p1.status_code, 200)
            p1 = resp_p1.json()
            self.assertEqual(len(p1), 1)
            self.assertEqual(p1[0]["id"], all_subs[0]["id"])

            # Second item via limit=1, offset=1
            resp_p2 = self.client.get("/api/submissions?limit=1&offset=1")
            self.assertEqual(resp_p2.status_code, 200)
            p2 = resp_p2.json()
            self.assertEqual(len(p2), 1)
            self.assertEqual(p2[0]["id"], all_subs[1]["id"])
        else:
            # If dataset is small, offset past length should yield empty list
            resp_offset = self.client.get("/api/submissions?limit=10&offset=1000")
            self.assertEqual(resp_offset.status_code, 200)
            self.assertEqual(len(resp_offset.json()), 0)

    def test_pagination_boundary_zero_limit(self):
        """Verify limit=0 is rejected with 422 Unprocessable Entity (ge=1)."""
        response = self.client.get("/api/submissions?limit=0")
        self.assertEqual(response.status_code, 422)

    def test_pagination_boundary_exceeded_limit(self):
        """Verify limit > 500 is rejected with 422 Unprocessable Entity (le=500)."""
        response = self.client.get("/api/submissions?limit=501")
        self.assertEqual(response.status_code, 422)

    def test_pagination_boundary_negative_offset(self):
        """Verify offset < 0 is rejected with 422 Unprocessable Entity (ge=0)."""
        response = self.client.get("/api/submissions?offset=-1")
        self.assertEqual(response.status_code, 422)

    def test_submissions_filter_with_pagination(self):
        """Verify pagination works when combined with filters (e.g. problem_id)."""
        response = self.client.get("/api/submissions?problem_id=CA-101&limit=2&offset=0")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertLessEqual(len(data), 2)
        for sub in data:
            self.assertEqual(sub["problem_id"], "CA-101")


class TestContestTimerAPI(unittest.TestCase):
    """Tests for Contests and Multi-day/custom duration Countdown API."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_get_contests_list(self):
        """Verify GET /api/contests returns active contests with duration and start_time."""
        response = self.client.get("/api/contests")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
        first_contest = data[0]
        self.assertIn("duration_minutes", first_contest)
        self.assertIn("start_time", first_contest)

    def test_create_multiday_contest(self):
        """Verify creating a contest with multi-day duration (e.g. 3 days = 4320 mins) succeeds."""
        payload = {
            "title": "HaUI Hackathon 2026 - 3 Ngày Đêm Lập trình",
            "desc": "Kỳ thi kéo dài 3 ngày đêm cho sinh viên K16",
            "creator": "TS. Nguyễn Thị Hoa Huệ",
            "duration_minutes": 4320,  # 3 days * 24 hours * 60 minutes
            "rule": "Luật ICPC (Penalty 20 phút/lần nộp sai)",
            "grader_mode": "hybrid",
            "problems": ["CA-101", "CA-102"]
        }
        response = self.client.post("/api/contests", json=payload)
        self.assertEqual(response.status_code, 201)
        created = response.json()
        self.assertEqual(created["duration_minutes"], 4320)
        self.assertEqual(created["title"], payload["title"])
        self.assertIn("id", created)


if __name__ == "__main__":
    unittest.main()
