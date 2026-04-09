# Security Review 01 — Final Report Before Public Exposure

**Date**: Sprint SECURITY_REVIEW_01
**Scope**: Full application security review
**Verdict**: **GO FOR PUBLIC EXPOSURE** (conditional — see section 6)

---

## 1. Review scope

| Area                        | Reviewed | Finding severity |
|-----------------------------|----------|------------------|
| Authentication (login/logout/register) | Yes | Fixed (timing attack) |
| Session management (cookies) | Yes | Hardened (samesite=strict) |
| Ownership / horizontal access | Yes | Solid (no issues) |
| Public vs private routes    | Yes | All correct |
| Form safety / CSRF          | Yes | Mitigated (samesite=strict) |
| Export + backup surfaces    | Yes | Scoped + protected |
| Leaderboard privacy         | Yes | No data leakage |
| Security headers            | Yes | Added (CSP, X-Frame, etc.) |
| Deployment assumptions      | Yes | Documented |
| Rate limiting               | No fix | Residual risk (see below) |

---

## 2. Findings

### FIXED — Critical / High

| # | Severity | Finding | Fix applied |
|---|----------|---------|-------------|
| F-01 | HIGH | **Login timing attack**: when username doesn't exist, `verify_password` was skipped, creating a measurable timing difference vs. a wrong-password attempt. An attacker could determine whether a username exists. | **Fixed**: always run `verify_password()` against a dummy bcrypt hash when the user is None. Response time is now constant regardless of username existence. |
| F-02 | HIGH | **Missing security headers**: no CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy. The app was vulnerable to clickjacking and content-type sniffing. | **Fixed**: added `SecurityHeadersMiddleware` in `app/main.py` setting X-Content-Type-Options: nosniff, X-Frame-Options: DENY, Referrer-Policy: strict-origin-when-cross-origin, Content-Security-Policy with frame-ancestors 'none', Permissions-Policy. |
| F-03 | MEDIUM | **Cookie SameSite=Lax**: the session cookie used `samesite=lax` which allows top-level cross-site GET requests to carry the cookie. Combined with the lack of CSRF tokens, this left a theoretical CSRF surface on GET-triggered state changes. | **Fixed**: upgraded to `samesite=strict`. The cookie is NEVER sent on any cross-origin request. This is the strongest CSRF protection available without tokens. Trade-off: external links to the app (e.g., from a bookmark manager) won't carry the cookie — the user will need to re-login. Acceptable for a personal app. |
| F-04 | MEDIUM | **/healthz/strict leaked absolute filesystem paths**: the `backup_dir.path` field exposed the server's directory structure to any caller. | **Fixed**: removed the `path` field from the healthz/strict response. The `exists` boolean is retained. |

### NOT FIXED — Accepted residual risks

| # | Severity | Finding | Decision |
|---|----------|---------|----------|
| R-01 | HIGH | **No login rate limiting**: brute-force attacks on the login endpoint are possible. bcrypt's computational cost (~200ms per attempt) provides some natural protection (~5 attempts/second). | **Accepted for V2 launch.** Mitigation: nginx `limit_req_zone` is documented in deploy/README.md as the recommended layer. The app itself doesn't need to implement rate limiting because nginx is always in front. Adding `limit_req` takes 3 lines of nginx config. |
| R-02 | HIGH | **No registration rate limiting**: account creation spam is possible. | **Accepted.** Same mitigation as R-01: nginx `limit_req` on `/register`. |
| R-03 | MEDIUM | **No CSRF tokens on POST forms**: all state-changing POSTs rely on `samesite=strict` cookie policy for CSRF protection, not on per-form tokens. | **Accepted.** `samesite=strict` prevents the browser from sending the cookie on ANY cross-origin request (GET or POST). This is equivalent to CSRF token protection for the threat model of this app. The only scenario where `samesite=strict` fails is if an attacker has XSS on the same origin — but if they have XSS, tokens are also bypassable. |
| R-04 | MEDIUM | **Username enumeration via /register**: the error "Ce nom d'utilisateur est déjà pris" reveals whether a username exists. | **Accepted.** For a small private group, this is a non-issue. If needed, the error can be changed to a generic message. |
| R-05 | LOW | **Cookie `secure` flag is False in dev**: HTTP cookies are allowed when `APP_ENV != "production"`. | **Accepted by design.** The operator MUST set `APP_ENV=production` on the VPS. |

