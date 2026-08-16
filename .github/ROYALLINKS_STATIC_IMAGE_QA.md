# Royal Links static-image QA staging

This marker documents the pre-APK QA rule requested on 2026-08-16:

- Review all Royal Links hole screenshots before APK adoption.
- Runtime app code must not recolor, crop, erase, regenerate, or otherwise mutate course-image pixels.
- Approved hole artwork is generated outside the APK and packaged as a static resource.
- Runtime behavior is decode + contain-fit + draw only.
- Tee-to-green artwork must remain fully visible above bottom navigation.

APK adoption is intentionally held until screenshot approval.
