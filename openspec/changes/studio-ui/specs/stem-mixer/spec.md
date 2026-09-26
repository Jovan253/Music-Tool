## ADDED Requirements

### Requirement: The mixer provides transport controls and a time readout
The mixer SHALL provide play/pause, skip backward and skip forward by a fixed interval, and a readout of current position against total duration. Position SHALL be driven by a single channel acting as the clock, because subscribing every channel to time updates would make the displayed time flicker between them.

#### Scenario: Position advances during playback
- **WHEN** playback is running
- **THEN** the readout advances and shows position and duration in minutes and seconds

#### Scenario: Skipping moves every channel together
- **WHEN** the listener skips forward or backward
- **THEN** all four channels move to the same position and stay aligned

#### Scenario: Transport is inert until every channel is loaded
- **WHEN** the stems have not all finished loading
- **THEN** the transport controls are disabled rather than acting on a partial set of channels

### Requirement: Each channel is visually identified
Every channel SHALL carry a consistent colour used by both its waveform and its channel marker, and its solo and mute controls SHALL be visibly lit when engaged. A channel silenced by another channel's solo SHALL be visibly de-emphasised, so the listener can see why it is inaudible.

#### Scenario: Soloing dims the other channels
- **WHEN** one channel is soloed
- **THEN** that channel stays fully rendered and the other three are visibly dimmed

#### Scenario: Engaged controls are legible at a glance
- **WHEN** a channel is muted or soloed
- **THEN** its control is lit in a colour distinct from the inactive state, not merely outlined

### Requirement: Loading and failure are visible states
The mixer SHALL show a placeholder shaped like audio while a waveform loads, and SHALL surface a readable message if the stems cannot be fetched, rather than rendering an empty console.

#### Scenario: Waveforms are loading
- **WHEN** stem audio is still being fetched
- **THEN** each channel shows a skeleton in place of its waveform

#### Scenario: Stems cannot be loaded
- **WHEN** fetching the stem URLs fails
- **THEN** an error is displayed explaining that the track could not be loaded

### Requirement: The mixer is usable on a phone
Channel rows SHALL reflow on narrow viewports so that label, waveform and controls stack rather than overflowing horizontally.

#### Scenario: Narrow viewport
- **WHEN** the viewport is narrower than a tablet
- **THEN** each channel stacks vertically and no horizontal scrolling is required
