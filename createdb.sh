#sudo -u postgres dropdb hiryu
#sudo -u postgres createdb -O hiryu hiryu
#rm -rf Hiryu/migrations
python manage.py makemigrations Hiryu
python manage.py migrate
ls Hiryu/fixtures/ | while read line
do
    python manage.py loaddata Hiryu/fixtures/"$line"/*
done
python manage.py createsuperuser
