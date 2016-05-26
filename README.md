# go_db_utils
Some helpers for managing a database of Go games. (Currently I have GoGoD and Go4Go, and use Sabaki as my SGF editor; the scripts here reflect all that, but some minor alterations could be made to tailor it for your use.) These things require [gofish](https://github.com/fohristiwhirl/gofish).

* Create or update a database of the games with `updater.py`
* Search the database with `searcher.pyw`

Building the database takes quite a while (well, I have 140k files), mostly due to the calculation of a "Dyer signature" for each game, which is used by the searcher for deduplication purposes.

![Searcher Screenshot](/screenshot.png?raw=true)
