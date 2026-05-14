# Requirements Document

## Introduction

DualMind is a full-stack AI orchestration and conversational platform that extends the existing HuggingGPT/DualMind codebase into a premium, production-grade SaaS product. The platform combines a futuristic landing page with a fully-featured AI chat application backed by a dual-agent (Generator + Discriminator) architecture. It introduces persistent user authentication, PostgreSQL-backed chat history, real-time streaming responses, and a polished UI inspired by ChatGPT, Claude, Perplexity, and Linear.

The existing codebase provides a React/TypeScript frontend (Vite, Tailwind CSS), a Python FastAPI backend with an orchestrator, planner, verifier, and tool pipeline. This spec defines the requirements for the complete platform rewrite and extension.

## Glossary

- **DualMind_Platform**: The complete full-stack application described in this document.
- **Landing_Page**: The public-facing marketing page at the root route (`/`).
- **Chat_Application**: The authenticated AI chat interface accessible after login.
- **Dual_Agent**: The Generator + Discriminator agent pair in the backend orchestrator.
- **Generator**: The planning/LLM agent that produces task plans and responses.
- **Discriminator**: The verifier agent that scores and approves/rejects plans.
- **Orchestrator**: The Python backend module coordinating the Dual_Agent pipeline.
- **Auth_Service**: The backend service handling JWT issuance, validation, and session management.
- **Chat_Service**: The backend service managing conversation CRUD and message persistence.
- **User**: An authenticated human interacting with the Chat_Application.
- **Session**: A single browser session identified by a JWT access token.
- **Conversation**: A named, persistent sequence of messages belonging to a User.
- **Message**: A single user or assistant turn within a Conversation.
- **Streaming_Response**: Server-Sent Events (SSE) delivery of assistant tokens as they are generated.
- **Sidebar**: The left-panel UI component listing Conversations and navigation controls.
- **Profile_Menu**: The dropdown UI component in the top-right corner for account and settings actions.
- **Toast**: A transient, non-blocking notification displayed to the User.
- **Skeleton_Loader**: An animated placeholder shown while content is loading.
- **DB**: The PostgreSQL relational database.
- **JWT**: JSON Web Token used for stateless authentication.
- **bcrypt**: The password hashing algorithm used for credential storage.

---

## Requirements

### Requirement 1: Landing Page — Hero and Navigation

**User Story:** As a visitor, I want to see a compelling, futuristic landing page, so that I understand DualMind's value proposition and am motivated to try the product.

#### Acceptance Criteria

1. THE Landing_Page SHALL render a full-viewport hero section containing the DualMind brand name, a tagline, an animated AI visual, and a primary call-to-action button labelled "Try Now".
2. THE Landing_Page SHALL render a sticky top navigation bar containing the DualMind logo, navigation links (Features, How It Works, Pricing, FAQ), and Sign In / Sign Up buttons.
3. WHEN a visitor clicks the "Try Now" button, THE Landing_Page SHALL navigate the visitor to the Chat_Application login route.
4. WHEN a visitor clicks "Sign In" in the navigation bar, THE Landing_Page SHALL navigate the visitor to the login page.
5. WHEN a visitor clicks "Sign Up" in the navigation bar, THE Landing_Page SHALL navigate the visitor to the signup page.
6. THE Landing_Page SHALL apply animated gradient backgrounds, glassmorphism card styles, and neon glow effects consistent with the existing Tailwind design tokens.
7. THE Landing_Page SHALL be fully responsive, rendering correctly on viewports from 320px to 2560px wide.

---

### Requirement 2: Landing Page — Content Sections

**User Story:** As a visitor, I want to read about DualMind's features, architecture, pricing, and FAQs, so that I can make an informed decision before signing up.

#### Acceptance Criteria

1. THE Landing_Page SHALL render a "Features" section containing at least six feature cards, each with an icon, title, and description.
2. THE Landing_Page SHALL render a "How DualMind Works" section that visually explains the Dual_Agent pipeline (Generator → Discriminator → Tool Execution → Response).
3. THE Landing_Page SHALL render a "Testimonials" section containing at least three testimonial cards with avatar, name, role, and quote.
4. THE Landing_Page SHALL render a "Pricing" section containing at least two pricing tiers, each listing included features and a call-to-action button.
5. THE Landing_Page SHALL render an "FAQ" section containing at least five accordion items that expand and collapse on click.
6. THE Landing_Page SHALL render a footer containing copyright text, social links, and navigation links.
7. WHEN a User scrolls the Landing_Page, THE Landing_Page SHALL apply smooth scroll-triggered entrance animations to each section.

