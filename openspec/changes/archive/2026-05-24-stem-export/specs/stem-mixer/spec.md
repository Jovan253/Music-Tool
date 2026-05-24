## ADDED Requirements

### Requirement: Mixer provides an Export button
The stem mixer UI SHALL include an Export button that captures the current per-stem volume and mute state, sends it to the export endpoint, and triggers a browser file download when the response is received.

#### Scenario: User clicks Export with default mix
- **WHEN** the user clicks Export with all stems at full volume and none muted
- **THEN** the browser downloads a file named `mix.mp3`

#### Scenario: User clicks Export with a stem muted
- **WHEN** the user has muted vocals and clicks Export
- **THEN** the exported file contains no vocal audio

#### Scenario: Export in progress shows loading state
- **WHEN** the user clicks Export and the request is in flight
- **THEN** the Export button is disabled and shows a loading indicator

#### Scenario: Export error shown to user
- **WHEN** the export request fails (network error or server error)
- **THEN** an error message is displayed near the Export button
