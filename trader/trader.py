import importlib
key = importlib.import_module('apikey')
polo = importlib.import_module('api')
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("k", help="api key")
parser.add_argument("s", help="api secret")



def main():
    args = parser.parse_args()
    apikey = key.APIKey(args.k, args.s)
    print apikey.getAPIkey()

if __name__ == "__main__":
    main()
