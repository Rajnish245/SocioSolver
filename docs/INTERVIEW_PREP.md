# SocioSolve — Technical Interview Preparation Guide

This document prepares you to confidently explain the SocioSolve project in a technical interview, viva, or project presentation.

---

## Elevator Pitch (30 seconds)

> "SocioSolve is a collaborative web platform built with Django and OpenAI. It lets citizens, students, NGOs, and companies report societal challenges — like water waste or pollution — and work together on solutions. The AI analyzes each challenge, generates solution roadmaps, finds similar challenges using semantic search, and recommends collaborators. Everything is backed by real database data, with graceful degradation when external services are unavailable."

---

## Architecture Questions

### Q: Explain the overall architecture of SocioSolve.

**Answer:**
SocioSolve follows Django's MTV pattern — Models, Templates, Views. There is no separate frontend framework; everything is server-rendered HTML using Django templates and Bootstrap 5.

The project is organized into seven Django applications:
- `accounts` — custom user model and authentication
- `challenges` — the core challenge management
- `solutions` — proposals, voting, comments
- `collaboration` — teams, tasks, milestones
- `partnerships` — organization profiles and sponsorships
- `impact` — impact dashboard backed by live database queries
- `ai_services` — a dedicated service layer for all OpenAI calls

The root URL dispatcher in `sociosolve_core/urls.py` routes requests to each app's URL configuration.

### Q: Why did you use Django instead of a separate frontend framework like React?

**Answer:**
The requirement specified server-rendered templates to avoid the complexity of a separate build pipeline. Django's template system with Bootstrap 5 is sufficient for a university project. The tradeoff is less interactivity, but the upside is simpler deployment, fewer moving parts, and better security (no token management in the browser). I added selective JavaScript (AJAX upvoting, Chart.js dashboards) where interactivity genuinely improves the experience.

---

## Database Questions

### Q: Why did you use a custom User model?

**Answer:**
Django strongly recommends creating a custom user model at the start of a project, before running any migrations. If you try to swap the user model after running migrations, you need complex data migrations. My custom `User` model extends `AbstractUser` with fields for `role`, `bio`, `skills`, `interests`, `organization`, and `avatar`. Setting `AUTH_USER_MODEL = 'accounts.User'` in `settings.py` makes Django use it everywhere.

### Q: How do you prevent a user from voting on the same proposal twice?

**Answer:**
Two layers of protection:
1. The `SolutionVote` model has `unique_together = ('proposal', 'user')` — the database itself rejects duplicate votes with an IntegrityError.
2. The vote view uses `get_or_create` wrapped in a `try/except IntegrityError` to handle the race condition gracefully.

Never rely on application-level checks alone for data integrity constraints — enforce them at the database level.

### Q: How do you distinguish verified impact from self-reported estimates?

**Answer:**
The `ImpactReport` model has an `is_verified` boolean field and a `verified_by_org` field. When creating a report, team leaders mark it as self-reported. Administrators can mark it as verified after reviewing supporting documentation. The impact dashboard and report detail pages display different badges: a green "Verified" badge vs an amber "Self-Reported" badge. Statistics in the dashboard clearly distinguish between the two categories.

---

## AI Integration Questions

### Q: How is the OpenAI API integrated into SocioSolve?

**Answer:**
All AI logic lives in `ai_services/services.py`. Views never call the OpenAI SDK directly — they call service methods. This separation makes the AI testable (by mocking the service layer) and keeps views thin.

The service module has four main classes:
- `AIChallengeAnalyzer` — sends challenge details to GPT-4o-mini and returns a structured JSON analysis
- `AISolutionGenerator` — generates five practical solution roadmaps
- `AISimilarChallengeFinder` — uses embeddings for semantic search, falls back to keyword search
- `AISmartTeamMatcher` — local algorithm that scores users by skill/interest overlap

### Q: How do you handle AI API failures?

**Answer:**
The service layer defines three custom exceptions: `AIServiceUnavailableError`, `AIRateLimitExceededError`, and `AIValidationError`. Every API call is wrapped in a try/except that catches these plus generic network errors. Views catch the exceptions and display Django messages — the user sees a friendly error, not a traceback.

If the API key is missing, the app still runs: similar challenge finder uses keyword search, and all non-AI features work normally.

### Q: How do you prevent abuse of AI features?

**Answer:**
Multiple layers:
1. **Authentication required** — all AI endpoints have `@login_required`
2. **Input validation** — `validate_challenge_input()` checks for empty, too-short (< 20 chars), or too-long (> 5000 chars) input
3. **Rate limiting** — `check_user_rate_limit()` counts successful `AIAnalysisLog` entries in the past hour; default limit is 20
4. **Caching** — analysis results are stored on the Challenge model; re-viewing doesn't trigger another API call
5. **Privacy** — user personal data (names, emails) is never sent to OpenAI

### Q: What is semantic search and how does SocioSolve implement it?

**Answer:**
Semantic search finds documents based on meaning rather than exact keyword matching. OpenAI's embedding model converts text into a high-dimensional vector (a list of numbers) where semantically similar texts have vectors that point in similar directions.