---

### Requirement 3: User Authentication — Registration

**User Story:** As a new visitor, I want to create an account with my email and password, so that I can access the Chat_Application and have my history saved.

#### Acceptance Criteria

1. THE Auth_Service SHALL expose a `POST /api/auth/register` endpoint that accepts `email`, `password`, and `display_name`.
2. WHEN a registration request is received with a valid email and a password of at least 8 characters, THE Auth_Service SHALL hash the password using bcrypt and persist the User record to the DB.
3. WHEN a registration request is received with an email that already exists in the DB, THE Auth_Service SHALL return HTTP 409 with a descriptive error message.
4. WHEN a registration request is received with a password shorter than 8 characters, THE Auth_Service SHALL return HTTP 422 with a descriptive validation error.
5. WHEN registration succeeds, THE Auth_Service SHALL return HTTP 201 with a JWT access token and a refresh token.
6. THE Signup_Page SHALL display inline validation errors for invalid email format and password length before form submission.
7. WHEN a User submits the signup form with valid data and the server returns HTTP 201, THE Signup_Page SHALL redirect the User to the Chat_Application.

---

### Requirement 4: User Authentication — Login and Session

**User Story:** As a registered User, I want to log in with my email and password and have my session persist across browser refreshes, so that I don't have to log in repeatedly.

#### Acceptance Criteria

1. THE Auth_Service SHALL expose a `POST /api/auth/login` endpoint that accepts `email` and `password`.
2. WHEN a login request is received with valid credentials, THE Auth_Service SHALL return HTTP 200 with a JWT access token (15-minute expiry) and a refresh token (7-day expiry).
3. WHEN a login request is received with invalid credentials, THE Auth_Service SHALL return HTTP 401 with a generic error message that does not reveal whether the email or password was incorrect.
4. THE Login_Page SHALL provide a "Remember me" checkbox; WHEN checked, THE Login_Page SHALL store the refresh token in a persistent cookie; WHEN unchecked, THE Login_Page SHALL store the refresh token in a session cookie.
5. THE Auth_Service SHALL expose a `POST /api/auth/refresh` endpoint; WHEN a valid refresh token is provided, THE Auth_Service SHALL return a new JWT access token.
6. WHEN the JWT access token expires and a valid refresh token is present, THE Chat_Application SHALL automatically call `/api/auth/refresh` and retry the original request without User intervention.
7. THE Auth_Service SHALL expose a `POST /api/auth/logout` endpoint; WHEN called, THE Auth_Service SHALL invalidate the refresh token in the DB.
8. WHEN a User clicks "Logout" in the Profile_Menu, THE Chat_Application SHALL call `/api/auth/logout`, clear stored tokens, and redirect the User to the Login_Page.

---

### Requirement 5: User Authentication — Password Security

**User Story:** As a User, I want my password stored securely, so that my account is protected even if the database is compromised.

#### Acceptance Criteria

1. THE Auth_Service SHALL hash all passwords using bcrypt with a minimum cost factor of 12 before storing them in the DB.
2. THE Auth_Service SHALL never return or log plaintext passwords.
3. WHEN comparing a login password to a stored hash, THE Auth_Service SHALL use a constant-time comparison function to prevent timing attacks.
4. THE DB SHALL store only the bcrypt hash, never the plaintext password.

---

### Requirement 6: PostgreSQL Database Schema

**User Story:** As a developer, I want a well-structured PostgreSQL schema, so that user data, conversations, and messages are stored efficiently and can be queried quickly.

#### Acceptance Criteria

1. THE DB SHALL contain a `users` table with columns: `id` (UUID primary key), `email` (unique, not null), `password_hash` (not null), `display_name`, `avatar_url`, `created_at`, `updated_at`.
2. THE DB SHALL contain a `refresh_tokens` table with columns: `id` (UUID), `user_id` (foreign key → users), `token_hash`, `expires_at`, `created_at`, `revoked` (boolean).
3. THE DB SHALL contain a `conversations` table with columns: `id` (UUID primary key), `user_id` (foreign key → users), `title`, `pinned` (boolean, default false), `created_at`, `updated_at`.
4. THE DB SHALL contain a `messages` table with columns: `id` (UUID primary key), `conversation_id` (foreign key → conversations), `role` (enum: user/assistant), `content` (text), `metadata` (JSONB), `created_at`.
5. THE DB SHALL contain a `user_settings` table with columns: `user_id` (foreign key → users, primary key), `theme` (enum: light/dark, default dark), `default_model`, `updated_at`.
6. THE DB SHALL apply an index on `messages.conversation_id` and `messages.created_at` to support fast chronological retrieval.
7. THE DB SHALL apply an index on `conversations.user_id` and `conversations.updated_at` to support fast sidebar listing sorted by recency.

