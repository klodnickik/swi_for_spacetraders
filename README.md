# Simple Web Interface for StarTraders API

This is UI for API of game https://spacetraders.io/.
The application will be hosted publicly, after implementing login functionality.



## Planned modifications

### minor changes
- block checking market and transfer during transfer
- include information about units in cargo on marketplace page
- protect field with number of units on marketplace and transfer pages
- format inventory on status page
- add information about location for each ship location (on status page)
- activate support for survey
- support for jumps between systems

### major changes
- login screen
- registartion of new agent / deleting the previous account
- automation of tasks, probably will require database support

## instalation

I recommend to use virtual environemnt.

`python3 -m venv venv`
`source venv/bin/activate`

`pip install -r requriments.txt`

Start web service
`flask --app swist_web run --host 0.0.0.0 --debug`