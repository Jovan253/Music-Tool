## ADDED Requirements

### Requirement: Stored audio is deleted after a retention window
The system SHALL delete a job's original upload and its stem objects once the job is older than a configured retention window, and SHALL then mark the job `expired` with `stems` cleared. The window SHALL be configurable via `STEM_RETENTION_DAYS` and SHALL default to 14 days.

Only jobs whose `created_at` is older than the cutoff and which still have stems recorded SHALL be selected. The cutoff SHALL be computed in UTC and compared against timezone-aware timestamps.

#### Scenario: A job past the window is expired
- **WHEN** the sweep runs and a job is older than the retention window and has stems
- **THEN** its upload and stem objects are deleted, its status becomes `expired`, and its `stems` is cleared

#### Scenario: A job inside the window is untouched
- **WHEN** the sweep runs and a job is newer than the retention window
- **THEN** nothing is deleted and the job is unchanged

#### Scenario: A job with no stems is never selected
- **WHEN** the sweep runs and a job is past the window but has no stems recorded
- **THEN** it is skipped, because there is nothing to delete and nothing to expire

#### Scenario: An already-expired job is not swept twice
- **WHEN** the sweep runs after a job has been expired
- **THEN** it is not selected again, because its stems are cleared

### Requirement: Storage is deleted before the record is updated
The system SHALL delete storage objects before updating the job record. Marking the record first would orphan the objects if deletion then failed, leaving files that nothing references and no later sweep can find.

#### Scenario: Storage deletion fails
- **WHEN** deleting a job's objects raises
- **THEN** the job record is left unchanged so the next sweep retries it, and the failure is logged

#### Scenario: Objects are already gone
- **WHEN** deletion targets a path that no longer exists
- **THEN** the sweep treats it as success and proceeds, because deletion is idempotent

### Requirement: Jobs can be exempted from retention
The system SHALL read a list of exempt job ids from `RETENTION_EXEMPT_JOB_IDS` and SHALL never delete their audio, regardless of age. This exists so a public demo job's stems survive indefinitely.

#### Scenario: An exempt job past the window survives
- **WHEN** the sweep runs and an exempt job is older than the retention window
- **THEN** its audio is not deleted and its status is unchanged

### Requirement: The sweep supports a dry run
The system SHALL support running the sweep without deleting anything, reporting what it would have done. There are no storage backups on the free tier, so the first run against real data must be observable before it is destructive.

#### Scenario: Dry run reports without deleting
- **WHEN** the sweep runs in dry-run mode
- **THEN** it returns the jobs it would expire, and no object is deleted and no record changed

### Requirement: The sweep runs on a schedule
The system SHALL run the sweep daily as a scheduled Modal function. Because the sweep queries the database and touches Supabase storage on every run, it SHALL also serve as the activity that prevents the Supabase free-tier project from auto-pausing.

#### Scenario: Scheduled run executes without an operator
- **WHEN** a day passes
- **THEN** the sweep has run and its outcome is visible in the Modal logs

#### Scenario: Sweep failure is visible
- **WHEN** a scheduled run raises
- **THEN** the failure is recorded in the Modal logs rather than passing silently, since a broken sweep also stops the Supabase keep-alive
