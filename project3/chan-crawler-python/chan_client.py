import requests
import logging
from datetime import datetime

class Client:
    BASE_API_URL = "https://a.4cdn.org"
    
    def __init__(self):
        self.last_modified = None
    
    ''' Retrieve all the threds of a given board '''
    def get_threads(self, board):
        # https://a.4cdn.org/pol/threads.json
        # create the end point url by joining parameters, etc.
        # endpoint_url = '/'.join([base_api_url, board, 'threads.json'])
        endpoint_url = self.build_request([board, 'threads.json'])
    
        # make request
        return self.execute(endpoint_url)

    ''' Retrieve all boards '''
    def get_boards(self):
        # https://a.4cdn.org/boards.json
        endpoint_url = self.build_request(["boards.json"])

        return self.execute(endpoint_url)
    
    ''' Retrieve the catalog for a given board '''
    def get_catalog(self, board):
        # https://a.4cdn.org/BOARD/catalog.json
        endpoint_url = self.build_request([board, 'catalog.json'])
    
        return self.execute(endpoint_url)

    ''' Given a board and thread number, retrieve the thread '''
    def get_thread(self, board, thread_number, last_modified=None):
        # https://boards.4channel.org/v/thread/648833274
        # https://boards.4channel.org/BOARD/thread/THREAD_NUMBER.json
        endpoint_url = self.build_request([board, "thread", f'{thread_number}.json'])

        return self.execute(endpoint_url, last_modified)
    
    ''' Execute the actual request and return the json '''
    def execute(self, endpoint_url, last_modified=None):
        headers = {}
        if last_modified:
            headers['If-Modified-Since'] = last_modified
        
        response = requests.get(endpoint_url, headers=headers)
    
        if response.status_code == 304: 
            logging.info('not modified')
            return None

        elif response.status_code == 404:
            logging.info(f"Unexpected response status: {response.status_code}")
            return []

        elif response.status_code != 200:
            logging.info(f"Unexpected response status: {response.status_code}")
            return None

        if 'Last-Modified' in response.headers:
            self.last_modified = datetime.strptime(response.headers['Last-Modified'], '%a, %d %b %Y %H:%M:%S GMT')

        return response.json()

    ''' Concatenate the list of parameters into a string that creates the proper url '''
    def build_request(self, endpoint_pieces):
        # put the base_api_url and any parameters into a single list
        endpoint_url = [self.BASE_API_URL] + endpoint_pieces
        endpoint_url = '/'.join(endpoint_url)
    
        return endpoint_url 