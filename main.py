from google.cloud import firestore
from datetime import datetime
from starlingbank import StarlingAccount
from os import environ
from math import floor
from hashlib import sha512
from base64 import b64encode

FIRESTORE_COLLECTION_NAME = environ['FIRESTORE_COLLECTION_NAME']
TARGET_GOAL_ID = environ['TARGET_GOAL_ID']
STARLING_API_TOKEN = environ['STARLING_API_TOKEN']
STARLING_WEBHOOK_SECRET = environ['STARLING_WEBHOOK_SECRET'].encode('utf-8')


def uid_already_processed(db, notification_uid):
    """Check if the notification UID has already been processed."""
    uid = db.document(notification_uid).get()
    if uid.exists:
        return True
    else:
        return False


def log_notification_uid(db, notification_uid):
    """Log the newly processed notification UID."""
    db.document(notification_uid).set({
        'processedDate': datetime.now().astimezone()
    })


def roundup(amount_spent):
    """Calculate the roundup and return the value in minor units (pennies)."""
    if amount_spent > 0:
        return 0

    amount_spent = -amount_spent  # Convert to a positive number
    amount_spent_floor = floor(amount_spent)

    if amount_spent_floor == amount_spent:
        return 0
    else:
        return int(round(((amount_spent_floor + 1) - amount_spent) * 100))


def signature_check(secret, body, signature):
    """Check the body and secret against the declared signature."""
    hash = b64encode(sha512(secret + body).digest())

    if hash == signature:
        return True
    else:
        return False


def process_request(request):
    """Process a Starling webhook body and transfer the roundup value if appropriate."""
    if signature_check(
        STARLING_WEBHOOK_SECRET,
        request.data,
        request.headers['X-Hook-Signature'].encode('utf-8')
    ) is False:
        return 'Signature Check Failure', 401

    message_body = request.get_json()
    notification_uid = message_body["webhookNotificationUid"]
    amount_spent = message_body["content"]["amount"]

    db = firestore.Client().collection(FIRESTORE_COLLECTION_NAME)

    if uid_already_processed(db, notification_uid):
        return 'Already Processed'
    log_notification_uid(db, notification_uid)

    roundup_minor_units = roundup(amount_spent)

    if roundup_minor_units == 0:
        return 'No Roundup Available'

    my_account = StarlingAccount(STARLING_API_TOKEN)

    my_account.update_balance_data()
    balance_minor_units = my_account.effective_balance * 100
    if roundup_minor_units > balance_minor_units:
        return 'Insufficient Funds'

    my_account.update_savings_goal_data()
    my_account.savings_goals[TARGET_GOAL_ID].deposit(roundup_minor_units)
