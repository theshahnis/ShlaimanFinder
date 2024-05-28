# ShlaimanFinder
never lose your Shlaiman again! - a RPi application to find Shlaiman during concerts and festivals.

Installation:

1.clone the repo
git clone https://github.com/theshahnis/ShlaimanFinder
cd ShlaimanFinder

2.create venv under /ShlaimanFinder/
python3 -m venv venv
source venv/bin/activate

pip install Flask Flask-SQLAlchemy Flask-Login passlib Flask-Mail Flask-Migrate

3. create another cli and under backend repo run
python run.py

over frontend folder , run
npm start
