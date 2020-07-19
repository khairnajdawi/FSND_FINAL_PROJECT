import json
from flask import request, _request_ctx_stack,abort,session
from functools import wraps
from jose import jwt
from urllib.request import urlopen
import constants

AUTH0_DOMAIN = 'kj-casting-agency.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'https://kj-casting-system.herukoapp.com'


# AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''


# General AuthError to raise auth error when there is
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Auth Token
def get_auth_token():
    return session[constants.JWT_PAYLOAD]


# check if permissions available in token
# then check requested permission is granted
def check_permissions(permission, payload):
    # if permission is not included in payload,raise auth error with 401 code
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'Invalid Authorization',
            'description': 'Can not check your permission!'
        }, 401)
    # if requested permission is not granted,raise auth error with 403 code
    if permission in payload['permissions']:
        return True
    raise AuthError({
        'code': 'Unauthorized',
        'description': 'You do not have permission to access this page!'
    }, 403)


# verify the provided jwt is valid
def verify_decode_jwt(token):
    # GET THE PUBLIC KEY FROM AUTH0
    jsonurl = urlopen('https://{}/.well-known/jwks.json'.format(AUTH0_DOMAIN))
    jwks = json.loads(jsonurl.read())
    # GET THE DATA IN THE HEADER
    unverified_header = jwt.get_unverified_header(token)
    # CHOOSE OUR KEY
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'Invalid Authorization',
            'description': 'Authorization malformed.'
        }, 401)
    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    # Finally, verify!!!
    if rsa_key:
        try:
            # USE THE KEY TO VALIDATE THE JWT
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )
            return payload
        # catch exception for expired signature error
        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'Login expired!',
                'description': 'Try to login again.'
            }, 401)
        # catch exception for jwt claims error
        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'AuthError',
                'description':
                    'Something went wrong with authentication, please contact your system administrator!'
            }, 401)
        # catch general exception
        except Exception:
            raise AuthError({
                'code': 'Oops',
                'description':
                    'Something went wrong with authentication, please contact your system administrator!'
            }, 400)
    # raise error if no rsa_key    
    raise AuthError({
        'code': 'Oops',
        'description': 'Something went wrong! please try again'
    }, 400)


# wrapper method to use for endpoints to request a speceific permission
def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_auth_token()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)
        return wrapper
    return requires_auth_decorator


# check if required permission is granted
def check_has_permission(permission):
    access_token = get_auth_token()
    payload = verify_decode_jwt(access_token)
    # check if token has permisssions
    if 'permissions' not in payload:
        return False
    # if requested permission is granted,return true
    if permission in payload['permissions']:
        return True
    return False