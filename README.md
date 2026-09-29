# Graffiti House Project

This repository contains code related to the [NEH-funded planning grant](https://rrchnm.org/news/rrchnm-receives-grant-in-collaboration-with-fairfax-citys-office-of-historic-resources-at-historic-blenheim-and-brandy-station-foundation-for-digitization-of-civil-war-graffiti/) for a collaborative project with the Roy Rosenzweig Center for History and New Media (RRCHNM), Historic Blenheim and the Civil War Interpretive Center (Fairfax City, VA), and the Brandy Station Foundation (Brandy Station, VA).

## Setup

The project requires Python 3.12+, [uv](https://docs.astral.sh/uv/), and
PostgreSQL. Create the local configuration and install the locked Python
dependencies:

```sh
cp .env.example .env
uv sync --group dev --locked
```

Create the database named in `.env`, then initialize and run the application:

```sh
uv run python manage.py migrate
uv run python manage.py runserver
```

For a containerized local environment, run `docker compose up --build` instead.

## Connecting to a remote database

`DATABASE_URL` overrides the individual `DB_HOST`, `DB_PORT`, `DB_NAME`,
`DB_USER`, and `DB_PASS` settings. Keep real credentials only in the ignored
`.env` file or your shell environment; never add them to `.env.example`.

For a database that accepts direct TLS connections:

```dotenv
DATABASE_URL=postgresql://readonly_user:percent-encoded-password@db.example.org:5432/graffitihouse?sslmode=require
DATABASE_READ_ONLY=True
DATABASE_ALLOW_MIGRATIONS=False
DB_APPLICATION_NAME=graffitihouse-local
```

When connected to the RRCHNM proxy, use the database's internal hostname in
that URL and skip the SSH-tunnel step, provided the proxy DNS and PostgreSQL
access rules expose it to your account.

If the database is only reachable through an SSH host, start a tunnel in a
separate terminal:

```sh
ssh -N -L 55432:database.internal:5432 your-user@bastion.example.org
```

Then connect a locally-run Django process through the tunnel:

```dotenv
DATABASE_URL=postgresql://readonly_user:percent-encoded-password@127.0.0.1:55432/graffitihouse
DATABASE_READ_ONLY=True
DATABASE_ALLOW_MIGRATIONS=False
```

For Django running inside Docker, use `host.docker.internal` instead of
`127.0.0.1`, and prevent the container startup command from running migrations:

```dotenv
DATABASE_URL=postgresql://readonly_user:percent-encoded-password@host.docker.internal:55432/graffitihouse
DATABASE_READ_ONLY=True
DATABASE_ALLOW_MIGRATIONS=False
RUN_MIGRATIONS=False
```

Use a dedicated read-only PostgreSQL account in addition to
`DATABASE_READ_ONLY=True` whenever possible. The setting is a useful second
guard, but server-side permissions remain the strongest protection. Admin
logins and any other feature that writes sessions or data will not work in
read-only mode.

`manage.py migrate` exits immediately when `DATABASE_ALLOW_MIGRATIONS=False`.
This is independent of read-only mode, so it can also protect a remote account
that needs application-level write access. Keep `RUN_MIGRATIONS=False` as well
when using that database through Compose; the normal deployment process remains
responsible for applying schema changes.

The most common Make targets are:

- `make preview`: start the Django development server.
- `make check`: run Django's system checks.
- `make test`: run the pytest suite.
- `make help`: list all development commands.

Production images install exactly the versions in `uv.lock`; update the
lockfile whenever dependency constraints change.

## Front end

There is no front-end build step. The public site's styles are plain CSS in
`static/css/site.css`, served as a static file; edit it and reload. The file
opens with a table of contents and the class naming convention. The Unfold
admin ships its own styles and does not load this stylesheet.

[Alpine.js](https://alpinejs.dev/) is vendored at `static/js/alpine.min.js`
(currently 3.16.3). To upgrade it, download the new build and commit it:

```sh
curl -fsSL -o static/js/alpine.min.js https://cdn.jsdelivr.net/npm/alpinejs@<version>/dist/cdn.min.js
```

## Public API

The project's public data is available as read-only JSON at `/api/v1/`. No
account or key is needed; only `GET` (plus `HEAD` and `OPTIONS`) is allowed.

- `/api/v1/` lists the endpoints; open it in a browser for a browsable view.
- `/api/v1/docs/` is interactive documentation (Swagger UI), and
  `/api/v1/schema/` is the OpenAPI 3 schema (`?format=json` for JSON).

| Endpoint | Contents | Filters |
| --- | --- | --- |
| `/api/v1/sites/` | Sites, with their location nested, wall and photo counts | `location`, `state`, `tag` |
| `/api/v1/locations/` | Places, with latitude and longitude | `state`, `city` |
| `/api/v1/walls/` | Photographed walls | `site`, `room`, `date_taken_after`, `date_taken_before`, `tag` |
| `/api/v1/photos/` | Graffiti photos cropped from walls | `wall`, `site`, `graffiti_type`, `person`, `tag` |
| `/api/v1/people/` | People, with aliases, organizations, service records, and photos | `governance`, `rank`, `military_branch`, `army_branch`, `photo`, `tag` |

Each endpoint also has a detail view (`/api/v1/walls/<id>/`), accepts
`?search=` (names, identifiers, and similar text fields), and accepts
`?ordering=` with a field name, prefixed by `-` to reverse it. Example:
`/api/v1/walls/?site=4&ordering=-date_taken`.

Lists are paginated: responses have `count`, `next`, `previous`, and
`results`. Pages hold 50 objects by default; `?page_size=` raises that to at
most 500.

Conventions:

- Every object has an `id` and its API `url`; objects with a page on the
  website also have `html_url`. Related objects appear as an id plus a
  `_url` field (`"site": 4, "site_url": "..."`) or as a list of
  `{"id", "url"}` references.
- Choice fields give the stored value and a label, for example
  `"military_rank": "2nd_lieutenant"` and
  `"military_rank_display": "2nd Lieutenant"`. Both are `null` when unset.
- Service records call the stored `military_division` field `army_branch`,
  matching its label in the admin.
- Images are absolute URLs, or `null` when there is no file.
- A photo's `crop` is its rectangle (`x`, `y`, `width`, `height`) in pixels of
  its wall's `image`.
- Wall and photo `description` fields are sanitized HTML. Site descriptions are
  plain text, and person descriptions may contain HTML.

Internal notes, record history, and ancillary sources are not published.
Anonymous clients are rate limited (`API_THROTTLE_RATE`, default
`120/minute`). Browsers on other sites may read the API through CORS; set
`API_CORS_ALLOWED_ORIGINS` to restrict which origins.
