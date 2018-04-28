import os
import random
import sys
import traceback
import kubernetes.client as k8s

from os.path import getsize
from scrapy.crawler import CrawlerProcess
from spider import DataSpider

WORDS_FILE = 'words.txt'
SERVICEACCOUNT_LOCATION = '/var/run/secrets/kubernetes.io/serviceaccount/'
CONFIG_MAP = 'database-params'

def random_word():
    """
    Reads random word from the attached words.txt file.
    """
    offset = random.randrange(getsize(WORDS_FILE))
    with open(WORDS_FILE) as file:
        file.seek(offset)
        file.readline()
        return file.readline()

def read_file(name):
    """
    Reads configuration from serviceaccounts files.
    """
    with open(SERVICEACCOUNT_LOCATION + name) as f:
        return f.read()

def read_configmap():
    """
    Reads ConfigMap object storing secrets to databases.
    """
    namespace = read_file('namespace')
    k8s.configuration.host = 'https://{}:{}'.format(
        os.getenv('KUBERNETES_SERVICE_HOST'),
        os.getenv('KUBERNETES_SERVICE_PORT'))
    k8s.configuration.api_key_prefix['authorization'] = 'Bearer'
    k8s.configuration.api_key['authorization'] = read_file('token')
    k8s.configuration.ssl_ca_cert = SERVICEACCOUNT_LOCATION + 'ca.crt'
    # we're getting database configuration
    obj = k8s.CoreV1Api().read_namespaced_config_map(CONFIG_MAP, namespace)

    return obj.data['MONGODB_USER'], obj.data['MONGODB_PASSWORD'], obj.data['MONGODB_DATABASE'],\
        os.getenv('DATABASE_SERVICE_HOST'), os.getenv('DATABASE_SERVICE_PORT'),


if __name__ == '__main__':
    user, passwd, host, port = 'user', 'password', 'localhost', '27017'
    if 'KUBERNETES_SERVICE_HOST' in os.environ:
        try:
            user, passwd, db, host, port = read_configmap()
        except k8s.rest.ApiException as e:
            print("Error reading config map!", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
    # create the spider
    word = random_word()
    process = CrawlerProcess()
    process.crawl(DataSpider,
        start_urls=['https://www.google.com/search?q='+word],
        mongodb_params={'user': user, 'passwd': passwd, 'host': host, 'port': port, 'db': db})
    process.start()
