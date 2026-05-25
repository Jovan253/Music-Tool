# Spec: user-auth

## Requirement: Users can sign up with email and password
The system SHALL allow new users to create an account using an email address and password via Supabase Auth. On success the user is automatically signed in and a session is established.

### Scenario: Successful sign-up
- **WHEN** a user submits a valid email and password on the sign-up form
- **THEN** the account is created, the user is signed in, and the app transitions to the main upload view

### Scenario: Duplicate email rejected
- **WHEN** a user attempts to sign up with an email that already has an account
- **THEN** the form displays an error and no new account is created

### Scenario: Invalid password rejected
- **WHEN** a user submits a password shorter than 6 characters
- **THEN** the form displays a validation error before submitting

## Requirement: Users can log in with email and password
The system SHALL allow existing users to authenticate using their email and password. On success a Supabase session is established and the access token is available for API requests.

### Scenario: Successful login
- **WHEN** a user submits valid credentials on the login form
- **THEN** the user is signed in and the app transitions to the main upload view

### Scenario: Wrong credentials rejected
- **WHEN** a user submits an incorrect password or unknown email
- **THEN** the form displays an authentication error and the user remains on the login page

## Requirement: Users can log out
The system SHALL allow authenticated users to end their session. On logout the session token is cleared and the user is redirected to the login page.

### Scenario: Logout clears session
- **WHEN** a user clicks the logout button
- **THEN** the session is invalidated client-side and the user sees the login page

## Requirement: Session persists across page reloads
The system SHALL restore the user's session automatically on page load if a valid unexpired token exists in local storage.

### Scenario: Returning user is auto-signed-in
- **WHEN** a user with an active session reloads the page
- **THEN** the app initialises in the authenticated state without requiring a new login

### Scenario: Expired session requires re-login
- **WHEN** a user's session has expired and they reload the page
- **THEN** the app shows the login page

## Requirement: Unauthenticated users cannot access job routes
The backend SHALL reject any request to a job route (`POST /upload`, `GET /jobs/{id}`, `GET /jobs/{id}/stems/{name}`, `POST /jobs/{id}/export`) that does not include a valid Bearer token.

### Scenario: Missing token returns 401
- **WHEN** a request is made to a job route with no Authorization header
- **THEN** the server responds `401 Unauthorized`

### Scenario: Invalid token returns 401
- **WHEN** a request is made with a malformed or expired JWT
- **THEN** the server responds `401 Unauthorized`

### Scenario: Valid token is accepted
- **WHEN** a request is made with a valid Supabase JWT in the Authorization header
- **THEN** the server processes the request normally
