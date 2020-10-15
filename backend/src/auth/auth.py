import json
from jose import jwt
from urllib.request import urlopen
from flask import request, abort
from functools import wraps

# Configuration
AUTH0_DOMAIN = 'dev-hassanien.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'drink'


# AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Auth Header


def get_token_auth_header():
    # Checking the authorization is available in tge request header
    if 'Authorization' not in request.headers:
        raise AuthError({
            'code': 'No header detected',
            'description': 'Authorization is missing.'
        }, 401)
    # Getting the token from the request header
    token_str = request.headers['Authorization']
    token_str_to_arr = token_str.split(" ")
    # Checking if the data in the header data follows 'Authorization: bearer token' format
    if len(token_str_to_arr) != 2 or token_str_to_arr[0].lower() != "bearer" or token_str_to_arr[1].strip() == "":
        raise AuthError({
            'code': 'header malformed',
            'description': 'header data (bearer token) is malformed.'
        }, 401)
    # Returning the token in its string representation
    token_to_return = token_str_to_arr[1]
    return token_to_return


def check_permissions(permission, payload):
    # Checking if 'permission' key is in the payload
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'bad payload',
            'description': 'payload doesn\'t have permissions array'
        }, 400)
    # Checking if the client can preform that action
    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'forbidden',
            'description': 'permission provided can\'t do that action'
        }, 403)
    # Return True to indicate the client can preform that action
    return True


# Note that method was provided in the course
def verify_decode_jwt(token):
    # Get public key from Auth0
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    # Get the data in the header
    unverified_header = jwt.get_unverified_header(token)
    # Auth0 token should have a key id
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed'
        }, 401)
    rsa_key = {}
    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
            break
    # verify the token
    if rsa_key:
        try:
            # Validate the token using the rsa_key
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer=f'https://{AUTH0_DOMAIN}/'
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)
        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, '
                'check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
        'code': 'invalid_header',
        'description': 'Unable to find the appropriate key.'
    }, 400)


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            payload = None
            try:
                token = get_token_auth_header()
                payload = verify_decode_jwt(token)
                check_permissions(permission, payload)
            except AuthError as err:
                abort(err.status_code)
            return f(payload, *args, **kwargs)
        return wrapper
    return requires_auth_decorator
