# SocioSolve — Entity-Relationship Diagram

This document shows all database models and their relationships using a Mermaid ER diagram.

---

## Full ER Diagram

```mermaid
erDiagram
    USER {
        int id PK
        string username
        string email
        string first_name
        string last_name
        string role
        string bio
        string skills
        string interests
        string organization
        image avatar
        datetime date_joined
        bool is_active
    }

    CHALLENGE_CATEGORY {
        int id PK
        string name
        string slug
        string description
        string icon
        int order
    }

    CHALLENGE {
        int id PK
        string title
        string description
        string location
        string affected_community
        string status
        image problem_image
        json ai_analysis_cache
        json ai_solutions_cache
        vector ai_embedding
        datetime created_at
        datetime updated_at
    }

    CHALLENGE_REPORT {
        int id PK
        string reason
        string details
        bool is_resolved
        datetime created_at
    }

    CHALLENGE_BOOKMARK {
        int id PK
        datetime created_at
    }

    SOLUTION_PROPOSAL {
        int id PK
        string title
        string description
        string implementation_steps
        string resources_needed
        string expected_impact
        int upvotes
        datetime created_at
        datetime updated_at
    }

    SOLUTION_VOTE {
        int id PK
        bool is_upvote
        datetime created_at
    }

    DISCUSSION_COMMENT {
        int id PK
        string content
        datetime created_at
        datetime updated_at
    }

    PROJECT_TEAM {
        int id PK
        string name
        string description
        string status
        datetime created_at
    }

    TEAM_MEMBERSHIP {
        int id PK
        string role
        string status
        string message
        datetime joined_at
    }

    PROJECT_TASK {
        int id PK
        string title
        string description
        string status
        string priority
        date due_date
        datetime created_at
    }

    PROJECT_MILESTONE {
        int id PK
        string title
        string description
        date target_date
        bool is_completed
        datetime completed_at
        datetime created_at
    }

    ORGANIZATION_PROFILE {
        int id PK
        string name
        string org_type
        string description
        string website
        string contact_email
        image logo
        bool is_verified
        datetime created_at
    }

    PARTNERSHIP_REQUEST {
        int id PK
        string message
        string status
        datetime created_at
        datetime updated_at
    }

    SPONSORED_CHALLENGE {
        int id PK
        string sponsorship_type
        string contribution_description
        decimal funding_amount
        date start_date
        date end_date
        string status
        datetime created_at
    }

    IMPACT_REPORT {
        int id PK
        string title
        string description
        int beneficiaries_count
        bool is_verified
        string verified_by_org
        date report_date
        string media_coverage
        datetime created_at
    }

    AI_ANALYSIS_LOG {
        int id PK
        string feature_used
        string input_summary
        int tokens_used
        bool success
        string error_message
        datetime created_at
    }

    USER ||--o{ CHALLENGE : "creates"
    USER ||--o{ CHALLENGE_REPORT : "files"
    USER ||--o{ CHALLENGE_BOOKMARK : "bookmarks"
    USER ||--o{ SOLUTION_PROPOSAL : "submits"
    USER ||--o{ SOLUTION_VOTE : "casts"
    USER ||--o{ DISCUSSION_COMMENT : "writes"
    USER ||--o{ PROJECT_TEAM : "leads"
    USER ||--o{ TEAM_MEMBERSHIP : "has"
    USER ||--o{ PROJECT_TASK : "assigned_to"
    USER ||--o{ ORGANIZATION_PROFILE : "manages"
    USER ||--o{ IMPACT_REPORT : "authors"
    USER ||--o{ AI_ANALYSIS_LOG : "triggers"

    CHALLENGE_CATEGORY ||--o{ CHALLENGE : "categorizes"
    CHALLENGE ||--o{ SOLUTION_PROPOSAL : "has"
    CHALLENGE ||--o{ CHALLENGE_REPORT : "receives"
    CHALLENGE ||--o{ CHALLENGE_BOOKMARK : "receives"
    CHALLENGE ||--o{ PROJECT_TEAM : "addressed_by"
    CHALLENGE ||--o{ SPONSORED_CHALLENGE : "receives"
    CHALLENGE ||--o{ AI_ANALYSIS_LOG : "analyzed_by"

    SOLUTION_PROPOSAL ||--o{ SOLUTION_VOTE : "receives"
    SOLUTION_PROPOSAL ||--o{ DISCUSSION_COMMENT : "has"

    PROJECT_TEAM ||--o{ TEAM_MEMBERSHIP : "has"
    PROJECT_TEAM ||--o{ PROJECT_TASK : "contains"
    PROJECT_TEAM ||--o{ PROJECT_MILESTONE : "tracks"
    PROJECT_TEAM ||--o{ IMPACT_REPORT : "produces"
    PROJECT_TEAM ||--o{ PARTNERSHIP_REQUEST : "receives"

    ORGANIZATION_PROFILE ||--o{ PARTNERSHIP_REQUEST : "sends"
    ORGANIZATION_PROFILE ||--o{ SPONSORED_CHALLENGE : "funds"
```

---

## Key Design Decisions

### Custom User Model
Django's `AbstractUser` is extended with `role`, `bio`, `skills`, `interests`, `organization`, and `avatar` fields. Using a custom user model from the start avoids painful migrations later.

### One Vote Per User Per Proposal
`SolutionVote` has a `unique_together = ('proposal', 'user')` constraint enforced at the database level — not just in application code. This prevents duplicate votes even if application logic is bypassed.

### AI Cache Fields on Challenge
`ai_analysis_cache` (JSONField) and `ai_solutions_cache` (JSONField) store AI responses directly on the Challenge model. This avoids re-calling the API on every page load. The `ai_embedding` field stores a comma-separated vector for semantic similarity search.

### Verified vs Self-Reported Impact
`ImpactReport.is_verified` distinguishes independently verified impact data from self-reported estimates. The UI clearly badges each report accordingly. No numbers are presented as verified facts unless explicitly marked.

### AI Analysis Log
Every AI API call is logged in `AIAnalysisLog` with the feature used, token count, success status, and error message. This enables monitoring, debugging, and cost estimation.

### Cascade Deletes
Challenge deletion cascades to all related proposals, votes, comments, team links, bookmarks, and reports. User deletion sets the `creator` field to `NULL` on challenges (via `SET_NULL`) to preserve the challenge record.

---

## Model Relationships Summary

| From | To | Relationship |
|------|----|--------------|
| User | Challenge | One-to-many (creator) |
| User | SolutionProposal | One-to-many (author) |
| User | SolutionVote | One-to-many (unique per proposal) |
| User | ProjectTeam | One-to-many (leader) |
| User | TeamMembership | One-to-many (member) |
| Challenge | ChallengeCategory | Many-to-one |
| Challenge | SolutionProposal | One-to-many |
| Challenge | ProjectTeam | One-to-many |
| ProjectTeam | ProjectTask | One-to-many |
| ProjectTeam | ProjectMilestone | One-to-many |
| ProjectTeam | ImpactReport | One-to-many |
| OrganizationProfile | PartnershipRequest | One-to-many |
| OrganizationProfile | SponsoredChallenge | One-to-many |
