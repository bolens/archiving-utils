# Initial verification evidence

Local validation: `make check`, `actionlint .github/workflows/*.yml`, and `make test-all`. 30 unittest methods pass. Format subtests exercise every catalog conversion. No local dependency skips.

[Artifact and browser receipt](validation.json) binds the Archify specification and delivered HTML by SHA-256. Archify passes 9 of 9 artifact checks with zero errors and warnings. Its browser command checks exact desktop viewports at 1440x900, 1600x1000, 1920x1080, and 2048x1320. Light/dark captures were visually reviewed for readable labels, routes, and containment.

The Pages site was exercised in Chromium at widths 390, 768, and 1440 with 900-pixel height and reduced motion. Checks cover catalog counts, search, empty state, category filtering, clipboard completion, theme switching, keyboard outlines, page errors, and horizontal containment. This does not establish Safari, Firefox, assistive-technology, or touch-device coverage.

[Desktop site](site-desktop.png) · [Mobile site](site-mobile.png) · [Light diagram](architecture-light.png) · [Dark diagram](architecture-dark.png)
