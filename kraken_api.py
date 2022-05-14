import requests
import urllib.parse
import hashlib
import hmac
import base64

def get_kraken_signature(path, data, secret):
    """Signature to authenticate API requests"""
    post_data = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + post_data).encode()
    message = path.encode() + hashlib.sha256(encoded).digest() 

    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sig_digest = base64.b64encode(mac.digest())
    return sig_digest.decode()

def kraken_request(path, data, public_key, private_key):
    """Makes a POST API request to the specified endpoint on Kraken"""
    post_url = "https://api.kraken.com" + path
    signature = get_kraken_signature(path, data, private_key)

    headers = {"API-Key": public_key, "API-Sign": signature}
    response = requests.post(url=post_url, headers=headers, data=data)
    return response