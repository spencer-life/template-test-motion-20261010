# Tempo Board product context

Tempo Board helps one person turn a short list of intentions into focused
work sessions. The main job is to choose a session, give it a bounded length,
and work through it without managing a larger productivity system.

## User and setting

- **User:** one person planning their own work.
- **Setting:** a browser tab beside the work they are doing.
- **Platform:** a responsive client-side web app.

## Core flow

1. Scan a small session queue and select the current item.
2. Start, pause, continue, or reset its countdown.
3. Add or remove a session when the plan changes.

## Scope and assumptions for this starter

- The initial plan is synthetic sample content; users can edit it in memory.
- Session lengths are 15, 25, or 45 minutes.
- The timer uses the browser clock, so it catches up after a background tab is
  throttled.
- Nothing is stored or sent anywhere. Reloading restores the sample plan.
- Accounts, sync, persistence, notifications, analytics, and service calls are
  outside this starter's scope.
