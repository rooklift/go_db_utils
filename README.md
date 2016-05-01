# go_db_utils
Some helpers for managing a database of Go games. (Currently I have GoGoD and Go4Go, and use Sabaki as my SGF editor; the scripts here reflect all that, but some minor alterations could be made to tailor it for your use.)

* Create or update a database of the games with `go_db_creator.py` (requires [gofish](https://github.com/fohristiwhirl/gofish))
* Search the database with `searcher.pyw`

Building the database takes quite a while (well, I have 130k files), mostly due to the calculation of a "Dyer signature" for each game, which is used by the searcher for deduplication purposes.

![Searcher Screenshot](/screenshot.png?raw=true)
