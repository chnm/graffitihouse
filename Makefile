preview :
	python3 manage.py runserver

graph_illustrate :
	python3 manage.py graph_models -a -g -o models.png

.PHONY : graph_illustrate