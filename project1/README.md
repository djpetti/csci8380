# CSCI 8380 Project 1

This project is a conflict-of-interest checker for academic researchers in CS.

## Installation

To use this app, you will need to have `npm` and `Python` installed.

To install:
```
cd frontend
npm install
cd ..
python deploy.py build -b
```

## Usage

As of yet, there is no web server. To view the frontend,
simply open up `frontend/static/index.html` in your browser.

## Development

The frontend will need to be rebuilt after every modification.
This can be automated using the `deploy.py` script. To rebuild
the frontend, run `python deploy.py build`. If you are in a hurry,
you can also add the `-b` flag to skip formatting and linting.