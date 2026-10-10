# Tempo Board design notes

## Direction

Make a quiet work surface with the familiarity of a paper planner and the
clarity of a simple instrument. Use warm paper around an evergreen timer card;
reserve the soft amber accent for the main action and elapsed-time track.

## Foundations

- **Typography:** self-hosted Inter Variable, matching the template's deliberate
  Inter preference. Use tabular numerals for the countdown.
- **Canvas:** warm ivory with dark green text and muted green supporting text.
- **Timer:** deep evergreen surface, cream type, and a restrained amber progress
  line. Use one soft offset shadow for depth.
- **Controls:** native buttons, text inputs, and radios with visible labels,
  visible keyboard focus, and no icon-only actions.
- **Layout:** timer first in document order; queue alongside it on wide screens
  and below it on narrow screens. Keep copy short and controls at least 44px
  tall.

## Motion

Use quick color changes for selection feedback. When a different session is
chosen, give the title a small opacity and vertical transition to keep the
content change legible. The progress fill moves linearly with the countdown.
Respect `prefers-reduced-motion` by removing the title's positional movement;
keep state readable without animation. Do not animate the timer controls or
move the queue on hover.

## States

The screen covers ready, running, paused, complete, and empty-queue states. The
session form uses browser validation and describes its length options. There is
no loading or network-error state because this starter has no remote requests.