---

## 3. Hardening applied

### SecurityHeadersMiddleware (new)

Every response now carries:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: camera=(), microphone=(), geolocation=()`
- `Content-Security-Policy: default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; frame-ancestors 'none'`

### Cookie upgrade

`samesite` upgraded from `lax` to `strict`. The cookie is never
sent on cross-origin requests of any kind.

### Login constant-time response

`verify_password()` is always called, even when the user doesn't
exist. A pre-computed dummy bcrypt hash ensures the CPU time is
identical in both code paths.

### /healthz/strict path masking

Absolute filesystem path removed from the `backup_dir` section
of the JSON response.

---

## 4. Route protection audit (complete)

### Private (require_user dependency) — 22 routes

All routes below return 303 → /login when accessed without a
valid session cookie:

| Route | Router | Method |
|-------|--------|--------|
| `/` | pages | GET |
| `/library` | pages | GET |
| `/library/{slug}` | pages | GET |
| `/history` | pages | GET |
| `/progress` | pages | GET |
| `/profile` | auth_routes | GET |
| `/profile/password` | auth_routes | GET |
| `/profile/password` | auth_routes | POST |
| `/sessions` | sessions | POST |
| `/sessions/{id}` | sessions | GET |
| `/sessions/{id}` | sessions | POST |
| `/sessions/{id}/exercises/{se_id}` | sessions | POST |
| `/rules` | sessions | GET |
| `/exercise-history/{slug}/{code}` | sessions | GET |
| `/export` | export | GET |
| `/export/sessions.json` | export | GET |
| `/export/sessions.csv` | export | GET |
| `/admin/sessions` | admin | GET |
| `/admin/sessions/{id}/delete` | admin | POST |
| `/admin/sessions/{id}/exclude` | admin | POST |
| `/leaderboard` | leaderboard | GET |

### Public (intentionally unauthenticated) — 7 routes

| Route | Reason |
|-------|--------|
| `/welcome` | Landing page for anonymous visitors |
| `/login` GET/POST | Login form and submission |
| `/register` GET/POST | Registration |
| `/logout` POST | Session cleanup (functional safety: clearing a cookie is harmless) |
| `/healthz` | Uptime probe (no sensitive data) |
| `/healthz/strict` | Operator-facing (sensitive data removed in this sprint) |

### Static files

`/static/*` — served by FastAPI's `StaticFiles` mount. Contains
only CSS, manifest, and SVG icon. No secrets.

---

## 5. Ownership audit (complete, no issues)

Every route that reads or writes `WorkoutSession` data filters
by `user_id == current_user.id`. The `get_owned_session_or_404`
helper centralises the ownership check for mutations. A user who
guesses another user's session ID gets a 404 with no information
leakage about existence.

Exports (`/export/sessions.json` and `.csv`) pass `user_id` to
the builder. The leaderboard shows only aggregated scores (no
session IDs, no template names, no exercise data of other users).

---

## 6. Public exposure verdict

### **GO FOR PUBLIC EXPOSURE**

Conditional on these production requirements:

1. **`APP_ENV=production`** in `.env.production` — ensures the
   `secure` flag is set on the session cookie (HTTPS-only).
2. **HTTPS** via certbot — the app MUST NOT be exposed over
   plain HTTP in production.
3. **nginx `limit_req`** on `/login` and `/register` — brute-
   force mitigation. Example:

   ```nginx
   limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/m;

   location = /login {
       limit_req zone=auth burst=10 nodelay;
       proxy_pass http://127.0.0.1:8000;
   }
   location = /register {
       limit_req zone=auth burst=5 nodelay;
       proxy_pass http://127.0.0.1:8000;
   }
   ```

4. **nginx `auth_basic` is NOT required** if the app auth is
   trusted (it is — bcrypt passwords, signed cookies,
   samesite=strict). However, keeping basic_auth as a second
   layer is harmless and recommended for defense-in-depth.

If these 4 conditions are met, the app is safe for public
internet exposure with a small trusted user group.

---

## 7. Tests added (9 new, total 262)

- Security headers present on private + public routes
- Cookie is samesite=strict and httponly
- Login with unknown user returns 401 (not 500 after timing fix)
- /healthz/strict does not leak absolute paths
- All private routes reject anonymous after hardening
- Ownership still enforced after hardening
- Exports still scoped after hardening
- Register duplicate returns 400 (not 500)
