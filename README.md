# starlingbank-roundup-google-cloud
Roundup Starling Bank card transactions and transfer the remainder to a specified savings goal. e.g. Spend £1.48, 52p gets transferred to the nominated savings goal.

This script designed to run as a Google Cloud Function. This cloud function then exposes a webhook that can be confgured against your personal access starling developer account. A Google Firestore database is also required to store Notification UIDs, this is to prevent the same notification being processed more than once (as the webhook is sometimes called more than once).

The following 4 enviroment variables are required:

* FIRESTORE_COLLECTION_NAME (e.g. StarlingNotificationUIDs)
* TARGET_GOAL_ID (e.g. "1086c98e-513g-4065-ac43-390e6ef58fg6", you will need to use the starling bank API to find this out)
* STARLING_API_TOKEN = (e.g. "4G3f4C2soM6fmghfgh5uq85hN6fGA8gTUWtt9pMhKxqDBjfgdf546Wfnt6xmD0Yc")
* STARLING_WEBHOOK_SECRET (e.g. "249f6af8-6123-4974-91fe-bef172ca534")
