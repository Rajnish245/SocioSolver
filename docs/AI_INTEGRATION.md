# SocioSolve — AI Integration Guide

## Overview

SocioSolve integrates with the **Mistral AI API** to provide four AI-powered features. All AI logic is encapsulated in `ai_services/services.py`. Views never call the Mistral SDK directly.

---

## Configuration

### 1. Get a Mistral API Key
- Sign up at https://console.mistral.ai/
- Create an API key in your account settings
- Add it to your `.env` file:

```
MISTRAL_API_KEY=your-key-here
```

### 2. Available Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MISTRAL_API_KEY` | *(empty)* | Your Mistral API key |
| `MISTRAL_MODEL` | `mistral-small-latest` | Chat model for analysis and generation |
| `MISTRAL_EMBEDDING_MODEL` | `mistral-embed` | Embedding model for semantic search |
| `MAX_AI_REQUESTS_PER_HOUR` | `15` | Max AI requests per user per hour |

### 3. Without an API Key

The application runs fully without an API key. When AI features are attempted:
- A clear "AI features require configuration" message is shown
- Similar challenge finder falls back to database keyword search
- No fake or hallucinated results are ever shown
- All non-AI features work normally

---

## AI Features

### A. AI Challenge Analyzer

**URL:** `POST /ai/analyze/<challenge_id>/`

**What it does:**
Sends the challenge title, description, location, and category to Mistral. Returns a structured JSON analysis.

**Output fields:**
```json
{
  "suggested_category": "Water Conservation",
  "root_causes": ["Aging infrastructure", "Lack of public awareness"],
  "affected_stakeholders": ["Residents", "Municipal Authority", "School students"],
  "priority": "High",
  "priority_explanation": "Affects 2000+ daily users and poses health risks",
  "missing_information": ["Exact daily wastage volume", "Municipal maintenance schedule"]
}
```

**Important:** The AI priority is a recommendation, not a verified fact. The UI displays:
> "AI-generated suggestions may be inaccurate and require human review."

**Caching:** Results are saved in `Challenge.ai_analysis_cache` (JSONField). Subsequent requests serve from the database — no repeat API call.

---

### B. AI Solution Generator

**URL:** `POST /ai/solutions/<challenge_id>/`

**What it does:**
Generates five practical solution roadmaps for a challenge. Each solution includes implementation steps, required resources, risks, potential collaborators, and impact measurement ideas.

**Output structure:**
```json
{
  "solutions": [
    {
      "title": "Smart Leak Detection System",
      "description": "...",
      "implementation_steps": ["Step 1", "Step 2"],
      "required_skills": ["IoT engineering", "Data analysis"],
      "required_resources": ["Sensors", "Cloud platform"],
      "potential_risks": ["High initial cost"],
      "potential_collaborators": ["Water board", "Tech companies"],
      "impact_measurement": ["Monthly water savings in liters"]
    }
  ]
}
```

**Caching:** Results are saved in `Challenge.ai_solutions_cache`. Subsequent views serve from the database.

---

### C. Similar Challenge Finder

**URL:** `GET /ai/similar/<challenge_id>/`

**Semantic search (when API key is configured):**
1. Generates an embedding vector for the challenge description using `mistral-embed`
2. Stores the vector on the `Challenge.ai_embedding` field
3. Computes cosine similarity against all other challenge embeddings
4. Returns the top 5 most similar challenges

**Keyword fallback (when API key is not configured):**
- Extracts significant words from the title and description
- Filters challenges using Django ORM `Q(title__icontains=...)` queries
- The UI clearly states: "Showing keyword-based results (semantic search not configured)"

**The UI never claims semantic search is active when it is not.**

---

### D. Smart Team Matcher

**URL:** `GET /ai/team-match/<challenge_id>/`

**What it does:**
Scores and ranks all registered users as potential collaborators based on:
- Skill overlap with challenge keywords
- Interest alignment
- Role appropriateness (students, universities, NGOs, etc.)

**Each recommendation includes:**
- Match score (0–100)
- Explanation of why this person was recommended
- User's role, skills, and interests

