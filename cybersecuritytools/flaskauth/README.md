# Flask auth

This module contains a bunch of helper functions and route 
decorators for implementing access control in flask.

## static_site_wrapper_app.py

This is primarily aimed at adding access control to a 
static site which has already been generated.  

Access is managed by creating an `access-control.json` file 
in the root of the static site and setting rules as follows:  

```
{
  "paths": {
    "/index.html": {
      "open_access": true
    },
    "/function-x": {
      "message": "You need to be granted one of the function-x-roles",
      "open_access": false,
      "require_any": ["function-x-role-1", "function-x-role-2"]
    },
    "/team-y": {
      "message": "You need to be granted the team-y role.",
      "open_access": false,
      "require_any": ["team-y"]
    },
    "/team-y/function-x": {
      "message": "You need to be granted both the team-y and function-x roles.",
      "open_access": false,
      "require_all": ["team-y", "function-x"]
    }
  }
}
```

This means that the rules governing access are kept alongside 
the static site content not separate from it.

The static site is then wrapped in a simple python flask app 
which implements an `@auth.authorize_static(app)` decorator 
on the static content route. 

## auth.py 

The decorator retrieves the static content, injects a login 
component, implements the access rules and where necessary 
replaces the `<main>` tag content with an access denied 
template.  

In addition to `@auth.authorize_static(app)` there are also 
decorators for use in more conventional flask apps which 
implement the same access controls. 

## alb.py 

There are also some helper functions for handling OIDC 
authentication delegated to an AWS load balancer using 
JWTs. 


