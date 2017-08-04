# AlbionStatus scraper and bot

This part of https://albionstatus.com is responsible for fetching the server status and pushing it (roughly every minute) into a MySQL database.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.
See deployment for notes on how to deploy the project on a live system.

Be sure to look into the repositories of the other parts of AlbionStatus:
* [The microservice](https://github.com/manniL/albionstatus-microservice)
* [The website](https://github.com/manniL/albionstatus-webstei)


### Prerequisites

To install the microservice on your machine, you'll need:

* Python **3!!** (sorry, no 2.x support here)
* [Pip](https://github.com/pypa/pip)
* A MySQL database for the status information
* The [MySQL Python connector](https://dev.mysql.com/downloads/connector/python/)
* Credentials for the Twitter API

Okay, you got these? Great, let's continue!

### Installing

1. Pull the application and switch to the correct branch (mostly `develop`, or `master` if you want to deploy)
2. Get all dependencies by using `pip -r requirements.txt` in the projects root folder
3. Grab a copy of the config.example.json file, enter the needed information
and save it as config.json
4. If you are ready to fetch data, use `python3 albionstatus.py` to start the scraper and bot

Here you go! You may like to use tools like *supervisor* to ensure that the script runs 24/7

## Deployment

Deployment works similar to installation. Just go for `master` instead of `develop`.

## Possible errors and there solutions

None known by now

## Built With

* [Pip](https://github.com/pypa/pip) - Dependency
management
* [Requests](https://github.com/requests/requests/) - Nice HTTP lib for Python
* [MySQL Python connector](https://dev.mysql.com/downloads/connector/python/)


## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, take a look in [our repository](https://github.com/manniL/albionstatus-scraper-bot).

## Authors

* **Alexander Lichter** - *Main work on the project* - [Website](http://developmint.de) - [BitBucket](https://bitbucket.org/manniL/) - [Github](https://github.com/manniL) - [StackOverflow](http://stackoverflow.com/users/3975480/mannil)

See also the [list of contributors](https://github.com/manniL/albionstatus-scraper-bot/contributors) who participated in this project.

## License

See [LICENSE file](https://github.com/manniL/albionstatus-scraper-bot/blob/master/LICENSE)