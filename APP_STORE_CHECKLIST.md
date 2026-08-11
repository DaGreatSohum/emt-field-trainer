# Apple App Store release checklist

## Accounts and public services

- Enroll in the Apple Developer Program and enable two-factor authentication. An
  organization enrollment also requires its legal entity details and D-U-N-S number.
- Deploy the Django API at a stable public HTTPS domain. Replace both placeholder URLs
  in `mobile/eas.json` before building.
- Host public support, privacy-policy, and terms URLs. The project includes `/privacy/`
  and `/terms/`; add a real support contact and keep all disclosures accurate.
- Verify that all scenario content is independently written and contains no third-party
  logos, reproduced protocol text, copyrighted graphics, or third-party training material.

## App Store Connect metadata

- Create the App Store Connect app record before upload. Confirm the unique bundle ID;
  change `com.emtfieldtrainer.app` if it is unavailable or not owned by your team.
- Supply the name, subtitle, description, keywords, category, support URL, privacy URL,
  copyright, review contact, and review notes. Explain that this is a training aid—not
  clinical decision support—and keep the backend available during review.
- Complete the age-rating questionnaire and App Privacy answers. The current manifest
  assumes training answers are unlinked user content used only for functionality and
  that there is no tracking. Change both the manifest and store answers if actual data
  handling changes.
- Upload the 1024×1024 App Store icon and required device screenshots. Do not show real
  patient information in screenshots.
- As a recommended quality-control step, consider independent clinical review for
  accuracy and legal review for branding, content-rights, and disclaimer questions.

## Release configuration

1. Set the real API address in `mobile/eas.json`, for example
   `https://api.yourdomain.com/api`.
2. Increment `version`, `ios.buildNumber`, and `android.versionCode` for later releases.
3. Keep `usesNonExemptEncryption: false` only while the app uses ordinary operating-
   system HTTPS and contains no custom or non-exempt encryption. Re-evaluate if that
   changes.
4. Verify the build uses Apple's currently required Xcode/iOS SDK. As of April 28,
   2026, App Store Connect requires Xcode 26 and the iOS 26 SDK.
5. Test on physical supported devices, poor/no network, interrupted requests, fresh
   installs, upgrades, accessibility text sizes, and backend failure modes.

## Build and submit

```bash
cd "/Users/sohummishrasen/Documents/EMT Field Trainer App/mobile"
npm install
npm run typecheck
npx expo-doctor
npx eas-cli login
npx eas-cli build --platform ios --profile production
npx eas-cli submit --platform ios --profile production
```

Use TestFlight for internal/external testing before submission. EAS will guide you
through Apple signing credentials; do not commit those credentials to this project.
Submission still requires completing App Store Connect metadata, export-compliance
answers, privacy answers, pricing/availability, and selecting the uploaded build.
