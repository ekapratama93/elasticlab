import json
import multiprocessing
import requests
from datetime import datetime
from elasticsearch import Elasticsearch
from joblib import Parallel, delayed
from requests.adapters import HTTPAdapter
from tqdm import tqdm
from urllib3.util import Retry

es = Elasticsearch(["localhost"], http_compress=True)
pool = multiprocessing.Pool(8)
num_cores = multiprocessing.cpu_count()


def search_article():
    res = es.search(
        index="kurio_engine",
        doc_type="article",
        body={"query":{"bool":{"must":[{"multi_match":{"query":"jokowi","fields": ["title","content","excerpt"]}}]}}}
    )
    for doc in res['hits']['hits']:
        print("%s" % (doc['_id']))

def insert_articles():
    articles = load_articles()
    for article in articles:
        res = es.index(index="kurio_engine", doc_type='article', id=article['id'], body=article)
        print(res['result'])

def load_articles():
    with open('source/article.json', 'r') as f:
        articles = []
        for line in f:
            articles.append(json.loads(line)['_source'])
    return articles

def transform_article():
    articles = load_articles()
    new_articles = []
    articles_bar = tqdm(articles[:3])
    for article in articles_bar:
        if 'entity_ids' in article and type(article['entity_ids']) is list and len(article['entity_ids']) > 0:
            # entities = [resolve_entity(e) for e in article['entity_ids']]
            entities = Parallel(n_jobs=num_cores)(delayed(resolve_entity)(e) for e in article['entity_ids'])
            article['entity_ids'] = entities
        if 'topic_ids' in article and type(article['topic_ids']) is list and len(article['topic_ids']) > 0:
            # topic = [resolve_topic(e) for e in article['topic_ids']]
            topic = Parallel(n_jobs=num_cores)(delayed(resolve_topic)(e) for e in article['topic_ids'])
            article['topic_ids'] = topic
        if 'location_ids' in article and type(article['location_ids']) is list and len(article['location_ids']) > 0:
            # location = [resolve_location(e) for e in article['location_ids']]
            location = Parallel(n_jobs=num_cores)(delayed(resolve_location)(e) for e in article['location_ids'])
            article['location_ids'] = location
        if 'source_ids' in article and type(article['source_ids']) is list and len(article['source_ids']) > 0:
            # source = [resolve_source(e) for e in article['source_ids']]
            source = Parallel(n_jobs=num_cores)(delayed(resolve_source)(e) for e in article['source_ids'])
            article['source_ids'] = source
        articles_bar.set_description("id : %s" % article['id'])
        new_articles.append(article)
    with open('source/ready_article.json','w') as f:
        for article in new_articles:
            f.write(json.dumps(article)+"\n")

def resolve_entity(entity_id):
    response = requests_retry_session().get("http://entity.kurioapps.com/v0/entities/{}".format(entity_id))
    if response.status_code == 200:
        return json.loads(response.text)['name']
    else:
        return None

def resolve_topic(topic_id):
    response = requests_retry_session().get("http://category.kurioapps.com/category/{}".format(topic_id))
    if response.status_code == 200:
        return json.loads(response.text)['name']
    else:
        return None

def resolve_location(location_id):
    response = requests_retry_session().get("https://locus.kurioapps.com/v1/locations/{}".format(location_id))
    if response.status_code == 200:
        return json.loads(response.text)['name']
    else:
        return None

def resolve_source(source_id):
    response = requests_retry_session().get("http://kurnlb-222-027b2b9263103f2b.elb.ap-southeast-1.amazonaws.com/feed/{}".format(source_id))
    if response.status_code == 200:
        return json.loads(response.text)['name']
    else:
        return None

def requests_retry_session(
    retries=10,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


if __name__ == "__main__":
    # insert_article()
    # search_article()
    transform_article()
