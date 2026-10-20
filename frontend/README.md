# Frontend

React app for story 1: the AdaptiveTutor landing, Yandex sign-in, and the profile.

The session slice is the one from absolute555: the browser opens `/api/v1/auth/oauth/yandex/start`, the server sends it back with a one-time code, and the app exchanges that code for an access token and a refresh token. Profile rename, photo, sign-out, and account deletion use the same paths. Supplier roles, ratings, and the car landing are not included.

Theme choice (`system`, `light`, `dark`) stays on this device under `adaptivetutor.theme`.

## Setup

```bash
cp .env.example .env
npm install
npm run dev
```

`npm run dev` serves the app at `http://127.0.0.1:5173` and proxies `/api` to `VITE_API_PROXY_TARGET`. The sign-in cookie is set on that site, so the frontend and the API must share it. The backend callback URL should be `http://127.0.0.1:5173/auth/callback` (or `localhost` on the same port).

## Test

```bash
npm test
```

Logic tests do not need the backend. A full sign-in check needs Postgres, Redis, and the API, with this dev server on port 5173.
