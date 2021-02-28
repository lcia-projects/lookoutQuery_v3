from logging import getLogger
from time import sleep
from requests import get, post
from json import dumps, loads
from datetime import datetime


class Core(object):
    def __init__(self, proxy=None, debug=False, logger=None):
        self.logger = logger or getLogger(__name__)
        self.proxy = proxy
        self.debug = debug

        self.headers = {
            "Accept": "application/json",
            "Content-type": "application/json",
        }

    def _submit_request(self, request_type=None, request_url=None, request_data=None, data=False, params=False, json=True, output_format='json', verify=True, auth=None):
        self.logger.info(
            '{} - Querying {} for the following: {}'.format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                                                            request_url, dumps(request_data)))

        #if self.debug:
        #    print('URL:\n{}\n'.format(request_url))
        #    print('Headers:\n{}\n'.format(self.headers))
        #    print('HTTP Request:\n{}\n'.format(dumps(request_data)))

        success = False
        retry = 1
        max_retry = 480
        wait_time = 30
        response = ''

        while not success and retry < max_retry:
            try:
                if request_type == 'GET':
                    if self.proxy:
                        if json:
                            response = get(request_url, headers=self.headers, json=request_data, verify=verify, proxies=self.proxy, auth=auth)
                            response.raise_for_status()
                        elif data:
                            response = get(request_url, headers=self.headers, data=request_data,
                                           verify=verify, proxies=self.proxy, auth=auth)
                            response.raise_for_status()
                        elif params:
                            response = get(request_url, headers=self.headers, params=request_data,
                                           verify=verify, proxies=self.proxy, auth=auth)
                            response.raise_for_status()
                        else:
                            raise Exception(
                                "Unknown request type: json, data or params are the only supported methods")
                            exit(1)
                    else:
                        if json:
                            response = get(request_url, headers=self.headers, json=request_data, verify=verify, auth=auth)

                            # if self.debug:
                            #     print(vars(response.request))

                            response.raise_for_status()
                        elif data:
                            response = get(request_url, headers=self.headers, data=request_data, verify=verify, auth=auth)

                            # if self.debug:
                            #     print(vars(response.request))

                            response.raise_for_status()
                        elif params:
                            response = get(request_url, headers=self.headers, params=request_data, verify=verify, auth=auth)

                            # if self.debug:
                            #     print(vars(response.request))

                            response.raise_for_status()
                        else:
                            raise Exception(
                                "Unknown request type: json, data or params are the only supported methods")
                            exit(1)

                    success = True

                if request_type == 'POST':
                    if self.proxy:
                        if json:
                            response = post(request_url, headers=self.headers, json=request_data, verify=verify, proxies=self.proxy, auth=auth)
                            response.raise_for_status()
                        elif data:
                            response = post(request_url, headers=self.headers, data=request_data, verify=verify, proxies=self.proxy, auth=auth)
                            response.raise_for_status()
                        elif params:
                            response = post(request_url, headers=self.headers, params=request_data, verify=verify,
                                           proxies=self.proxy, auth=auth)
                            response.raise_for_status()
                        else:
                            raise Exception(
                                "Unknown request type: json, data or params are the only supported methods")
                            exit(1)
                    else:
                        if json:
                            response = post(request_url, headers=self.headers, json=request_data, verify=verify, auth=auth)
                            response.raise_for_status()
                        elif data:
                            response = post(request_url, headers=self.headers, data=request_data, verify=verify, auth=auth)
                            response.raise_for_status()
                        elif params:
                            response = post(request_url, headers=self.headers, params=request_data, verify=verify, auth=auth)
                            response.raise_for_status()
                        else:
                            raise Exception(
                                "Unknown request type: json, data or params are the only supported methods")
                            exit(1)

                    success = True

                # if self.debug:
                #     print('HTTP Response: {}'.format(response.text))

                if response:
                    if output_format == 'json':
                        try:
                            return response.json()
                        except Exception as e:
                            msg = 'Invalid JSON response {} - Exiting'.format(response.text)
                            print(msg)
                            self.logger.error(msg, exc_info=True)
                            exit(1)

                    elif output_format == 'csv':
                        return response.text

                    elif output_format == 'raw':
                        return response.content
                    else:
                        raise Exception(
                            "Unknown output_format: json, csv or raw are the only supported formats")
                        exit(1)

            except:
                msg = 'Request failed to {}.  Retrying in {} seconds'.format(request_url, wait_time)
                print(msg)
                self.logger.error(msg, exc_info=True)
                sleep(wait_time)
                retry += 1

    @classmethod
    def from_json(cls, json_str):
        json_dict = loads(json_str.__dict__, indent=4)
        return cls(**json_dict)
