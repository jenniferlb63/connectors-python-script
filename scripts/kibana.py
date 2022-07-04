from connectors.elastic import ElasticServer
from connectors.logger import logger

import os
import asyncio

import yaml


CONNECTORS_INDEX = ".elastic-connectors"

# XXX should be set by kibana
async def prepare(config):
    es = ElasticServer(config["elasticsearch"])

    # https:#github.com/elastic/enterprise-search-team/discussions/2153#discussioncomment-2999765
    doc = {
        # Used by the frontend to manage the api key associated with the connector
        "api_key_id": "",
        # Configurations, e.g. API key
        "configuration": {
            "host": {"value": "mongodb://127.0.0.1:27021", "label": "MongoDB Host"},
            "database": {"value": "sample_airbnb", "label": "MongoDB Database"},
            "collection": {
                "value": "listingsAndReviews",
                "label": "MongoDB Collection",
            },
        },
        # Name of the index the documents will be written to. Set by Kibana, *not* the connector.
        "index_name": "search-airbnb",
        # used to surface copy and icons in the front end
        "service_type": "mongo",
        # Current status of the connector, and the value can be 1. Needs configuration, 2. Configured, 3. Error
        "status": "1",
        # Current sync status, and the value can be 1. Completed, 2. In progress, 3. Failed
        "sync_status": "1",
        # sync error
        "sync_error": "",
        # Written by connector on each operation, used by Kibana to hint to user about status of connector
        "last_seen": "",
        # Date the last sync was completed
        "last_synced": "",
        # Date the connector was created
        "created_at": "",
        # Date the connector was updated
        "updated_at": "",
        # Scheduling intervals
        "scheduling": {"enabled": True, "interval": "0 * * * *"},  # crontab syntax
        # A flag to run sync immediately
        "sync_now": True,
    }

    await es.prepare_index(CONNECTORS_INDEX, [doc], delete_first=True)
    print("Done")
    await es.close()


config_file = os.path.join(os.path.dirname(__file__), "..", "config.yml")

if not os.path.exists(config_file):
    raise IOError(f"{config_file} does not exist")

with open(config_file) as f:
    config = yaml.safe_load(f)


loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(prepare(config))
except (asyncio.CancelledError, KeyboardInterrupt):
    logger.info("Bye")
