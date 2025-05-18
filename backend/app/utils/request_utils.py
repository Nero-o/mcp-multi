from flask import request

def get_client_ip(req):
    if req.headers.getlist("X-Forwarded-For"):
        return req.headers.getlist("X-Forwarded-For")[0]
    return req.remote_addr

def get_user_agent(req):
    return req.headers.get('User-Agent')