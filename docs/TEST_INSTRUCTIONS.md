# SocioSolve — Test Instructions

## Running Tests

### Prerequisites
```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1
```

### Run All Tests
```powershell
python manage.py test
```

**Expected output:**
```
----------------------------------------------------------------------
Ran 27 tests in X.XXXs

OK
```

### Run with Verbosity (see each test name)
```powershell
python manage.py test --verbosity=2
```

### Run Tests for a Specific App
```powershell
python manage.py test accounts
python manage.py test challenges
python manage.py test solutions
python manage.py test collaboration
python manage.py test impact
python manage.py test ai_services
```

### Run a Single Test Class
```powershell
python manage.py test accounts.tests.AuthenticationAndAccountTests
python manage.py test ai_services.tests.AIServicesTests
```

### Run a Single Test Method
```powershell
python manage.py test accounts.tests.AuthenticationAndAccountTests.test_user_login_and_logout
```

---

## Test Coverage Overview

### accounts/tests.py — 5 Tests

| Test | Description |
|------|-------------|
| `test_user_roles` | Verifies all 6 role constants exist on the UserRole enum/choices |
| `test_user_registration` | Registers a new user via the registration form and checks redirect + login |
| `test_user_login` | Logs in with correct credentials, verifies session |
| `test_user_logout` | Logs out and verifies session is cleared |
| `test_anonymous_restrictions` | Checks that anonymous users are redirected from protected URLs (dashboard, profile) |

### challenges/tests.py — 5 Tests

| Test | Description |
|------|-------------|
| `test_challenge_creation` | Authenticated user creates a challenge; checks it appears in the database |
| `test_challenge_permissions` | Owner can access edit/delete; verifies correct HTTP response codes |
| `test_challenge_edit` | Owner edits a challenge and verifies the updated title is saved |
| `test_unauthorized_edit` | Another user cannot edit someone else's challenge (403 or redirect) |
| `test_challenge_moderation` | Admin can view reported challenges; report form works for regular users |

### solutions/tests.py — 3 Tests

| Test | Description |
|------|-------------|
| `test_solution_proposal` | User submits a solution proposal; verifies it is linked to the challenge |
| `test_vote_toggle_and_deduplication` | Upvoting adds a vote; voting again removes it; a second user's vote is counted separately |
| `test_discussion_comment` | User posts a comment on a proposal; comment is saved and associated correctly |

### collaboration/tests.py — 5 Tests

| Test | Description |
|------|-------------|
| `test_team_leadership` | Team creator is automatically assigned the leader role |
| `test_join_request` | A user requests to join a team; membership is in 'pending' status |
| `test_join_approval` | Team leader approves a join request; membership status changes to 'approved' |
| `test_task_permissions` | Only team members can create tasks; non-members get 403 |
| `test_milestone_creation` | Team leader can create a milestone; it is linked to the correct team |

### impact/tests.py — 2 Tests

| Test | Description |
|------|-------------|
| `test_dashboard_metrics` | Dashboard view returns HTTP 200 and context contains all required metric keys |
| `test_verified_vs_estimated` | Verified impact reports are correctly separated from self-reported estimates in the context |

### ai_services/tests.py — 7 Tests

> **All AI tests use `unittest.mock.patch` — no internet connection or API key required.**

| Test | Description |
|------|-------------|
| `test_input_validation_too_short` | Input under 20 characters raises `AIValidationError` |
| `test_missing_api_key` | When `MISTRAL_API_KEY` is not set, `AIServiceUnavailableError` is raised |
| `test_rate_limiting` | After creating enough log entries in the past hour, next request raises `AIRateLimitExceededError` |
| `test_mocked_analyzer` | Mocks the Mistral client; verifies the analyzer returns expected fields |
| `test_mocked_solution_generator` | Mocks the Mistral client; verifies 5 solutions are returned with required fields |
| `test_keyword_fallback` | Without API key, similar challenge finder returns keyword-based results |
| `test_team_matching` | Team matching works entirely locally; verifies skill-matched users appear in results |

---

## Mocking Strategy

AI tests mock at the Mistral client level:

```python
from unittest.mock import patch, MagicMock

@patch('ai_services.services.get_mistral_client')
def test_mocked_analyzer(self, mock_client_factory):
    mock_client = MagicMock()
    mock_client_factory.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.choices[0].message.content = json.dumps({
        "suggested_category": "Environment",
        "root_causes": ["Industrial pollution"],
        "affected_stakeholders": ["Residents"],
        "priority": "High",
        "priority_explanation": "Affects health",
        "missing_information": []
    })
    mock_response.usage.total_tokens = 100
    mock_client.chat.complete.return_value = mock_response
    
    analyzer = AIChallengeAnalyzer()
    result = analyzer.analyze(self.challenge, self.user)
    
    self.assertIn('suggested_category', result)
    self.assertEqual(result['priority'], 'High')
```

This approach:
- Does not require API credits
- Does not require internet access
- Tests the parsing and error-handling logic, not the AI model's response quality
- Is deterministic — tests always return the same mock data

---

## System Checks

Run Django's built-in system checks:

```powershell
python manage.py check
```

Expected: `System check identified no issues (0 silenced).`

Check migrations are up to date:

```powershell
python manage.py migrate --check
```

Expected: No output (all migrations applied).

---

## Test Database

Django creates a separate test database for each test run and destroys it afterward. The production `db.sqlite3` is never modified by tests.

To keep the test database between runs (for debugging):

```powershell
python manage.py test --keepdb
```

---

## Common Issues

### Issue: Tests fail with `ImproperlyConfigured`
**Cause:** Missing environment variable
**Fix:** Make sure `.env` file exists with at least `SECRET_KEY` set

### Issue: AI tests fail with actual API calls
**Cause:** Mock patch path is incorrect
**Fix:** The patch path must match where the symbol is used, not where it is defined:
```python
# Correct:
@patch('ai_services.services.get_mistral_client')
# NOT: @patch('mistralai.client.Mistral')
```

### Issue: `OperationalError: no such table`
**Cause:** Migrations not applied
**Fix:** `python manage.py migrate`

### Issue: Vote deduplication test fails
**Cause:** `unique_together` not applied
**Fix:** `python manage.py migrate solutions`
