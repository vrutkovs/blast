import os
import praw
import random
import sys
import traceback
import kubernetes.client as k8s
from base64 import standard_b64decode
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError


SERVICEACCOUNT_LOCATION = '/var/run/secrets/kubernetes.io/serviceaccount/'
CONFIG_MAP = 'database-params'
PRAW_SECRET = 'praw-secret'
SUBREDDITS = os.getenv('SUBREDDIT') or 'aww'
LIMIT = os.getenv('LIMIT') or 10

def read_file(name):
    """
    Reads configuration from serviceaccounts files.
    """
    with open(SERVICEACCOUNT_LOCATION + name) as f:
        return f.read()

def get_k8s_api():
    """
    Get k8s namespaced API
    """
    # Authenticate using token
    k8s.configuration.host = 'https://{}:{}'.format(
        os.getenv('KUBERNETES_SERVICE_HOST'),
        os.getenv('KUBERNETES_SERVICE_PORT'))
    k8s.configuration.api_key_prefix['authorization'] = 'Bearer'
    k8s.configuration.api_key['authorization'] = read_file('token')
    k8s.configuration.ssl_ca_cert = SERVICEACCOUNT_LOCATION + 'ca.crt'
    return k8s.CoreV1Api()

def read_configmap():
    """
    Reads ConfigMap object storing secrets to databases.
    """
    # Read serviceaccount token
    namespace = read_file('namespace')
    # we're getting database configuration
    k8s_api = get_k8s_api()
    db_configmap = k8s_api.read_namespaced_config_map(CONFIG_MAP, namespace)

    return db_configmap.data['MONGODB_USER'], db_configmap.data['MONGODB_PASSWORD'], \
           db_configmap.data['MONGODB_DATABASE'], \
           os.getenv('DATABASE_SERVICE_HOST'), os.getenv('DATABASE_SERVICE_PORT')

def read_reddit_secret():
    """
    Read PRAW data secret from k8s
    """
    # Read serviceaccount token
    namespace = read_file('namespace')
    k8s_api = get_k8s_api()
    praw_secret = k8s.CoreV1Api().read_namespaced_secret(PRAW_SECRET, namespace)

    # secrets are base64 encoded
    result = {}
    for item in ['client_id', 'client_secret', 'username', 'password']:
        encoded = praw_secret.data.get(item)
        if encoded:
            result[item] = standard_b64decode(encoded).decode('utf-8')

    return result

def get_reddit():
    """
    Creates a PRAW instance based on the client ID and client secret
    """
    secret = read_reddit_secret()
    reddit = praw.Reddit(user_agent='catcatgo_parser', **secret)
    # Verify authentication
    reddit.user.me()
    return reddit

def get_mongo_client(mongodb_params):
    client = MongoClient('mongodb://{user}:{passwd}@{host}:{port}/{db}'
                         .format(**mongodb_params))
    client.server_info()
    return client

def save_item(client, db_name, collection_name, title, url):
    db = client.get_database(db_name)
    collection = db.get_collection(collection_name)
    # Use URL as a key, so that we wouldn't insert duplicates
    key = {'url': url}
    data = {'title': title, 'url': url};
    print("Saving '{}' - {}".format(title, url))
    collection.update(key, data, upsert=True)


if __name__ == '__main__':
    # Read mongo connection config map
    user, passwd, host, port = 'user', 'password', 'localhost', '27017'
    if 'KUBERNETES_SERVICE_HOST' in os.environ:
        try:
            user, passwd, db, host, port = read_configmap()
            mongodb_params={'user': user, 'passwd': passwd, 'host': host, 'port': port, 'db': db}
        except k8s.rest.ApiException as e:
            print("Error reading config map!", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            sys.exit(1)

    # create mongodb client
    mongo_client = get_mongo_client(mongodb_params)

    # Fetch 10 links and store title and url in mongo
    reddit = get_reddit()
    for post in reddit.subreddit(SUBREDDITS).hot(limit=LIMIT):
        save_item(mongo_client, db, 'url', post.title, post.url)
