Coviu API
=====================

This repository holds an example of accessing the coviu api from a python client. The example is intended purely for demonstrative purposes and so has been written with the intention of making the HTTP requests that are made as obvious as possible.

In order to run the demo, you'll need your api key and secret, python2 with requests and PyJWT. There is
a makefile that sets up a virtualenv if you have virtualenv installed.

```
make env
```

And to run the demo
```
COVIU_API_KEY=... COVIU_API_KEY_SECRET=... [COVIU_API_ENDPOINT=...] make run
```

Example output.

```
send owner to http://localhost:9000/v1/session/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJybGUiOiJvd25lciIsInVuIjoiRHIuIEphbmUgV2hvIiwiZXhwIjoxNDUwNDEzODkzLCJpbWciOiJodHRwOi8vd3d3LmZpbGxtdXJyYXkuY29tLzIwMC8zMDAiLCJzaWQiOiI2YzFjNDljYS1hOTc0LTQ5NDEtOGI4YS1kOTM2YjY3M2YwZjAiLCJpc3MiOiJhMmExN2ZlYS1hMjBlLTExZTUtYjViZS1iMzJmNmI2ZjUyYmYiLCJydG4iOiJodHRwczovL2Nvdml1LmNvbSIsInJlZiI6IjIyOTFlYjI0LWMwY2MtNDg5OS1hOGQ0LWI4MzU5MDIyZjMwZiIsImVtYWlsIjoiZHIud2hvQGdtYWlsLmNvbSIsIm5iZiI6MTQ1MDQxMDI5M30.4tp62a4jv3NhewlVpypospr6Fp5Wk7hA6HmDL63Btko
send guest to http://localhost:9000/v1/session/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJybGUiOiJndWVzdCIsInVuIjoiSm9lIEd1ZXN0IiwiZXhwIjoxNDUwNDEzODkzLCJpbWciOiJodHRwOi8vd3d3LmZpbGxtdXJyYXkuY29tLzIwMC8zMDAiLCJzaWQiOiI2YzFjNDljYS1hOTc0LTQ5NDEtOGI4YS1kOTM2YjY3M2YwZjAiLCJpc3MiOiJhMmExN2ZlYS1hMjBlLTExZTUtYjViZS1iMzJmNmI2ZjUyYmYiLCJydG4iOiJodHRwczovL2Nvdml1LmNvbSIsInJlZiI6IjIyOTFlYjI0LWMwY2MtNDg5OS1hOGQ0LWI4MzU5MDIyZjMwZiIsIm5iZiI6MTQ1MDQxMDI5M30.AbXcl8L-RAalfeys0otEWnYWBhV0lTKIp78eU_Cbge8

```

## Getting started with the Coviu API.

This document describes how to get up and running quickly with the coviu api. It only includes the most basic operations that allow you to get a user into a call quickly. A complete set of API documents will be made available at a later date.

This document assumes that you have been issued with credentials for accessing the API. The API is currently in closed beta. As we move into production, further documentation will be made available for setting up credentials.

