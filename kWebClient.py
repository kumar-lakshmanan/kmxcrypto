'''
Created on 29-Apr-2025

@author: kayma
'''
import kTools
import requests
import json

class WebClient:
    
    def __init__(self, base_url, headers=None, auth=None):
        self.tls = kTools.KTools()
        self.base_url = base_url
        self.headers = headers or {}
        self.auth = auth

    def _build_url(self, endpoint):
        return f"{self.base_url}/{endpoint}"

    def _make_request(self, method, endpoint, data=None, params=None, headers=None):
        url = self._build_url(endpoint)
        all_headers = self.headers.copy()
        if headers:
            all_headers.update(headers)
        
        response = requests.request(method, url, headers=all_headers, json=data, params=params, auth=self.auth)
        response.raise_for_status()
        return response

    def get(self, endpoint="", params=None, headers=None):
        return self._make_request("GET", endpoint, params=params, headers=headers)

    def post(self, endpoint, data=None, headers=None):
         return self._make_request("POST", endpoint, data=data, headers=headers)

    def put(self, endpoint, data=None, headers=None):
        return self._make_request("PUT", endpoint, data=data, headers=headers)

    def patch(self, endpoint, data=None, headers=None):
        return self._make_request("PATCH", endpoint, data=data, headers=headers)

    def delete(self, endpoint, headers=None):
        return self._make_request("DELETE", endpoint, headers=headers)

    def get_json(self, endpoint, params=None, headers=None):
      response = self.get(endpoint, params, headers)
      return response.json()


# Example Usage
if __name__ == '__main__':

    url = "https://www.grtjewels.com"
    url = "https://coinmarketcap.com/currencies/litecoin"
    url = "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/market-pairs/latest?slug=litecoin&start=1&limit=10&category=spot&centerType=all&sort=cmc_rank_advanced&direction=desc&spotUntracked=true"
    url = "https://api.coinmarketcap.com/gravity/v3/gravity/crypto/queryVoteResult"
    url = 'https://api.coinmarketcap.com/data-api/v3/cryptocurrency/market-pairs/latest?slug=xrp&start=1&limit=10&category=spot&centerType=all&sort=cmc_rank_advanced&direction=desc&spotUntracked=true'
    url = 'https://api.coinmarketcap.com/gravity/v3/gravity/vote/overview-data' #works
    
    
    payloads = {}
    payloads['cryptoId'] = '52'
    payloads['timeFrame'] = 7
        
    params = {}

    endpoint = ''
    
    headers = {}
    headers['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
    
    wc = WebClient(base_url=url)
    

    #resp = wc.get(endpoint, params, headers)
    resp = wc.post(endpoint, payloads, headers)



    print(resp)
    print(resp.content)
    wc.tls.writeFileContent('temppage.html', resp.content)

    print('done')
    
    
  
#
# # Example Usage
# if __name__ == '__main__':
#     client = WebClient(base_url="https://jsonplaceholder.typicode.com")
#
#     # GET request
#     response_get = client.get("posts/1")
#     print("GET Response:", response_get.json())
#
#     # POST request
#     new_post = {"userId": 1, "title": "Custom Post", "body": "This is a custom post."}
#     response_post = client.post("posts", data=new_post)
#     print("POST Response:", response_post.json())
#
#     #GET request and parse json
#     response_get_json = client.get_json("todos/1")
#     print("GET JSON Response:", response_get_json)
#
#     # Error handling
#     try:
#         client.get("nonexistent_endpoint")
#     except requests.exceptions.HTTPError as e:
#         print("Error:", e)