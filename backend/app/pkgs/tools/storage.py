from flask import session

def set(key, value):
    session[key] = value
    session.update

def get(key):
    return session[key] if key in session else None

def pop(key):
    session.pop(key)

def clearup():
    session.clear()