In SocioSolve:
1. When a challenge is analyzed, its description is converted to an embedding vector
2. The vector is stored as a comma-separated string in `Challenge.ai_embedding`
3. When finding similar challenges, the target challenge's embedding is compared to all others using cosine similarity
4. `cosine_similarity(a, b) = dot(a, b) / (|a| × |b|)` — returns 1 for identical, 0 for unrelated
5. The top 5 results are returned

The fallback uses Django Q objects to search for keyword matches in title and description fields.

---

## Security Questions

### Q: How do you handle permissions?

**Answer:**
Three layers:
1. **Decorators** — `@login_required`, `@role_required('university')` — applied to view functions
2. **Object-level checks** — inside views, `if request.user != challenge.creator and not request.user.is_staff: return HttpResponseForbidden()`
3. **Template conditionals** — cosmetic only (hide edit buttons from non-owners), but the actual enforcement is in the view

Template conditionals alone are insufficient — a user could craft a POST request directly to the edit URL.

### Q: How do you protect the OpenAI API key?

**Answer:**
- Stored in `.env` (local environment file)
- `.env` is in `.gitignore` and never committed
- `.env.example` provides a template with placeholder values
- The key is loaded via `python-dotenv` in `settings.py`: `os.environ.get('OPENAI_API_KEY', '')`
- Never exposed in templates, JavaScript, or HTTP responses
- Never appears in error messages shown to users

### Q: How does CSRF protection work in Django?

**Answer:**
Django's CSRF middleware generates a secret token per session. Every POST form must include `{% csrf_token %}` in the template, which renders a hidden input field with the token. The middleware verifies the token on every POST request. If missing or invalid, the request is rejected with a 403 Forbidden. This prevents cross-site request forgery attacks where malicious sites try to submit forms on behalf of authenticated users.

---

## Collaboration Features Questions

### Q: How do teams work in SocioSolve?

**Answer:**
- Any authenticated user can create a `ProjectTeam` linked to a challenge
- The creator is automatically assigned the 'leader' role via a `TeamMembership` record
- Other users submit a join request (membership with status='pending', optional message)
- The team leader reviews requests and approves or rejects them
- Approved members can create tasks and view the Kanban board
- Tasks have status: To-Do, In Progress, Completed, Blocked
- Milestones track major goals with target dates and completion status

### Q: How does upvoting work?

**Answer:**
`SolutionVote` stores (proposal, user, is_upvote). The vote view:
1. Tries to get an existing vote with `get_or_create`
2. If the vote already exists, it was created=False, so we delete it (toggle off)
3. If it was just created, it stays (toggle on)
4. The proposal's `upvotes` count is recalculated using an aggregate `Count` query

This is wrapped in a database transaction to handle concurrent votes safely.

---

## Testing Questions

### Q: How did you test AI features without making real API calls?

**Answer:**
Using `unittest.mock.patch` to replace the OpenAI client with a `MagicMock`. The patch path targets the symbol as imported in the services module: `@patch('ai_services.services.OpenAI')`. The mock returns a predetermined response object. This tests parsing logic, error handling, and rate limiting without internet access or API credits.

### Q: What is the test database?

**Answer:**
When you run `python manage.py test`, Django creates a temporary database prefixed with `test_` (e.g., `test_db.sqlite3`), runs all tests against it, then destroys it. Your production database is never touched. Each test class gets a fresh database state using transactions or `TestCase.setUp()`.

---

## Limitations and Honest Answers

### Q: What are the limitations of this project?

**Answer:**
1. **No real-time features** — there's no WebSocket or live update; users must refresh to see new comments
2. **SQLite in production** — SQLite is fine for development but doesn't support concurrent writes well; production needs PostgreSQL
3. **No email verification** — the registration flow doesn't send verification emails
4. **AI hallucination** — the AI can generate plausible-sounding but incorrect information; the ethical disclaimer is important
5. **Semantic search at scale** — storing embeddings as comma-separated strings is fine for a prototype, but a production system should use pgvector or a dedicated vector database
6. **No background task queue** — long-running AI tasks run synchronously in the request-response cycle; production would benefit from Celery + Redis

### Q: What would you improve if you had more time?

**Answer:**
- Real-time notifications with Django Channels (WebSockets)
- Email notifications for team updates, join request approvals, etc.
- PostgreSQL with pgvector for production-grade semantic search
- Celery task queue for async AI processing with progress indicators
- OAuth2 social login (Google, LinkedIn) for easier onboarding
- Export challenge reports to PDF
- More granular role permissions using Django Guardian for object-level permissions
- A REST API layer (Django REST Framework) to enable mobile apps

---

## Key Numbers

| Metric | Value |
|--------|-------|
| Django apps | 7 |
| Database models | 16 |
| URL patterns | ~40 |
| HTML templates | 30+ |
| Automated tests | 27 |
| Test pass rate | 100% |
| AI features | 4 |
| Demo users | 6 (all roles) |
| Demo challenges | 3 |
| Lines of Python | ~3000+ |
