# Python library to interface with myTecnoalarm TCS app cloud services

This repo provides code to interface with the cloud services of the "my Tecnoalarm TCS" app.
Funcionality has been reverse-engineered and may not be complete.

## How to install it

`pip install pytcs-tecnoalarm`

## How to use it

To use this library you need to authenticate to the cloud service.

### First login

Open an interactive prompt and run:

```python
from pytcs_tecnoalarm import TCSSession
s = TCSSession()
s.login(email, password)
```

If your account does not have 2 factor authenticator, you will be logged in.
Otherwise, this will throw an `OTPException`

Get the code from your email and run

```python
s.login(email, password, pin)
```

If everything goes right, you will have an authenticated token and app-id to re-use in the future
(does not seem to expire)

extract then with

```python
s.token
s.appid
```

You can also use directly the login.py script, it will handle the OTP and print your Token and App ID

`python login.py`

### Future logins

Simply pass your token and appid when instantiating the session

```python
from pytcs_tecnoalarm import TCSSession
s = TCSSession(token, appid)
```

This will run the `.re_auth()` function that should re-enable the token for immediate use.

The token never changes.
