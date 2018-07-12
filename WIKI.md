Dota Flask Facts
======

## Tech Stack

#### [Flask](http://flask.pocoo.org)
Flask is used as web server, it's clean and easy to control. 

#### [Postgresql](https://www.postgresql.org)
Postgresql is chosen as data storage, links between score, hero and player can be mapped using relations.

#### [Heroku](https://www.heroku.com)
5 free hosting app is awesome.

#### [Foundation](https://foundation.zurb.com/sites.html)
Easy to use mock up html template, and I am tired of twitter bootstrap. :P

Another way to design this system is based on AWS lambda architecture, the good side about this approach is that 
only the logic for API is needed. Of course, the drawback is you are bound to AWS. :( Besides that, database may not 
be the best choice for data storage, as most of the data is for reading and joining between tables is very rare.


## TODO

#### Better automated testing and higher coverage
Testing is always important for software! But to design a good automated testing framework takes time. 

#### Background task to refresh score data
Right now, the system is doing lazy loading, which means, it will find data from database first, if no data is found, 
it will fetch from API. And data is only valid within the same day. A better way will be scheduling a background thread 
/ task to refresh score data.

#### Caching latest score data
Loading from database will be slow when database grows bigger, therefore add a caching layer to always store the latest
score data is a good enhancement as well. 

#### Improve the formulas
The current simple model for comparision and recommendation is linear in a way that only consider player himself
/ herself. Given the fact that dota is a team game, I believe that adding more factors from peers will improve the model.

#### API optimization
leader board needs 5 API calls per player, recommendation needs 4 API calls per player, there is a way to reduce the 
the number of API calls needed. Also, for leader board, paging can be added to support more players within same board.


## API

#### Leader Board

##### HTML example
```bash
curl "http://dota-flask.herokuapp.com/leaderboard?ids=89427480,88553213&sort=o"
```
##### JSON example
```bash
curl -i -H "Accept: application/json" "http://dota-flask.herokuapp.com/leaderboard?ids=89427480,88553213&sort=o"
```

_NOTE: max number of id supported for leader board is 10, 
sort supports 'o' - overall, 'c' - count, 'w' - week, 'y' - year_

##### Open Dota API
* [player api](https://docs.opendota.com/#tag/players%2Fpaths%2F~1players~1%7Baccount_id%7D%2Fget)
* [player win lose api](https://docs.opendota.com/#tag/players%2Fpaths%2F~1players~1%7Baccount_id%7D~1wl%2Fget)

#### Comparision

##### HTML example
```bash
curl "http://dota-flask.herokuapp.com/compare?p1=89427480&p2=88553213"
```
##### JSON example
```bash
curl -i -H "Accept: application/json" "http://dota-flask.herokuapp.com/compare?p1=89427480&p2=88553213"
```

##### Open Dota API
* [player api](https://docs.opendota.com/#tag/players%2Fpaths%2F~1players~1%7Baccount_id%7D%2Fget)
* [player win lose api](https://docs.opendota.com/#tag/players%2Fpaths%2F~1players~1%7Baccount_id%7D~1wl%2Fget)

#### Recommendation

##### HTML example
```bash
curl "http://dota-flask.herokuapp.com/recommend?p=89427480"
```
##### JSON example
```bash
curl -i -H "Accept: application/json" "http://dota-flask.herokuapp.com/recommend?p=89427480"
```

##### Open Dota API
* [player api](https://docs.opendota.com/#tag/players%2Fpaths%2F~1players~1%7Baccount_id%7D%2Fget)
* [player win lose api](https://docs.opendota.com/#tag/players%2Fpaths%2F~1players~1%7Baccount_id%7D~1wl%2Fget)
* [player hero api](https://docs.opendota.com/#tag/players%2Fpaths%2F~1players~1%7Baccount_id%7D~1heroes%2Fget)
* [player hero rankings api](https://docs.opendota.com/#tag/players%2Fpaths%2F~1players~1%7Baccount_id%7D~1rankings%2Fget)
* [heroes api](https://docs.opendota.com/#tag/heroes%2Fpaths%2F~1heroes%2Fget)


## Recommendation Formula

The recommendation formula used is below:
```text
rank_score * 0.5 + normalized_win_score * 0.45 + normalized_last_played_score * 0.05
```

The formula takes account for the case where player has a high win rate on the given hero but a very low number 
of matches played. Besides that, adding the last played time as a factor make the model more relevant to player's 
recent performance.
