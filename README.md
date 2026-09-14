# Graffiti House Project

This repository contains code related to the [NEH-funded planning grant](https://rrchnm.org/news/rrchnm-receives-grant-in-collaboration-with-fairfax-citys-office-of-historic-resources-at-historic-blenheim-and-brandy-station-foundation-for-digitization-of-civil-war-graffiti/) for a collaborative project with the Roy Rosenzweig Center for History and New Media (RRCHNM), Historic Blenheim and the Civil War Interpretive Center (Fairfax City, VA), and the Brandy Station Foundation (Brandy Station, VA).

## Setup

The project requires Python 3.12+, [uv](https://docs.astral.sh/uv/),
Node.js 22+, and PostgreSQL. Create the local configuration and install the
locked Python and frontend dependencies:

```sh
cp .env.example .env
uv sync --group dev --locked
cd theme/static_src && npm ci && cd ../..
```

Create the database named in `.env`, then initialize and run the application:

```sh
uv run python manage.py migrate
uv run python manage.py tailwind build
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
- `make tailwind`: rebuild CSS as source files change.
- `make check`: run Django's system checks.
- `make test`: run the pytest suite.
- `make help`: list all development commands.

Production images install exactly the versions in `uv.lock` and
`theme/static_src/package-lock.json`; update both lockfiles whenever dependency
constraints change.