---

### Requirement 7: Chat History — Persistence and Retrieval

**User Story:** As a User, I want my chat history saved to the database and loaded when I log in, so that I can continue previous conversations from any device.

#### Acceptance Criteria

1. THE Chat_Service SHALL expose a `GET /api/conversations` endpoint; WHEN called with a valid JWT, THE Chat_Service SHALL return the authenticated User's Conversations ordered by `updated_at` descending, grouped by date (Today, Yesterday, Last 7 Days, Older).
2. THE Chat_Service SHALL expose a `GET /api/conversations/:id/messages` endpoint; WHEN called with a valid JWT and a Conversation ID belonging to the User, THE Chat_Service SHALL return all Messages for that Conversation ordered by `created_at` ascending.
3. WHEN a User sends a message, THE Chat_Service SHALL persist the user Message and the assistant Message to the DB within the active Conversation.
4. WHEN a User starts a new chat, THE Chat_Service SHALL create a new Conversation record and set its title to the first 60 characters of the first user message.
5. WHEN the Chat_Application loads after login, THE Chat_Application SHALL fetch and display the User's Conversations in the Sidebar within 2 seconds.
6. IF a DB write fails during message persistence, THEN THE Chat_Service SHALL return HTTP 500 and THE Chat_Application SHALL display a Toast error without losing the message content from the UI.

---

### Requirement 8: Chat History — Management

**User Story:** As a User, I want to rename, pin, delete, and search my conversations, so that I can keep my chat history organised.

#### Acceptance Criteria

1. THE Chat_Service SHALL expose a `PATCH /api/conversations/:id` endpoint; WHEN called with a valid JWT and a `title` field, THE Chat_Service SHALL update the Conversation title.
2. THE Chat_Service SHALL expose a `PATCH /api/conversations/:id` endpoint; WHEN called with a valid JWT and a `pinned` field, THE Chat_Service SHALL toggle the pinned state of the Conversation.
3. THE Chat_Service SHALL expose a `DELETE /api/conversations/:id` endpoint; WHEN called with a valid JWT, THE Chat_Service SHALL soft-delete the Conversation and all its Messages.
4. THE Sidebar SHALL display pinned Conversations at the top of the list, separated from unpinned Conversations by a visual divider.
5. THE Sidebar SHALL provide a search input; WHEN a User types in the search input, THE Sidebar SHALL filter the displayed Conversations to those whose title contains the search string (case-insensitive, client-side).
6. WHEN a User renames a Conversation, THE Sidebar SHALL update the displayed title optimistically before the server confirms the change.
7. WHEN a User deletes a Conversation, THE Sidebar SHALL remove it from the list and THE Chat_Application SHALL navigate to a new empty chat if the deleted Conversation was active.

---

### Requirement 9: Chat Interface — Message Rendering

**User Story:** As a User, I want messages to be rendered with rich formatting, syntax-highlighted code, and copy controls, so that I can read and reuse AI responses easily.

#### Acceptance Criteria

1. THE Chat_Application SHALL render assistant messages using a Markdown renderer that supports headings, bold, italic, lists, blockquotes, tables, and inline code.
2. THE Chat_Application SHALL render fenced code blocks with syntax highlighting and a "Copy" button; WHEN the "Copy" button is clicked, THE Chat_Application SHALL copy the code to the clipboard and display a "Copied!" confirmation for 2 seconds.
3. THE Chat_Application SHALL render user messages in a distinct bubble style visually differentiated from assistant messages.
4. WHEN an assistant message is being streamed, THE Chat_Application SHALL display a typing indicator animation until the stream completes.
5. THE Chat_Application SHALL auto-scroll to the latest message as new content arrives during streaming.
6. WHEN a User hovers over an assistant message, THE Chat_Application SHALL display action buttons: Copy full response, Regenerate response.
7. THE Chat_Application SHALL display the timestamp of each message in a human-readable relative format (e.g., "2 minutes ago").

---

### Requirement 10: Chat Interface — Input and Interaction

**User Story:** As a User, I want a rich input area with file upload, voice input, and suggested prompts, so that I can interact with DualMind in multiple ways.

#### Acceptance Criteria

