## ADDED Requirements

### Requirement: DEMUCS_DEVICE controls inference device
The system SHALL read the `DEMUCS_DEVICE` environment variable and pass its value to Demucs as `--device`. If the variable is not set, the system SHALL default to `"cuda"` when `torch.cuda.is_available()` returns `True`, otherwise `"cpu"`.

#### Scenario: CUDA available and no env var set
- **WHEN** `torch.cuda.is_available()` returns `True` and `DEMUCS_DEVICE` is not set
- **THEN** Demucs is invoked with `--device cuda`

#### Scenario: No GPU and no env var set
- **WHEN** `torch.cuda.is_available()` returns `False` and `DEMUCS_DEVICE` is not set
- **THEN** Demucs is invoked with `--device cpu`

#### Scenario: Env var overrides auto-detection
- **WHEN** `DEMUCS_DEVICE=cpu` is set and a CUDA GPU is present
- **THEN** Demucs is invoked with `--device cpu`

#### Scenario: Invalid device value causes job failure
- **WHEN** `DEMUCS_DEVICE` is set to an unsupported value
- **THEN** the separation worker catches the Demucs error and marks the job as `failed`

### Requirement: DEMUCS_DEVICE documented in env example
The `apps/api/.env.example` file SHALL include a commented-out entry for `DEMUCS_DEVICE` with its default logic and a note that `cuda` is used automatically when a GPU is present.

#### Scenario: Developer sees device config option
- **WHEN** a developer opens `.env.example`
- **THEN** they can see `DEMUCS_DEVICE` with an inline comment explaining valid values and the auto-detect default
