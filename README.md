# Graffiti House Project

This repository contains code related to the [NEH-funded planning grant](https://rrchnm.org/news/rrchnm-receives-grant-in-collaboration-with-fairfax-citys-office-of-historic-resources-at-historic-blenheim-and-brandy-station-foundation-for-digitization-of-civil-war-graffiti/) for a collaborative project with the Roy Rosenzweig Center for History and New Media (RRCHNM), Historic Blenheim and the Civil War Interpretive Center (Fairfax City, VA), and the Brandy Station Foundation (Brandy Station, VA).

## Setup

The project uses [uv](https://docs.astral.sh/uv/) for dependency and package management. To create your Django environment, navigate to the root (cloned) directory and do the following:

```sh
cd graffitihouse
uv sync
```

Running `manage.py` will require prepending uv to the commands, like so:

```sh
uv run python manage.py migrate
uv run python manage.py tailwind build
uv run python manage.py runserver
```

A Makefile exists to make life a little more convenient. The common commands are:

- `make preview`: preview the site locally; this runs `uv run python manage.py runserver`.
- `make tailwind`: compile the CSS; this runs `uv run python manage.py tailwind start` and will reload the browser anytime updates happen.
