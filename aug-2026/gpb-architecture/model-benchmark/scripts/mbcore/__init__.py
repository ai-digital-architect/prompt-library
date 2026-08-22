"""model-benchmark harness core.

Version discipline: a change to scoring, matching, resolution or the response
schema invalidates cross-version leaderboard comparison until a backfill runs.
These constants are stamped into every run manifest so the report can tell
whether two rounds are comparable — see skills/change-management/SKILL.md.
"""

HARNESS_VERSION = "1.0.0"
SCORING_VERSION = "1.0.0"
MATCHER_VERSION = "1.0.0"
RESOLVER_VERSION = "1.0.0"
RESPONSE_SCHEMA_VERSION = "1.0.0"

# Changing any of these REQUIRES a backfill before results are compared across
# the boundary. Listed explicitly so the check is not a matter of memory.
COMPARABILITY_CRITICAL = (
    "SCORING_VERSION",
    "MATCHER_VERSION",
    "RESOLVER_VERSION",
    "RESPONSE_SCHEMA_VERSION",
)
