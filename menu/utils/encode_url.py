from django.core import signing

def encode_id(id):
    return signing.dumps(id)

def decode_id(encoded_id):
    try:
        return signing.loads(encoded_id)
    except signing.BadSignature:
        return None