The API endpoint during the beta period is [https://api.covi.io](https://api.covi.io).

### Terminology

Before we start, we need to define a couple of terms that will be used through this document.

* Session - A web (video, audio, data) call on coviu through either a browser, native app, or mobile. Currently sessions may have up to 5 participants.
* Session Owner - The user (person) hosting a session. Controls access to the session.
* Session Guest - A user (person) who has been granted access to a session by the session owner.
* Subscription - A user who has arranged to have access to the system for the purposes of hosting sessions.
* Client - An API consumer (software) making request to access protected resources [rfc6749](https://tools.ietf.org/html/rfc6749#section-1.1).

### Authentication

The coviu API uses a number of flows from OAuth2 [rfc6749](https://tools.ietf.org/html/rfc6749) to provide authentication and later authorization to resources.

#### Getting access

You will have been issued an `api_key` and `api_key_secret`. These are similar to a username and password for various API operations. In order to access the REST API, you will need secure an access token. This can be achieved by following the [OAuth2 Client Credentials Grant](https://tools.ietf.org/html/rfc6749#section-4.4).


```
POST /v1/auth/token
Authorization: Basic Base64(api_key:api_key_secret)
Body: grant_type=client_credentials
Response: 200, application/json;UTF-8
{
  access_token: "acces token ...",
  refresh_token: "refresh token ...",
  expires_in: <access_token ttl>,
  token_type: "Bearer",
  scope: "coviu-enterprise-api"
}
```

Once the ttl on the access token has expired, you'll no longer be able to use it to access the REST API. In this instance you can refresh the access token by using the [refresh_token](https://tools.ietf.org/html/rfc6749#section-6) grant_type.

```
POST /v1/auth/token
Authorization: Basic Base64(api_key:api_key_secret)
Body: grant_type=refresh_token&refresh_token=<refresh_token>
Response: 200, application/json;UTF-8
{
  access_token: "acces token ...",
  refresh_token: "refresh token ...",
  expires_in: <access_token ttl>,
  token_type: "Bearer",
  scope: "coviu-enterprise-api"
}
```

### API Structure

Having recovered an access token, you may now use it to access various resources provided by the api. The Coviu API uses a hypermedia convention based on [HAL](http://stateless.co/hal_specification.html). This minimizes the need for an API consumer to keep track of paths to resources and construct URLs themselves. As such, your first step after recovering an access token is to get the root api resource

```
GET /v1/
Authorization: Bearer <access token ... >
Response: 200; application/json;UTF-8
{
    "content": {
        "active": boolean,
        "orgId": string,
        "clientId": string
    },
    "_links": {
        "org": {
            "href": "/v1/orgs/<org id>"
        },
        "self": {
            "href": "/v1"
        },
        "sessions": {
            "href": "/v1/orgs/<org id>/sessions"
        },
        "subscriptions": {
            "href": "/v1/orgs/<org id>/subscriptions"
        }
    }
}
```

The `_links` object in the response contains urls to the top level resources associated with your organisation.

### Creating subscriptions

By creating a subscription you're giving a user the ability to host sessions on coviu.

```
POST /v1/orgs/<org id>/subscriptions
Authorization: Bearer <access token ...>
Body:
{
  "ref": string,
  "email": string,
  "name": string
}
Response: 200; application/json;UTF-8
{
    "content": {
        "ref": string,
        "name": string,
        "started": number,
        "ended": number,
        "orgId": string,
        "active": boolean,
        "subscriptionId": string,
        "email": string
    },
    "_links": {
        "org": {
            "href": "/v1/orgs/<org id>"
        },
        "self": {
            "href": "/v1/orgs/<org id>/subscriptions/<subscriptionId>"
        }
    }
}
```

You'll notice the existence of both the `ref`, and `subscriptionId`. `subscriptionId` is a unique identifier we generate that is unique across all subscription ever made. It's our internal identifier. ref is an ID set by you that lets you correlate the subscription with objects in your system.  E.g. The user id in your system.

### Create a session

In order to give your users access to a coviu session, you need to generate a session link for that user in the session. This is simply a matter of signing a Json Web Token [JWT](https://tools.ietf.org/html/rfc7519) with an appropriate set of claims for the user. *The JWT must be signed against your `api_key_secret` using the HS256 (HMAC SHA-256) hashing algorithm.*

#### An owner's session link

The JWT for the owner of a session must be signed over the following claims

```
{
    "iss": string - issuer: must be your api_key,
    "un": string - user name: the screen name of their user,
    "ref": string - ref: the reference used for creating the subscription,
    "sid": string - session id: a string identifying the session,
    "img": string - OPTIONAL image: a url of the user's profile picture,
    "email": string - email: the email address of the user,
    "rle": string - role: the role of the user in the call. Must be set to 'owner',
    "rtn": string - OPTIONAL return url: The url to send the user to after the call has finished.,
    "nbf": number - OPTIONAL not before: The epoch timestamp (seconds) that the session may start,
    "exp": number - OPTIONAL expiry: The epoch timestamp (seconds) that the session may end
}
```

#### A guest's session link

The JWT for the guests session must be signed over the following claims

```
{
    "iss": string - issuer: must be your api_key,
    "un": string - user name: the screen name of their user,
    "ref": string - ref: the reference used for creating the subscription of the owner,
    "sid": string - session id: a string identifying the session,
    "img": string - OPTIONAL image: a url of the user's profile picture,
    "rle": string - role: the role of the user in the call. Must be set to 'guest',
    "rtn": string - OPTIONAL return url: The url to send the user to after the call has finished.,
    "nbf": number - OPTIONAL not before: The epoch timestamp (seconds) that the session may start,
    "exp": number - OPTIONAL expiry: The epoch timestamp (seconds) that the session may end
}
```

Having created the JWT, constructing a link to the session is done as follows

```
https://api.covi.io/v1/session/<JWT>
```

Some points to note:

* The session id (`sid`) claim indicates the session. If two tokens have the same `sid` claim, they will be connected into the same session.
* It is not required that you create a session with `sid` before signing the token.
* You don't need to create a new subscription for the guest in a session. Only the owner needs to have a subscription.
* A single subscription may not be used for multiple sessions at the same time. Multiple entries to the same session by a single subscription are allowed.

### Removing a subscription

Removing a subscription means the user may no longer host sessions in coviu.

```
DELETE /v1/orgs/<org id>/subscriptions/<subscriptionId>
Authorization: Bearer <access token ...>
Response: 200; application/json;UTF-8
{
    "content": {
        "ref": string,
        "name": string,
        "started": number,
        "ended": number,
        "orgId": string,
        "active": boolean - false,
        "subscriptionId": string,
        "email": string
    },
    "_links": {
        "org": {
            "href": "/v1/orgs/<org id>"
        },
        "self": {
            "href": "/v1/orgs/<org id>/subscriptions/<subscriptionId>"
        }
    }
}
```

### Get Subscriptions

Subscription are available through the subscriptions collection. Automatic pagination is applied.

```
GET /v1/orgs/<org id>/subscriptions?page=1&count=200
Authorization: Bearer <access token ...>
Response: 200; application/json;UTF-8
{
    "content": [Subscription Resource],
    "_links": {
        "next": {
            "href": "/v1/orgs/<org id>/subscriptions?page=2&count=200"
        },
        "self": {
            "href": "/v1/orgs/<org id>/subscriptions?page=1&count=200"
        },
        "previous": {
            "href": "/v1/orgs/<org id>/subscriptions?page=0&count=200"
        }
    }
}
```

### Get Session Entries

Get pages of session entries. Session entries represent instances of the system granting access to a session.

```
GET /v1/orgs/<org id>/session?page=1&count=200
Authorization: Bearer <access token ...>
Response: 200; application/json;UTF-8
{
    "content": [{
      "content": {
          "name": string,
          "accessToken": string,
          "clientId": string,
          "sessionId": string,
          "orgId": string,
          "entryTime": number,
          "entryId": string,
          "subscriptionId": string,
          "role": string,
          "peerId": string
      },
      "_links": {
          "org": {
              "href": "/v1/orgs/<org id>"
          },
          "self": {
              "href": "/v1/orgs/<org id>/sessions/<session id>"
          },
          "client": {
              "href": "/v1/orgs/<org id>/clients/<client id>"
          },
          "subscription": {
              "href": "/v1/orgs/<org id>/subscriptions/<subscription id>"
          }
      }
    },
    ...],
    "_links": {
        "next": {
            "href": "/v1/orgs/<org id>/subscriptions?page=2&count=200"
        },
        "self": {
            "href": "/v1/orgs/<org id>/subscriptions?page=1&count=200"
        },
        "previous": {
            "href": "/v1/orgs/<org id>/subscriptions?page=0&count=200"
        }
    }
}
```
