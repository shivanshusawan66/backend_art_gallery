# ai-mf-platform

Repo for backend code of AI MF Platform

steps to run locally 

create a pg admin server using the env credentials or create a database named "AIMF" in the current server and change credentials in .env accordingly

change path in django_manage.py to path of ai_mf_platform in your machine

run build-postgres

comment out init.py from line 26-38 of core

python ai_mf_backend/django_manage.py makemigrations ai_mf_backend 

python ai_mf_backend/django_manage.py migrate ai_mf_backend 

build workflow application