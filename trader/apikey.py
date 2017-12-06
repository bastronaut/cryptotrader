
class apikey:
    def __init__(self, APIkey, secret):
            self.APIkey = APIkey
            self.secret = secret

    def getkey(self):
        return self.APIkey

    def getsecret(self):
        return self.secret
