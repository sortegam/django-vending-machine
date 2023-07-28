up:
	python manage.py runserver

makemigrations:
	python manage.py makemigrations

migrate:
	python manage.py migrate

dbshell:
	python manage.py dbshell
	

collectstatic:
	python manage.py collectstatic