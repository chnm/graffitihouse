# Graffiti House Project

This repository contains code related to the [NEH-funded planning grant](https://rrchnm.org/news/rrchnm-receives-grant-in-collaboration-with-fairfax-citys-office-of-historic-resources-at-historic-blenheim-and-brandy-station-foundation-for-digitization-of-civil-war-graffiti/) for a collaborative project with the Roy Rosenzweig Center for History and New Media (RRCHNM), Historic Blenheim and the Civil War Interpretive Center (Fairfax City, VA), and the Brandy Station Foundation (Brandy Station, VA).

## Setup 

The project uses [Poetry](https://python-poetry.org/docs/basic-usage/) for dependency and package management. To create your Django environment, navigate to the root (cloned) directory and do the following: 

```sh
% cd graffitihouse
% poetry install
% poetry shell
```

When you're done doing active work on Django, don't forget to deactivate your virtual environment. 

```sh
% exit
```

Running `manage.py` will require prepending poetry to the commands, like so: 

```sh
poetry run python manage.py migrate
poetry run python manage.py tailwind build
poetry run python manage.py runserver
```

A Makefile exists to make life a little more convenient. The common commands are: 

- `make preview`: preview the site locally; this runs `poetry run python manage.py runserver`.
- `make tailwind`: compile the CSS; this runs `poetry run python manage.py tailwind start` and will reload the browser anytime updates happen.