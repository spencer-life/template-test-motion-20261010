# Design and skill setup

This starter keeps project-specific visual decisions in `DESIGN.md` and
`PRODUCT.md`. Its app uses a Vite entry point with native HTML controls, custom
CSS, self-hosted Inter Variable, and no component or animation library.

## Reviewed guidance

The project-local skills in `.agents/skills` were read from these upstream
sources and copied into this repository so they remain available in clean
clones:

| Skill | Reviewed source | Revision |
| --- | --- | --- |
| `modern-web-guidance` | [GoogleChrome/modern-web-guidance](https://github.com/GoogleChrome/modern-web-guidance/tree/a97286845f2baba38988f9e5fe2b2a1351021e50) | `a97286845f2baba38988f9e5fe2b2a1351021e50` |
| `animate`, `review-animations` | [emilkowalski/skills](https://github.com/emilkowalski/skills/tree/e8a175de22ae1e49370fc144c1f3bb9aeedf988d) | `e8a175de22ae1e49370fc144c1f3bb9aeedf988d` |

The Emil skill copies carry their upstream MIT license. The Modern Web Guidance
copy carries its upstream Apache-2.0 license. The local `review-animations`
copy enables project invocation as required by this repository's motion route;
its `disable-model-invocation` flag is set to `false`, and both Emil skills set
`policy.allow_implicit_invocation: true`. The skill bodies remain otherwise
unchanged. Treat upstream updates as a review and reapply these metadata choices
deliberately.

For app behavior, the work used Impeccable context guidance version `0.1.5`
from its official project. That temporary CLI is not an app dependency; the
project retains its narrow `.impeccable/config.json` typography exception and
the written design decisions here.

## Applying the guidance

- Read `modern-web-guidance` for browser forms, errors, motion, and responsive
  platform behavior. Its research in this setup focused on native form
  validation, accessible error announcements, timer semantics, reduced motion,
  and `:has()` support.
- Read `animate` when implementing animation and `review-animations` when
  reviewing motion. The current app uses only a short selected-title transition
  and a timer progress fill; both respect reduced-motion preferences.
- Use Impeccable for future frontend critique or polish when the skill is
  available. When it is not available, keep the product and visual decisions
  in the tracked project docs and verify layout, focus, contrast, and reduced
  motion directly.

The local skill files and `skills-lock.json` are tracked. The lock records their
source revisions and content hashes; it does not prove native host discovery.
No global skill settings or hooks are required.