1. THE Chat_Application SHALL provide a multi-line text input that expands vertically up to 200px as the User types and resets to a single line after submission.
2. WHEN the User presses Enter (without Shift), THE Chat_Application SHALL submit the message; WHEN the User presses Shift+Enter, THE Chat_Application SHALL insert a newline.
3. THE Chat_Application SHALL provide a file upload button; WHEN clicked, THE Chat_Application SHALL open a file picker accepting PDF, PNG, and JPEG files up to 10MB.
4. WHEN a file is selected, THE Chat_Application SHALL display a file preview chip in the input area showing the filename and a remove button.
5. THE Chat_Application SHALL provide a voice input button; WHEN clicked and microphone permission is granted, THE Chat_Application SHALL transcribe speech to text using the Web Speech API and populate the input field.
6. WHEN the chat is empty (no messages), THE Chat_Application SHALL display at least four suggested prompt cards; WHEN a User clicks a suggested prompt, THE Chat_Application SHALL populate the input field with that prompt text.
7. THE Chat_Application SHALL support the keyboard shortcut Ctrl+K (Cmd+K on macOS) to focus the chat input from anywhere in the Chat_Application.

---

### Requirement 11: Streaming Responses

**User Story:** As a User, I want to see AI responses appear word-by-word in real time, so that I get immediate feedback and the experience feels fast and alive.

#### Acceptance Criteria

1. THE Chat_Service SHALL expose a `POST /api/chat/stream` endpoint that returns a Server-Sent Events stream of assistant response tokens.
2. WHEN a streaming request is initiated, THE Chat_Application SHALL render tokens incrementally as they arrive, appending each token to the current assistant message bubble.
3. WHEN the stream ends, THE Chat_Application SHALL mark the message as complete and persist it to the DB.
4. IF the stream is interrupted by a network error, THEN THE Chat_Application SHALL display a Toast error and retain the partially received content in the message bubble.
5. WHILE a stream is in progress, THE Chat_Application SHALL display a "Stop generating" button; WHEN clicked, THE Chat_Application SHALL abort the SSE connection and finalise the partial message.

---

### Requirement 12: Profile and Settings

**User Story:** As a User, I want to manage my profile, change my theme, and update my settings, so that I can personalise my DualMind experience.

#### Acceptance Criteria

1. THE Chat_Application SHALL display a Profile_Menu trigger (avatar icon) in the top-right corner of the Chat_Application header.
2. WHEN the Profile_Menu trigger is clicked, THE Chat_Application SHALL display a dropdown containing: My Profile, Settings, Theme Toggle, and Logout.
3. THE Profile_Menu SHALL display the User's avatar image if one is set, or a generated initials avatar if not.
4. WHEN a User clicks "Theme Toggle" in the Profile_Menu, THE Chat_Application SHALL switch between light and dark mode and persist the preference to the DB via `PATCH /api/users/settings`.
5. THE Settings_Page SHALL allow the User to update their display name and upload a new avatar image.
6. WHEN a User uploads a new avatar, THE Chat_Service SHALL store the image and update the `avatar_url` field in the `users` table.
7. THE Chat_Application SHALL load the User's saved theme preference from the DB on login and apply it before the first render to prevent a flash of unstyled content.

---

### Requirement 13: Backend API — Node.js/Express Layer

**User Story:** As a developer, I want a Node.js/Express API layer that handles authentication, conversation management, and proxies AI requests to the Python orchestrator, so that the frontend has a single, consistent API surface.

#### Acceptance Criteria

1. THE Chat_Service SHALL be implemented as a Node.js/Express application running on a configurable port (default 3001).
2. THE Chat_Service SHALL connect to the DB using a connection pool with a minimum of 2 and maximum of 10 connections.
3. THE Chat_Service SHALL validate all incoming request bodies using a schema validation library and return HTTP 422 for invalid payloads.
4. THE Chat_Service SHALL proxy AI generation requests to the Python Orchestrator running on a configurable internal URL.
5. THE Chat_Service SHALL apply rate limiting of 60 requests per minute per authenticated User on AI generation endpoints.
6. THE Chat_Service SHALL return consistent JSON error responses with `error`, `message`, and `statusCode` fields for all 4xx and 5xx responses.
7. THE Chat_Service SHALL log all requests with method, path, status code, and response time using a structured logger.

---

### Requirement 14: Frontend Architecture — React Application Structure

**User Story:** As a developer, I want a scalable, well-organised React application structure, so that the codebase is maintainable and new features can be added efficiently.

#### Acceptance Criteria

