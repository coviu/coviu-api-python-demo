'''
    Demonstration of using the coviu REST API.
    Author: Briely Marum <briley.marum@nicta.com.au>
    Date: 18 Dec 2015
    Copyright: NICTA 2016 MIT license.
'''

import requests
import json
import jwt
import base64
import time
import uuid
import os

endpoint = os.getenv('COVIU_API_ENDPOINT', "https://api.covi.io")
api_key = os.environ.get('COVIU_API_KEY')
api_key_secret = os.environ.get('COVIU_API_KEY_SECRET')

def build_auth_headers(api_key, api_key_secret):
    '''
    Construct the HTTP Basic Auth header. Notice that requests takes an 'auth'. This
    included purely for the purposes of the demonstration.
    '''
    return {"Authorization": "Basic " + base64.b64encode(api_key + ":" + api_key_secret)}

def build_oauth2_auth_header(access_token):
    '''
    Construct the OAuth2 bearer token authorization header from an access token.
    It's possible that requests can do this too. I haven't really checked.
    '''
    return {"Authorization": "Bearer " + access_token}

def get_access_token():
    '''
    Use the api_key and api_key_secret to get an access token and refresh token for the api client.
    '''
    return requests.post(endpoint + "/v1/auth/token",
    data={"grant_type": "client_credentials"},
    headers=build_auth_headers(api_key, api_key_secret)).json()

def refresh_access_token(refresh_token):
    '''
    Use the api_key and api_key_secret along with a previous refresh token to refresh an
    access token, returning a new grant with access token and refresh token.
    '''
    return requests.post(endpoint + "/v1/auth/token",
                         data={"grant_type": "refresh_token", "refresh_token": refresh_token},
                         headers=build_auth_headers(api_key, api_key_secret)).json()

def get_api_root(access_token):
    '''
    Get the API root resource that includes links to our organisation's collections.
    '''
    return requests.get(endpoint + "/v1/", headers=build_oauth2_auth_header(access_token)).json()

def create_subscription(access_token, api_root, body):
    '''
    Create a new subscription for a user. We need to create a subscription before we sign a session jwt
    for the user, otherwise coviu will rudely deny access to the session.
    '''
    headers = build_oauth2_auth_header(access_token)
    headers['Content-Type']  = 'application/json' # not needed in later versions of requests
    return requests.post(endpoint  + api_root['_links']['subscriptions']['href'],
                         headers=headers,
                         data=json.dumps(body)).json()

def get_subscriptions(access_token, api_root):
    '''
    Get the first page of subscriptions, leaving the API to choose how many to return.
    '''
    return requests.get(endpoint + api_root['_links']['subscriptions']['href'],
                        headers=build_oauth2_auth_header(access_token)).json()

def get_sessions(access_token, api_root):
    '''
    Get the first page of sessions, leaving the API to choose how many to return.
    '''
    return requests.get(endpoint + api_root['_links']['sessions']['href'],
                        headers=build_oauth2_auth_header(access_token)).json()

def get_link(access_token, page):
    '''
    Get a resource identified by HAL link object.
    '''
    return requests.get(endpoint + page['href'], headers=build_oauth2_auth_header(access_token)).json()

def delete_subscription(access_token, subscription):
    '''
    Delete a previously created subscription.
    '''
    return requests.delete(endpoint + subscription['_links']['self']['href'],
                           headers=build_oauth2_auth_header(access_token)).json()

# Recover an access token using our
grant = get_access_token()

# Refresh an access token before grant['expires_in'] has expired.
grant = refresh_access_token(grant['refresh_token'])

# Get the root of the api
api_root = get_api_root(grant['access_token'])

# # # Create a new subscription for one of your users
subscription_ref = str(uuid.uuid4())
subscription = create_subscription(grant['access_token'],
                                   api_root, {
                                    'ref': subscription_ref,
                                    'name': 'Dr. Jane Who',
                                    'email': 'test@test.com'
                                    })

# Get a page of sessions for
sessions = get_sessions(grant['access_token'], api_root)

# Get the first page of subscriptions
subscriptions = get_subscriptions(grant['access_token'], api_root)

# Get all sessions for that subscription
for sub in subscriptions['content']:
    get_link(grant['access_token'], sub['_links']['sessions'])

# Get the entire set of subscriptions traversing forward
while 'next' in subscriptions['_links']:
    subscriptions = get_link(grant['access_token'], subscriptions['_links']['next'])

# Get the entire set of subscriptions traversing backwards
while 'previous' in subscriptions['_links']:
    subscriptions = get_link(grant['access_token'], subscriptions['_links']['previous'])

# delete the subscription we created. Don't do this if you want your user to access coviu.
delete_subscription(grant['access_token'], subscription)

# generate a random string for the session Id. This only needs to be known to the participants.
sessionId = str(uuid.uuid4())

# Sign a jwt for the owner of the subscription. This lets them into the call straight away.
owner = jwt.encode({
    'iss': api_key,
    'un': 'Dr. Jane Who',
    'ref': subscription_ref,
    'sid': sessionId,
    'img': 'http://www.fillmurray.com/200/300',
    'email': 'dr.who@gmail.com',
    'rle': 'owner',
    'rtn': 'https://coviu.com',
    'nbf': int(time.time()),
    'exp': int(time.time()) + 60*60
}, api_key_secret, algorithm='HS256')

# Sign a jwt for the guest of the owner. This gets them to the right spot, but they still need to be
# let into the call by the owner of a session.
guest = jwt.encode({
    'iss': api_key,
    'un': 'Joe Guest',
    'ref': subscription_ref,
    'sid': sessionId,
    'img': 'http://www.fillmurray.com/200/300',
    'rle': 'guest',
    'rtn': 'https://coviu.com',
    'nbf': int(time.time()),
    'exp': int(time.time()) + 60*60
}, api_key_secret, algorithm='HS256')


print "send owner to " + endpoint + "/v1/session/" + owner
print "send guest to " + endpoint + "/v1/session/" + guest
