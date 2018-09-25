# MySchoolDining API
A Nifty API for MySchoolDining

## About
This project is a Flask web server that fetches, caches, and serves data from MySchoolDining.

It can present data in pure JSON, for a whole week, for different dates, and even human readable text for serving directly to users [(See Siri Shortcut)](#Shortcut)

## Installation

To install, clone the project, and install the requirements

`pip install -r requirements.txt`

Create a `config.json` in the project root directory that looks like the one below
```json
{
  "cache": "$HERE/cache.json",
  "school": "SCHOOL_NAME",
  "menu": "MENU_NAME"
}
```
A config needs to have
* A cache file location, use `$HERE` to represent the directory where the config is in.
* A school name, this is the `school_name` part of `https://myschooldining.com/school_name`
* A menu name, on MySchoolDining, there are different menu types sometimes. Identify the id of the desired menu. Example: The ones at [The New School](https://myschooldining.com/thenewschool) at the time of this writing are Dining Room (diningroom), Summer Camps (summercamps), and Preschool (preschool)

Then, just run Flask

```
export FLASK_APP=menu/app.py
flask run   
```

## API Endpoints

#### `/api`
Returns menu for a specified date
##### Query Args
* `days` (Number): How many days in the future to fetch
* `wordify` (Boolean): Whether to make the text human readable (true), or JSON (false)

#### `/week`
Returns menu for current week in JSON

## Shortcut
Want to ask Siri for the menu? (iOS 12 only)

Download the Shortcut [here](https://www.icloud.com/shortcuts/7a5784c83c444a80b69bb04efc16a89d)