import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen


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


# Auth Header
def get_token_auth_header():
    # check if Authorization is included in request header
    # if not, then raise auth error with 401 code
    if 'Authorization' not in request.headers:
        raise AuthError({
            'code': 'Invalid header',
            'description': 'Invalid Authorization Header'
        }, 401)

    # read Authorization from request header
    auth_header = request.headers['Authorization']
    header_parts = auth_header.split(' ')
    # Auth header must have 2 parts, Barear and token seperated by single space
    # check if split returns two parts
    if(len(header_parts) != 2):
        raise AuthError({
            'code': 'Invalid header',
            'description': 'Invalid Authorization Header'
        }, 401)
    # check the first parts is bearer
    elif header_parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'Invalid header',
            'description': 'Invalid Authorization Header'
        }, 401)
    return header_parts[1]


# check if permissions available in token
# then check requested permission is granted
def check_permissions(permission, payload):
    # if permission is not included in payload,raise auth error with 401 code
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid claims',
            'description': 'permissions not included in JWT'
        }, 401)
    # if requested permission is not granted,raise auth error with 403 code
    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'Unauthorized',
            'description': 'permission not found'
        }, 403)
    return True


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
            'code': 'invalid_header',
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
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)
        # catch exception for jwt claims error
        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description':
                    'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        # catch general exception
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    # raise error if no rsa_key
    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)


# wrapper method to use for endpoints to request a speceific permission
def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)
        return wrapper
    return requires_auth_decorator
