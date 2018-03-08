# API

This repo contains engines, apis, docs and server

- **Current API Version:** 1.0
- **Current Engine Version:** 1.0
- **Current api endpoint path:** /api/v1

## Dev env setup
Setup virtualenv
```
virtualenv venv -p python3
source venv/bin/activate
```

Install dep
```
pip3 install -r requirements.txt
```

Start dev server
```
python3 app.py
```

## Documentation
### V1.0
To see documentation start the server and browse to `http://127.0.0.1:5000/api/v1/docs`

## To Do
- implement user permissions to get rid of static api key and secret
