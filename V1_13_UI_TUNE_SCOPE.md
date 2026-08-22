# V1.13.6 UI Tune Scope Lock

Base: `70b04917935b9d6c481aeb386ff52ae1c1780b11` (`V1.13.6 Round Log`)
Branch: `release/v1.13.6-ui-tune`
Purpose: interim UI/design-only publication based on the proven V1.13.6 field APK.

## Allowed changes
- UI colors, typography, spacing, sizing, alignment, corner radius, shadows and visual hierarchy.
- Canvas drawing/layout constants used only for presentation.
- UI artwork/drawable assets and UI preview-generation assets/scripts.
- User-facing labels where they do not change behavior or data semantics.
- Launcher/app icon polish if requested.
- Version name/code and artifact naming only when producing the interim APK.

## Locked / forbidden changes
- GPS acquisition, filtering, coordinates, geo scope or navigation math.
- Course/hole metadata, yardage values, course packs or hole ordering.
- Round Log persistence/provider/schema or score storage behavior.
- Permissions, activity flow, network behavior or feature logic unless required solely to fix a UI regression and explicitly approved.
- Any modification to `beta-ver2` or other V2 development branches.
- Merge/rebase from `main` or `beta-ver2` into this branch during the interim UI tune.

## Release rule
- All UI tune commits stay on `release/v1.13.6-ui-tune`.
- Build/test from this branch only.
- Do not merge this branch into `beta-ver2`.
- V2 may later cherry-pick individual visual changes only after separate review.
