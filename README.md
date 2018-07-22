Dota Flask
========================

[![Build Status](https://travis-ci.org/wgx731/dota-flask.svg?branch=master)](https://travis-ci.org/wgx731/dota-flask)

## Idea Source 

[Dota](https://en.wikipedia.org/wiki/Defense_of_the_Ancients) status check :video_game:

![Image Of Dota](https://upload.wikimedia.org/wikipedia/en/4/42/Dota75-loading-screen.png)

## Prerequisite

### Docker (Optional)

* [Download Docker](https://www.docker.com/community-edition#/download)
* [Docker Get Started](https://docs.docker.com/get-started)
* [Docker Documentation](https://docs.docker.com)

### Pipenv

* [Python Installation Guide](http://docs.python-guide.org/en/latest/starting/installation)
* [Pipenv Documentation](https://pipenv.readthedocs.io/en/latest)
* [Pipenv Install Guide](https://pipenv.readthedocs.io/en/latest/basics.html#installing-pipenv)

### Heroku

* [Sign Up](https://www.heroku.com)
* [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
* [Heroku Container Registry](https://devcenter.heroku.com/articles/container-registry-and-runtime)

###### NOTE: heroku app used in docker user guide and pipenv user guide should be different app!

## Docker User Guide

### Build Flask App

* `docker build -t dota-flask -f Dockerfile.local .`
* `docker build -t dota-flask -f Dockerfile .` (only use this command for deployment)

### Database Utils

##### Drop Flask App Local Sqlite Database (One Time Clean Up)

* `docker run -ti --rm -v $PWD/db:/opt/webapp/db dota-flask python drop_db.py`

##### Create Flask App Local Sqlite Database (One Time Setup)

* `docker run -ti --rm -v $PWD/db:/opt/webapp/db dota-flask python create_db.py`

### Run Flask App Test With Coverage

* `docker run -ti --rm -v $PWD:/opt/webapp -v $PWD/db:/opt/webapp/db dota-flask coverage run --source=app tests.py`
* `docker run -ti --rm -v $PWD:/opt/webapp dota-flask coverage report`
* `docker run -ti --rm -v $PWD:/opt/webapp dota-flask coverage html`

### Start Flask App Container

* `docker run -ti --rm -v $PWD/db:/opt/webapp/db --env PORT=5000 -p 5000:5000 dota-flask`

_NOTE:_ stop app using `Ctrl+C`, container will be removed once app is stopped

### Deploy Flask App To Heroku

* `heroku login`
* `heroku container:login`
* `heroku apps --all`
* `heroku apps:create <heroku-docker-app-name>` (only run this command if you haven't created `<heroku-docker-app-name>`)
* `heroku container:push web -a <heroku-docker-app-name>`
* `heroku open -a <heroku-docker-app-name>`
* `heroku logs -a <heroku-docker-app-name>`

### Create Heroku Postgresql Addon (One Time Setup)

* `heroku login`
* `heroku addons -a <heroku-docker-app-name>`
* `heroku addons:create heroku-postgresql:hobby-dev -a <heroku-docker-app-name>` (only run this command if you want to create new postgresql)
* `heroku addons:attach <heroku-app-with-db>::DATABASE -a <heroku-docker-app-name>` (only run this command if you want to use an existing postgresql)
* `heroku pg:promote <heroku-database> -a <heroku-docker-app-name>`

### Drop Heroku Postgresql Database (One Time Clean Up)

* `heroku run python drop_db.py -a <heroku-docker-app-name>`

### Create Heroku Postgresql Database (One Time Setup)

* `heroku run python create_db.py -a <heroku-docker-app-name>`

### Destory Flask App On Heroku

* `heroku container:rm web -a <heroku-docker-app-name>`


### Setup Google Analytics Tracking ID

* `heroku config -a <heroku-docker-app-name>`
* `heroku config:set GTAG_TRACKING_ID=<gtag-tracking-id-for-heroku-docker-app> -a <heroku-docker-app-name>`

### Clean Up Docker Images

* `docker rmi -f $(docker images --filter "dangling=true" -q --no-trunc)`
* `docker rmi -f dota-flask`
* `docker rmi -f registry.heroku.com/<heroku-docker-app-name>/web`

## Pipenv User Guide

### Install Depedencies

* `pipenv install --dev`

### Database Utils

##### Drop Flask App Local Sqlite Database (One Time Clean Up)

* `pipenv run python drop_db.py`

##### Create Flask App Local Sqlite Database (One Time Setup)

* `pipenv run python create_db.py`

### Run Flask App

##### Setup Environment Variable

* Mac / Linux / Git Bash: `export FLASK_APP=app_local.py`
* Windows CMD / Git CMD: `set FLASK_APP=app_local.py`

##### Start Flask App

* `pipenv run flask run`

_NOTE:_ stop app using `Ctrl+C`, use `Git Bash` in Windows

###  Run Flask App Test With Coverage

* `pipenv run coverage run --source=app tests.py`
* `pipenv run coverage report`
* `pipenv run coverage html`

### Deploy Flask App To Heroku

* `heroku login`
* `heroku apps --all`
* `heroku git:remote -a <heroku-normal-app-name>`
* `heroku apps:create <heroku-normal-app-name>` (only run this command if you haven't created `<heroku-normal-app-name>`)
* `git push -f heroku persistent:master`
* `heroku open -a <heroku-normal-app-name>`
* `heroku logs -a <heroku-normal-app-name>`

### Create Heroku Postgresql Addon (One Time Setup)

* `heroku login`
* `heroku addons -a <heroku-normal-app-name>`
* `heroku addons:create heroku-postgresql:hobby-dev -a <heroku-normal-app-name>` (only run this command if you want to create new postgresql)
* `heroku addons:attach <heroku-app-with-db>::DATABASE -a <heroku-normal-app-name>` (only run this command if you want to use an existing postgresql)
* `heroku pg:promote <heroku-database> -a <heroku-normal-app-name>`

### Drop Heroku Postgresql Database (One Time Clean Up)

* `heroku run python drop_db.py -a <heroku-normal-app-name>`

### Create Heroku Postgresql Database (One Time Setup)

* `heroku run python create_db.py -a <heroku-normal-app-name>`


### Setup Google Analytics Tracking ID

* `heroku config -a <heroku-normal-app-name>`
* `heroku config:set GTAG_TRACKING_ID=<gtag-tracking-id-for-heroku-normal-app> -a <heroku-normal-app-name>`

## Contributing

[Pull Requests](https://github.com/wgx731/dota-flask/pulls) are most welcome!

## Thanks

**dota-flask** © 2018+, [@wgx731]. Released under the [MIT](https://github.com/wgx731/dota-flask/blob/master/LICENSE) License.

Authored and maintained by [@wgx731] with help from contributors ([list][contributors]).

> GitHub [@wgx731]

[@wgx731]: https://github.com/wgx731
[contributors]: https://github.com/wgx731/dota-flask/contributors

