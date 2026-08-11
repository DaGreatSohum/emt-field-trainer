# EMT Field Trainer

A React Native/Expo field-training app backed by Django and SQLite. It follows the supplied architecture: students search 20 protocol-grounded scenarios, complete an adaptive chat-style simulation, and receive a saved score and performance review.

## Included

- 20 scenarios mapped to the supplied 2026 Maryland EMS protocols
- Adaptive next prompts based on missed and safety-critical concepts
- Attempt status, scores, feedback, and transcripts stored in SQLite
- Searchable mobile scenario dashboard
- Chat-style field simulation and final evaluation
- Training-only safety notice

## Quick start

Requirements: Python 3.9+, Node.js 20.19+, and Expo Go or an iOS/Android simulator.

From the project folder:

```bash
./run-dev.sh
```

The script migrates SQLite, starts Django on all local interfaces, detects the Mac's LAN IP, passes that API address to Expo, and stops Django when Expo exits.

The browser version is available at:

```text
http://localhost:8000/
```

Use `localhost` or `127.0.0.1` in the browser. `0.0.0.0` is the address Django
binds to so other devices can connect; it is not the recommended browser URL.

After Expo starts:

- Press `i` for the iOS Simulator.
- Press `a` for an Android emulator.
- Or scan the QR code with Expo Go while the phone and computer are on the same Wi-Fi network.

## First-time setup

Only needed if dependencies are missing:

```bash
cd "/Users/sohummishrasen/Documents/EMT Field Trainer App"
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cd mobile
npm install
cd ..
./run-dev.sh
```

## Run the services separately

Terminal 1:

```bash
cd "/Users/sohummishrasen/Documents/EMT Field Trainer App"
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver 0.0.0.0:8000
```

Terminal 2 (replace the example IP with the computer's LAN address for a physical phone):

```bash
cd "/Users/sohummishrasen/Documents/EMT Field Trainer App/mobile"
EXPO_PUBLIC_API_URL=http://192.168.1.20:8000/api npm start
```

For iOS Simulator, `http://127.0.0.1:8000/api` works. For Android Emulator, use `http://10.0.2.2:8000/api`.

## Verification

```bash
cd "/Users/sohummishrasen/Documents/EMT Field Trainer App"
.venv/bin/python manage.py test
cd mobile
npx tsc --noEmit
```

Production security controls and deployment obligations are documented in
[`SECURITY.md`](SECURITY.md). Follow [`APP_STORE_CHECKLIST.md`](APP_STORE_CHECKLIST.md)
before creating an iOS release; the checked-in EAS API domain is deliberately a
placeholder and must be replaced with the deployed HTTPS backend.

## Hosting

`render.yaml` contains a Render Blueprint for the Django web/API service. Its free
configuration is useful for staging, but its SQLite file is ephemeral. Before a public
App Store release, use a paid persistent disk with `DJANGO_DATABASE_PATH=/var/data/db.sqlite3`
or migrate production to managed PostgreSQL. Never represent a free ephemeral service
as durable production storage.

## Clinical scope

This is an educational training aid, not a clinical decision-support system. Real patient care must follow current Maryland protocols, local jurisdictional policy, online medical direction, and the clinician's authorized scope of practice.