**Important safeguards:**
- Users are NOT automatically enrolled in teams
- The team leader must manually invite or approve each member
- Match scores are algorithmic, not verified endorsements

---

## Rate Limiting

```python
# ai_services/services.py
def check_user_rate_limit(user):
    one_hour_ago = timezone.now() - timedelta(hours=1)
    recent_count = AIAnalysisLog.objects.filter(
        user=user,
        created_at__gte=one_hour_ago,
    ).count()
    if recent_count >= settings.AI_RATE_LIMIT_PER_USER_PER_HOUR:
        raise AIRateLimitExceededError(
            f"You have reached the limit of {settings.AI_RATE_LIMIT_PER_USER_PER_HOUR} AI requests per hour."
        )
```

Rate limit is per user, per hour. Default: 15 requests/hour.

---

## Error Handling

All AI service methods raise typed exceptions:

| Exception | When raised |
|-----------|-------------|
| `AIServiceUnavailableError` | No API key, network error, timeout, service down |
| `AIRateLimitExceededError` | User exceeded hourly quota |
| `AIValidationError` | Input too short, too long, or empty |

Views catch these exceptions and display user-friendly Django messages. No raw exception tracebacks are shown to end users.

---

## Input Validation

Before any API call:
```python
def validate_challenge_input(title, description):
    if not title or not description:
        raise AIValidationError("Title and description are required.")
    if len(description) < 20:
        raise AIValidationError("Description is too short for meaningful analysis.")
    if len(description) > 5000:
        raise AIValidationError("Description is too long. Please limit to 5000 characters.")
```

---

## Privacy Considerations

- Only the challenge title, description, location, category, and affected community are sent to Mistral
- User names and personal details are NOT sent to Mistral
- The team matching feature is entirely local — no user data is sent to any external service
- AI analysis logs store only token counts, feature name, and success status — not the full response content

---

## Monitoring & Logging

Every AI API call creates an `AIAnalysisLog` record:

```python
AIAnalysisLog.objects.create(
    user=request.user,
    challenge=challenge,
    feature_used='analyze_challenge',
    input_summary=f"Challenge: {challenge.title[:100]}",
    tokens_used=response.usage.total_tokens,
    success=True
)
```

View all logs in Django Admin → AI Services → AI Analysis Logs.

---

## Ethical AI Disclaimer

All AI output pages display:

> ⚠️ **AI Disclaimer:** These suggestions are generated by AI and may be inaccurate, incomplete, or inappropriate for your specific context. Always verify AI-generated recommendations with domain experts and local stakeholders before taking action. AI cannot replace community engagement and professional expertise.

This disclaimer is implemented in:
- `templates/ai_services/solutions_view.html`
- `templates/ai_services/similar_challenges.html`
- `templates/ai_services/team_matching.html`
- `templates/challenges/challenge_detail.html` (AI analysis section)

---

## Mistral SDK Version

The project uses the official Mistral Python SDK v3.x (client pattern):

```python
from mistralai.client import Mistral
from mistralai.client.models import ResponseFormat

client = Mistral(api_key=settings.MISTRAL_API_KEY)

response = client.chat.complete(
    model=settings.MISTRAL_MODEL,
    messages=[...],
    response_format=ResponseFormat(type='json_object')
)
```

Key differences from the OpenAI SDK:
- Chat: `client.chat.complete(...)` not `client.chat.completions.create(...)`
- Embeddings: `client.embeddings.create(model=..., inputs=[text])` — uses `inputs` (list) not `input`
- Response format: `ResponseFormat(type='json_object')` — Pydantic model, not a dict

---

## Cost Estimation

| Feature | Typical Tokens | Model | Estimated Cost |
|---------|---------------|-------|----------------|
| Challenge Analyzer | ~800 in + ~400 out | mistral-small-latest | ~\$0.0003 |
| Solution Generator | ~800 in + ~1200 out | mistral-small-latest | ~\$0.0005 |
| Embedding (similar) | ~200 in | mistral-embed | ~\$0.00002 |
| Team Matching | Local only | — | \$0.00 |

*Prices are approximate and subject to change. Check https://mistral.ai/pricing for current rates.*