1. THE Chat_Application frontend SHALL be organised into the following top-level directories: `src/pages`, `src/components`, `src/layouts`, `src/hooks`, `src/store`, `src/services`, `src/utils`, `src/types`, `src/assets`.
2. THE Chat_Application SHALL use Zustand for global state management, with separate stores for: `authStore` (user, tokens), `chatStore` (conversations, active conversation, messages), `uiStore` (theme, sidebar open/closed, toast queue).
3. THE Chat_Application SHALL use React Router v6 with protected routes; WHEN an unauthenticated User navigates to a protected route, THE Chat_Application SHALL redirect to the Login_Page.
4. THE Chat_Application SHALL use Axios with an interceptor that automatically attaches the JWT access token to all authenticated requests.
5. THE Chat_Application SHALL implement React.lazy and Suspense for route-level code splitting, with Skeleton_Loaders shown during chunk loading.
6. THE Chat_Application SHALL define all shared TypeScript interfaces and types in `src/types/index.ts`.

---

### Requirement 15: UI/UX — Design System and Animations

**User Story:** As a User, I want a visually stunning, consistent, and responsive interface, so that using DualMind feels like a premium AI product.

#### Acceptance Criteria

1. THE Chat_Application SHALL apply the existing Tailwind design tokens (neon-blue, neon-purple, neon-pink, glassmorphism utilities) consistently across all new components.
2. THE Chat_Application SHALL use Framer Motion for all page transitions, sidebar open/close animations, message entrance animations, and modal open/close animations.
3. THE Chat_Application SHALL display Skeleton_Loaders for the Sidebar conversation list and the message history while data is being fetched.
4. THE Chat_Application SHALL display Toast notifications for: successful actions (green), warnings (yellow), and errors (red), with a 4-second auto-dismiss and a manual close button.
5. THE Chat_Application SHALL apply hover microanimations (scale, glow, colour shift) to all interactive elements (buttons, cards, sidebar items).
6. THE Chat_Application SHALL be fully responsive: the Sidebar SHALL collapse to a slide-over drawer on viewports narrower than 768px, accessible via a hamburger menu button.
7. THE Chat_Application SHALL support both light and dark modes, with all components correctly styled in both modes using the existing CSS custom property system.

---

### Requirement 16: Chat Export

**User Story:** As a User, I want to export a conversation, so that I can save or share the content outside of DualMind.

#### Acceptance Criteria

1. THE Chat_Application SHALL provide an "Export" option in the Conversation context menu in the Sidebar.
2. WHEN a User selects "Export as Markdown", THE Chat_Application SHALL generate a Markdown file containing all messages in the Conversation and trigger a browser download.
3. WHEN a User selects "Export as JSON", THE Chat_Application SHALL generate a JSON file containing the full Conversation object (messages, timestamps, metadata) and trigger a browser download.
4. THE exported Markdown file SHALL include message role labels (User, Assistant), timestamps, and formatted content.

---

### Requirement 17: Performance and Reliability

**User Story:** As a User, I want the application to load quickly and handle errors gracefully, so that I have a reliable experience.

#### Acceptance Criteria

1. THE Chat_Application SHALL achieve a Largest Contentful Paint (LCP) of under 2.5 seconds on a simulated 4G connection for the Landing_Page.
2. THE Chat_Application SHALL implement React Error Boundaries around the Chat_Window and Sidebar components; IF a rendering error occurs, THEN THE Chat_Application SHALL display a fallback UI with a "Reload" button instead of a blank screen.
3. THE Chat_Application SHALL lazy-load images on the Landing_Page using the `loading="lazy"` attribute.
4. THE DB queries for conversation listing and message retrieval SHALL complete within 200ms for a User with up to 1000 Conversations and 10,000 Messages, given the indexes defined in Requirement 6.
5. THE Chat_Service SHALL implement request deduplication for concurrent identical GET requests to prevent redundant DB queries.

---

### Requirement 18: Parser and Serializer — Chat State

**User Story:** As a developer, I want chat state serialized to and deserialized from localStorage reliably, so that session persistence works correctly across browser refreshes.

#### Acceptance Criteria

1. THE Chat_Application SHALL serialize the active Conversation's messages to localStorage as a JSON string on every state change.
2. WHEN the Chat_Application initialises, THE Chat_Application SHALL deserialize the stored JSON string back into the message array.
3. THE Serializer SHALL produce valid JSON for all Message objects, including those with nested `executionDetails` and `attachments` fields.
4. FOR ALL valid Message arrays, serializing then deserializing SHALL produce an array structurally equivalent to the original (round-trip property).
5. IF the stored JSON string is malformed, THEN THE Chat_Application SHALL discard it, initialise with an empty message array, and display a Toast warning to the User.
