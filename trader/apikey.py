
class APIKey:
    def __init__(self, APIkey, secret):
            self.APIkey = APIkey
            self.secret = secret

    def getAPIkey(self):
        return self.APIkey

    def getSecret(self):
        return self.secret
