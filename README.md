# EPF MD • Web Programming Lab 2

## Outline

This project is a demonstration of web programming principles:

- language: Python
- main technology: FastAPI
- technical magic: CRUD operations in SQLite DB and template rendering

## Subject

A virtual specialty coffeshop website

## Setup

Create a virtual environmnent.

On UNIX core :

```
# Create a virtual environment
python3 -m venv env
# Activate virtual environment
source env/bin/activate
# Install dependencies
pip install -r requirements.txt
```

To run the app locally:

```
fastapi dev
```

## Deployment

> Adjusted from original source: https://testdriven.io/blog/fastapi-htmx/

Create a Render account, go ahead and make one. It's free.

Then, create a new Web Service on the free tier. You can choose to manually specify this public repository or connect your GitHub account directly to Render (if you have forked this repository for instance). Render automatically picks up the `pip install -r requirements.txt` command but we need to specify the command for starting our app.

Render by default expects the port to be bound to `10000`. By default, FastAPI binds to port `8000`, but we're able to use the `$PORT` environment variable to let Render handle it:

```
$ fastapi run main.py --port $PORT
```

With this done, we're able to get our web app deployed. It might take a few minutes for it to fully deploy and accept traffic, so if you're impatient you can view the already deployed instance at https://fastapi-coffee-lab.onrender.com.
