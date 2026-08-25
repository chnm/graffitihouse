preview :
	uv run python3 manage.py runserver

# Compile TailwindCSS
tailwind :
	uv run python3 manage.py tailwind start

mm :
	uv run python3 manage.py makemigrations

migrate :
	uv run python3 manage.py migrate

graph_illustrate :
	uv run python3 manage.py graph_models -a -g -o models.png

.PHONY : preview tailwind graph_illustrate
