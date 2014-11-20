installing:
==

make sure devDependencies are installed globally.

run "npm install" to install javascript dependencies.

run "pip3 install -r requirements" to install python dependencies.


running a server
==

enable python virtual environment: source env/bin/activate

python server: python3 innovationday.py

javascript compiler: watchify -v -t reactify innovationday.react.js -o static/js/bundle.js


useful links
==

http://flask.pocoo.org/docs/0.10/

http://docs.sqlalchemy.org/en/rel_0_9/

build status
==
[![Build Status](http://jenkins.colingalindo.ddns.us/buildStatus/icon?job=cs3398Server)](http://jenkins.colingalindo.ddns.us/job/cs3398Server/)
