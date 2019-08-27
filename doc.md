### Create Mapping Search
```
curl -X PUT \
  http://localhost:9200/kurio_engine \
  -H 'Content-Type: application/json' \
  -d '{
	"settings": {
		"number_of_shards": 1,
		"analysis": {
			"analyzer": {
				"kurio_analyzer": {
					"filter": ["lowercase", "kurio_stopwords", "kurio_stemmer_id", "kurio_stemmer_en"],
					"char_filter": ["html_strip", "url_pattern"],
					"type": "custom",
					"tokenizer": "kurio_tokenizer"
				}
			},
			"tokenizer": {
				"kurio_tokenizer": {
					"token_chars": ["letter", "digit", "punctuation"],
					"min_gram": "3",
					"type": "ngram",
					"max_gram": "3"
				}
			},
			"filter": {
				"kurio_stemmer_en": {
					"name": "english",
					"type": "stemmer"
				},
				"kurio_stemmer_id": {
					"name": "indonesian",
					"type": "stemmer"
				},
				"kurio_stopwords": {
					"type": "stop",
					"stopwords": ["_indonesian_", "_english_"]
				}
			},
			"char_filter": {
				"url_pattern": {
					"pattern": "((https?|ftp|gopher|telnet|file|Unsure|http):((/)|())+[wd:#@%/;$()~_?+-=.&]*)",
					"type": "pattern_replace",
					"replacement": " "
				}
			}
		}
	},
	"mappings": {
		"article": {
			"_all": {
				"enabled": false
			},
			"properties": {
				"content": {
					"type": "text",
					"analyzer": "kurio_analyzer"
				},
				"created_at": {
					"type": "long"
				},
				"curated": {
					"type": "long",
					"index": false
				},
				"curated_at": {
					"type": "long"
				},
				"curated_by": {
					"type": "long",
					"index": false
				},
				"deleted": {
					"type": "boolean",
					"index": false
				},
				"deleted_at": {
					"type": "boolean",
					"index": false
				},
				"entity_ids": {
					"type": "keyword"
				},
				"excerpt": {
					"type": "text",
					"analyzer": "kurio_analyzer"
				},
				"full_url": {
					"type": "keyword"
				},
				"id": {
					"type": "long"
				},
				"inappropriate": {
					"type": "boolean"
				},
				"json": {
					"type": "text",
					"index": false
				},
				"location_ids": {
					"type": "integer"
				},
				"pinned": {
					"type": "long",
					"index": false
				},
				"pinned_until": {
					"type": "boolean",
					"index": false
				},
				"published_at": {
					"type": "long"
				},
				"source_ids": {
					"type": "integer"
				},
				"thumbnail": {
					"type": "keyword"
				},
				"thumbnail_dimension": {
					"type": "keyword",
					"index": false
				},
				"thumbnails": {
                    "type": "nested"
				},
				"title": {
					"type": "text",
					"analyzer": "kurio_analyzer",
					"boost": 2.0
				},
				"topic_ids": {
					"type": "integer"
				},
				"updated_at": {
					"type": "long"
				},
				"url": {
					"type": "keyword"
				}
			}
		}
	}
}'
```

### Template MultiMatch Search
```
curl -X POST \
  http://localhost:9200/_scripts/multi-match \
  -H 'Content-Type: application/json' \
  -d '{
    "script": {
        "lang": "mustache",
        "source": {
        	"from": "{{ from }}",
        	"size": "{{ size }}",
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": "{{ keyword }}",
                                "fields": [
                                    "title",
                                    "content",
                                    "excerpt"
                                ]
                            }
                        }
                    ]
                }
            },
            "sort": [
                "_score",
                {
                    "published_at": "desc"
                }
            ]
        }
    }
}'
```

To Query:
```
curl -X GET \
  'http://localhost:9200/kurio_engine/article/_search/template?size=6' \
  -H 'Content-Type: application/json' \
  -d '{
	"id": "multi-match",
	"params": {
		"keyword": "jokowi",
		"from": 0,
		"size": 5
	}
}'
```

### Template Query String
```
curl -X POST \
  http://localhost:9200/_scripts/query-string \
  -H 'Content-Type: application/json' \
  -d '{
    "script": {
        "lang": "mustache",
        "source": {
        	"from": "{{ from }}",
        	"size": "{{ size }}",
            "query": {
                "bool": {
                    "must": [
                        {
                            "query_string": {
                                "query": "{{ keyword }}",
                                "fields": [
                                    "title",
                                    "content",
                                    "excerpt"
                                ]
                            }
                        }
                    ]
                }
            },
            "sort": [
                "_score",
                {
                    "published_at": "desc"
                }
            ]
        }
    }
}'
```

To Query:
```
curl -X GET \
  http://localhost:9200/kurio_engine/article/_search/template \
  -H 'Content-Type: application/json' \
  -d '{
	"id": "query-string",
	"params": {
		"keyword": "jokowi AND jakarta",
		"from": 0,
		"size": 5
	}
}'
```

for Simple Query String:
```
curl -X POST \
  http://localhost:9200/_scripts/simple-query-string \
  -H 'Content-Type: application/json' \
  -d '{
    "script": {
        "lang": "mustache",
        "source": {
        	"from": "{{ from }}",
        	"size": "{{ size }}",
            "query": {
                "bool": {
                    "must": [
                        {
                            "simple_query_string": {
                                "query": "{{ keyword }}",
                                "fields": [
                                    "title",
                                    "content",
                                    "excerpt"
                                ]
                            }
                        }
                    ]
                }
            },
            "sort": [
                "_score",
                {
                    "published_at": "desc"
                }
            ]
        }
    }
}'
```

To Query:
```
curl -X GET \
  http://localhost:9200/kurio_engine/article/_search/template \
  -H 'Content-Type: application/json' \
  -d '{
	"id": "simple-query-string",
	"params": {
		"keyword": "(jokowi) + presiden -debat",
		"from": 0,
		"size": 5
	}
}'
```