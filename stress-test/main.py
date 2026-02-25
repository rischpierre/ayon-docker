import os
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

import ayon_api

PROJECT = "pet_project3"
NUM_THREADS = 10
REQUESTS_PER_THREAD = 3 * 1000
AYON_API_KEY = os.environ["AYON_API_KEY"]
AYON_SERVER_URL = os.environ["AYON_SERVER_URL"]
assert AYON_API_KEY
assert AYON_SERVER_URL

ayon_api.init_service(
        token=AYON_API_KEY,
        server_url=AYON_SERVER_URL,
)

PROJECT = "pet_project3"


def random_query(random_ids):
    get_entity, ids = random.choice(((ayon_api.get_version_by_id, random_ids["versions"]), (ayon_api.get_folder_by_id, random_ids["folders"])))
    try:
        selected_id = random.choice(ids)
        result = get_entity(PROJECT, selected_id)
        # print(result)
    except Exception as e:
        print(f"error: {e}")


def export_ids_to_file(file_):
    folders = list(ayon_api.get_folders(PROJECT))
    versions = list(ayon_api.get_versions(PROJECT))
    print(len(folders), len(versions))

    data = {
        PROJECT: {
            "versions": [x["id"] for x in versions],
            "folders": [x["id"] for x in folders],
        }
    }
    import json

    with open(file_, "w") as fp:
        json.dump(data, fp, indent=2)


def get_ids(file_):
    import json
    data = {}
    with open(file_, "r") as fp:
        data = json.load(fp)
    return data[PROJECT]

def main():
    # export_ids_to_file("random_ids.json")
    random_ids = get_ids("random_ids.json")

    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        futures = [
            executor.submit(random_query,random_ids)
            for i in range(REQUESTS_PER_THREAD)
        ]

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Worker error: {e}")


if __name__ == "__main__":
    main()
