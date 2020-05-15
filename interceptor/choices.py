
ALLOWED_MEHTODS = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']

HTTP_REQUEST_METHODS = tuple((key, key.upper()) for key in ALLOWED_MEHTODS)
