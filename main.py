import time
import requests
import kraken_api
import twitter_api

def main():
    # Get Kraken REST API access keys
    with open("api_keys.txt", "r") as f:
        lines = f.read().splitlines()
        public_key, private_key = lines[0], lines[1]

    while True:
        status = requests.get('https://api.kraken.com/0/public/SystemStatus')
        if status.json()["result"]["status"] != "online":
            print("API status offline")
            # try again in 60 seconds
            time.sleep(60)
            continue

        volume = 0  # minimum required order to buy dogecoins on Kraken is 20 dogecoin
        account_balance = 0  # balance in account in USD
        doge_balance = 0  # number of dogecoins currently held in account

        # retrieve current cash and dogecoin balances
        response = kraken_api.kraken_request(
            '/0/private/Balance', 
            {
                "nonce": str(int(1000*time.time()))
            }, 
            public_key, 
            private_key)
        try:
            account_balance = float(response.json()["result"]["ZUSD"])
        except KeyError:
            print("Error retrieving account balance")
            print("Response:", response.json())
        try:
            doge_balance = float(response.json()["result"]["XXDG"])
        except KeyError:
            print("Error retrieving dogecoin balance")
            print("Response:", response.json())

        # Get sentiment of tweets; sentiment -> float, volume -> int
        sentiment = twitter_api.get_sentiment(account_balance, doge_balance)
        current_price = float(requests.get("https://api.kraken.com/0/public/Ticker?pair=DOGEUSD"
                                          ).json()["result"]["XDGUSD"]["c"][0])
        volume = int(account_balance * 0.95 / current_price)

        # Buy order from Kraken API if positive sentiment found in Elon's tweet
        if sentiment > 0 and volume >= 20:
            response = kraken_api.kraken_request(
                '/0/private/AddOrder', 
                {
                    "nonce": str(int(1000*time.time())),
                    "ordertype": "market",
                    "type": "buy",
                    "volume": volume,
                    "pair": "XDGUSD",
                }, 
                public_key, 
                private_key)
            
            error_data = response.json()["error"]
            if not error_data:
                print("Successfully bought", volume, "Doge!")
                continue
            elif "Insufficient funds" in error_data[0]:
                print("Insufficient funds to make an order of", volume, "Doge.")
            else:
                print("Unknown Error. API response:", error_data)
        elif volume < 20:
            print("Insufficient funds to make a minimum order of 20 Doge.")

        # Sell order from Kraken API if negative sentiment found in Elon's tweet
        if doge_balance > 0 and sentiment < 0:            
            response = kraken_api.kraken_request(
                '/0/private/AddOrder', 
                {
                    "nonce": str(int(1000*time.time())),
                    "ordertype": "market",
                    "type": "sell",
                    "volume": doge_balance,
                    "pair": "XDGUSD",
                }, 
                public_key, 
                private_key)
            
            error_data = response.json()["error"]
            if not error_data:
                print("Successfully sold", doge_balance, "Doge!")
            elif "Insufficient funds" in error_data[0]:
                print("Insufficient funds to sell an order of", doge_balance, "Doge.")
            else:
                print("Unknown Error. API response:", error_data)
        
        time.sleep(10)

main()