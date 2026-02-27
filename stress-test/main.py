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


def random_query_huge(random_ids):
    shots = list(ayon_api.get_folders(PROJECT, folder_types=["Shot"]))
    assert shots
    shots_ids = [x["id"] for x in shots]
    try:
        selected_id = random.choice(shots_ids)
        # selected_id = 'c80d6c8efb1711edaeef901b0e2e41d2'
        query = f"""
            query MyQuery {{
              project(name: "{PROJECT}") {{
                folder(id: "{selected_id}") {{
                  products {{
                    edges {{
                      node {{
                        versions {{
                          edges {{
                            node {{
                              active
                              allAttrib
                              author
                              createdAt
                              createdBy
                              data
                              featuredVersionType
                              hasReviewables
                              heroVersionId
                              id
                              isLatest
                              isLatestDone
                              name
                              parents
                              path
                              productId
                              projectName
                              status
                              tags
                              taskId
                              thumbnailId
                              updatedAt
                              updatedBy
                              version
                              representations {{
                                edges {{
                                  node {{
                                    active
                                    allAttrib
                                    context
                                    createdBy
                                    createdAt
                                    data
                                    fileCount
                                    id
                                    name
                                    parents
                                    path
                                    projectName
                                    status
                                    tags
                                    traits
                                    updatedAt
                                    updatedBy
                                    versionId
                                  }}
                                }}
                              }}
                            }}
                          }}
                        }}
                        active
                        allAttrib
                        createdAt
                        createdBy
                        data
                        folderId
                        id
                        name
                        parents
                        path
                        productBaseType
                        productType
                        projectName
                        status
                        tags
                        type
                        updatedAt
                        updatedBy
                      }}
                    }}
                  }}
                }}
              }}
            }}
           
        """
        result = ayon_api.query_graphql(query)
        # from pympler import asizeof
        # print(asizeof.asizeof(result.data["data"]) / 1024 / 1024, "MB")
            
    except Exception as e:
        print(f"error: {e}")

def random_query(random_ids):
    get_entity, ids = random.choice(
        (
            (ayon_api.get_version_by_id, random_ids["versions"]),
            (ayon_api.get_folder_by_id, random_ids["folders"]),
        )
    )
    try:
        selected_id = random.choice(ids)
        result = get_entity(PROJECT, selected_id)
        # print(result)
    except Exception as e:
        print(f"error: {e}")

def random_version_update(random_ids):
    ids = random_ids["versions"]
    statuses = ("Not ready", "In progress")
    try:

        selected_id = random.choice(ids)
        version = ayon_api.get_version_by_id(PROJECT, selected_id)

        if not version:
            raise RuntimeError("no version")

        original_status = version["status"]
        new_status = next((s for s in statuses if s != original_status), None)
        if not new_status:
            raise RuntimeError("no status")

        ayon_api.update_version(PROJECT, selected_id, status=new_status)
        ayon_api.update_version(PROJECT, selected_id, status=original_status)

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
        futures = []
        for _ in range(REQUESTS_PER_THREAD):
            f = random.choice(
                (
                    # 5:1 query:update ratio
                    random_version_update,
                    random_query,
                    random_query,
                    random_query,
                    random_query,
                    # random_query_huge,
                )
            )
            futures.append(executor.submit(f, random_ids))

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Worker error: {e}")


if __name__ == "__main__":
    main()
