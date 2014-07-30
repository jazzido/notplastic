import json, urllib, urllib2

from flask import Blueprint, jsonify, current_app, request, abort, session, redirect, url_for

from notplastic import db, utils, csrf

mod = Blueprint('auth0', __name__, url_prefix='/auth0')

@mod.route('/callback', methods=['GET'])
def callback():
    code = request.args.get("code")

    base_url = "https://{domain}".format(domain=current_app.config['AUTH0_DOMAIN'])
    data = urllib.urlencode([('client_id', current_app.config['AUTH0_CLIENT_ID']),
                             ('redirect_uri', url_for('.callback', _external=True)),
                             ('client_secret', current_app.config['AUTH0_CLIENT_SECRET']),
                             ('code', code),
                             ('grant_type', 'authorization_code')])

    req = urllib2.Request(base_url + "/oauth/token", data)
    response = urllib2.urlopen(req)
    oauth = json.loads(response.read())
    userinfo = base_url + "/userinfo?access_token=" + oauth['access_token']

    response = urllib2.urlopen(userinfo)
    profile = response.read()

    ## store profile in session
    session['profile'] = profile

    redirect("/")
