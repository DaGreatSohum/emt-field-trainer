# Security model

The application uses the OWASP Mobile Application Security Verification Standard
(MASVS) and OWASP API Security Top 10 as its security baseline. This is a practical
baseline, not a guarantee that defects can never exist. Reassess it before every
public release and after material architecture changes.

## Implemented controls

- **Access control:** Every training attempt has a random UUID plus a separate
  high-entropy bearer token. Only the token hash is stored. Attempt reads and writes
  use constant-time token comparison and return `404` when unauthorized, limiting
  object-ID enumeration and BOLA exposure.
- **Input and abuse controls:** Responses must be text, cannot be blank, are capped
  at 4,000 characters, and request bodies are capped at 16 KiB. Start and response
  endpoints are rate limited.
- **Network security:** Production Django redirects to HTTPS, uses secure cookies,
  HSTS, restrictive trusted hosts/origins, and proxy TLS detection. The mobile release
  refuses to run without an HTTPS API URL.
- **Platform/privacy:** The mobile app requests no camera, microphone, location, or
  Android permissions; Android backups are disabled. The iOS privacy manifest declares
  user-entered training responses as unlinked, non-tracking content used for app
  functionality. Revisit that declaration if analytics, advertising, accounts, crash
  reporting, or other SDKs are added.
- **Browser hardening:** CSP, clickjacking protection, MIME sniffing protection,
  same-origin referrer/COOP policy, disabled sensitive browser capabilities, and
  same-site cookies are enabled. Browser assets are self-hosted.
- **Data minimization:** The UI warns users not to enter patient identifiers. Attempts
  expire after the configured retention period (90 days by default). Scenario-list
  responses do not expose another user's progress or score.
- **Secrets and release integrity:** Production secrets come from environment
  variables, `.env` and signing artifacts are ignored, dependencies are pinned, and
  no secret is embedded in the React Native bundle.

## Production obligations

1. Put Django behind a maintained TLS reverse proxy or managed HTTPS service. Never
   expose Gunicorn directly to the internet.
2. Store `DJANGO_SECRET_KEY` and signing credentials in the host's secret manager.
3. Replace the in-process rate-limit cache with Redis before using multiple workers or
   instances. The current local-memory limiter is intentionally suitable only for a
   single-instance deployment.
4. SQLite remains supported for the requested single-instance design. Protect the
   database and backups with restrictive filesystem permissions and encrypted storage.
   Use managed PostgreSQL before horizontal scaling or high concurrent load.
5. Centralize security logs and uptime/error monitoring without recording answer text,
   bearer tokens, or real patient information. Establish backup-restore tests and an
   incident-response contact.
6. Run dependency and security checks before each release, promptly patch supported
   Django/Expo versions, and arrange an independent penetration test before clinical
   training deployment.
7. Confirm that use of Maryland protocol content, organization names, logos, and other
   materials is licensed. This repository does not establish those rights.

## Security verification

```bash
.venv/bin/python manage.py test trainer
.venv/bin/python manage.py check
.venv/bin/pip check
cd mobile
npm run typecheck
npx expo-doctor
npm audit --omit=dev
```

At the August 11, 2026 review, `npm audit fix` removed all compatible fixes and
`expo-doctor` passed 18/18 checks. The registry still reports advisories in Expo/Metro
build-tool dependencies (`image-size`, `postcss`, and an indirect `uuid`); npm's only
offered remediation is a breaking jump to Expo 57. These tools are not exposed as
server-side request handlers in the shipped app, but the advisories remain a supply-
chain release risk. Re-run the audit and upgrade to an Expo-supported patched SDK as
soon as Expo publishes a compatible path; do not conceal or waive the findings.

For a production-settings review, provide temporary non-secret test values:

```bash
DJANGO_DEBUG=false \
DJANGO_SECRET_KEY='replace-with-a-long-random-test-value' \
DJANGO_ALLOWED_HOSTS='api.example.com' \
DJANGO_CSRF_TRUSTED_ORIGINS='https://api.example.com' \
.venv/bin/python manage.py check --deploy
```

Report vulnerabilities privately to the application's designated security contact.
Do not include tokens, production secrets, or real patient information in reports.
