sudo -u postgres dropdb hiryu
sudo -u postgres createdb -O hiryu hiryu
rm -rf Hiryu/migrations
python manage.py makemigrations Hiryu
python manage.py migrate
#python manage.py loaddata Hiryu/fixtures/*
python manage.py createsuperuser
