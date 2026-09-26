## MODIFIED Requirements

### Requirement: The client stops polling on any terminal status
While a job is being separated the client SHALL poll `GET /jobs/{job_id}` and SHALL stop when the status is anything other than `pending` or `processing`. It SHALL NOT enumerate the terminal statuses it knows about, because an unrecognised status would then poll forever.

#### Scenario: Polling stops on success
- **WHEN** a polled job reaches `done`
- **THEN** polling stops and the mixer opens

#### Scenario: Polling stops on failure
- **WHEN** a polled job reaches `failed`
- **THEN** polling stops and the job's error is displayed

#### Scenario: Polling stops on an unrecognised status
- **WHEN** a polled job returns a status the client does not specifically handle, such as `expired`
- **THEN** polling stops and a message is shown, rather than the client polling indefinitely against a job that will never change

#### Scenario: Expired job does not open an empty mixer
- **WHEN** a job is `expired`
- **THEN** the client explains that the audio was removed rather than opening a mixer with no loadable stems
