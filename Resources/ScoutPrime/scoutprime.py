from configparser import ConfigParser
from argparse import ArgumentParser
from logging import Formatter, handlers, BASIC_FORMAT, INFO, ERROR, StreamHandler, getLogger
from os import environ
from sys import argv
from json import dumps, loads
from datetime import datetime, timedelta
from ast import literal_eval
from Resources.ScoutPrime import core
from re import compile, IGNORECASE

class ScoutPrime(object):
    def __init__(self, config=None, proxy=None, section_name='scoutprime', debug=False, logger=None):
        self.config = config
        self.section_name = section_name
        self.proxy = proxy
        self.logger = logger or getLogger(__name__)
        self.debug = debug

        if config:
            self._parse_config()

        else:
            raise Exception(
                "Please specify the ScoutPrime configuration file to properly initialize the ScoutPrime object")

        if not hasattr(self, 'base_url'):
            raise Exception(
                "Please specify base_url in the ScoutPrime configuration file.")
            exit(1)

        if self.debug:
            self.core_request = core.Core(debug=True)
        else:
            self.core_request = Core()

        self.core_request.headers.update({
            "User-Agent": "ScoutPrime Python3 SDK",
            "Authorization": "Bearer {}".format(self.api_token),
        })

    def _parse_config(self):
        config_parser = ConfigParser(interpolation=None)
        config_parser.read(self.config)

        for section in config_parser.sections():
            if section == self.section_name:
                self.__dict__.update(config_parser.items(section))

    def _convert_time_to_epoch_millis(self, sp_query, num_mins, last_activity=False, first_seen=False, delay=False, delay_minutes=None):
        now_to_convert = datetime.utcnow().strftime('%Y-%m-%dT%H:00:00.000Z')
        now = datetime.strptime(now_to_convert, '%Y-%m-%dT%H:00:00.000Z')
        epoch = datetime.utcfromtimestamp(0)

        if delay:
            now_shifted = now - timedelta(minutes=int(delay_minutes))
            time_delta = now_shifted - timedelta(minutes=num_mins)

            now_milliseconds = int((now_shifted - epoch).total_seconds()) * 1000
            time_delta_milliseconds = int((time_delta - epoch).total_seconds()) * 1000
        else:
            time_delta = now - timedelta(minutes=num_mins)

            now_milliseconds = int((now - epoch).total_seconds()) * 1000
            time_delta_milliseconds = int((time_delta - epoch).total_seconds()) * 1000

        if last_activity:
            data_to_add = '["between", "lastActivityAt", {}, {}]'.format(time_delta_milliseconds, now_milliseconds)
        elif first_seen:
            data_to_add = '["between", "firstSeen", {}, {}]'.format(time_delta_milliseconds, now_milliseconds)

        sp_query['query'].append(literal_eval(data_to_add))

    def _include_historical(self, sp_query):
        sp_query.update({'period': 'all'})

    def _set_accept_text_csv(self):
        self.core_request.headers.update(dict(Accept='text/csv'))

    def _construct_url(self, api_uri):
        return '{}/{}'.format(self.base_url, api_uri)

    def normalize_data(self, data_to_normalize):
        normalized_data = []

        for line in data_to_normalize:
            if 'ref' in line:
                if 'type' in line['ref']:
                    if line['ref']['type'] == 'ipv4':
                        if 'name' in line:
                            line['src_ip'] = line.pop('name')

                    if line['ref']['type'] == 'fqdn':
                        if 'name' in line:
                            line['src_name'] = line.pop('name')

                    if line['ref']['type'] == 'cidrv4':
                        if 'name' in line:
                            line['src_ip'] = line.pop('name')

            if 'ticScore' in line:
                line['criticality'] = line.pop('ticScore')

            if 'left' in line:
                if 'ref' in line['left']:
                    if 'type' in line['left']['ref']:
                        if line['left']['ref']['type'] == 'ipv4':
                            if 'name' in line['left']:
                                line['src_ip'] = line['left'].pop('name')

                        if line['left']['ref']['type'] == 'fqdn':
                            if 'name' in line['left']:
                                line['src_name'] = line['left'].pop('name')

                        if line['left']['ref']['type'] == 'cidrv4':
                            if 'name' in line['left']:
                                line['src_ip'] = line['left'].pop('name')

                        # Remove the name from a file reference since it is an internal uuid and not a file name associated with the hash
                        if line['left']['ref']['type'] == 'file':
                            if 'name' in line['left']:
                                del line['left']['name']

                if 'ticScore' in line['left']:
                    line['criticality'] = line['left'].pop('ticScore')

                    del line['left']['ref']

                line.update(line['left'])
                del line['left']

            if 'right' in line:
                if 'ref' in line['right']:
                    del line['right']['ref']
                    line.update(line['right'])

                del line['right']

            if 'ref' in line:
                del line['ref']

            normalized_data.append(line)

        return normalized_data

    def submit_graph_query(self, uri='graph/query', historical=False, minutes=False, last_activity=True,
                           first_seen=False, time_interval=False, time_delay=False):
        request_url = self._construct_url(api_uri=uri)

        try:
            query = loads(self.sp_query)
        except:
            msg = '{} - EXITING - The following is not valid JSON: {}'.format(
                datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z'), self.sp_query)
            self.logger.error(msg)
            exit(1)

        if historical:
            self._include_historical(query)

        if minutes:
            if last_activity:
                self._convert_time_to_epoch_millis(sp_query=query, num_mins=minutes, last_activity=True, first_seen=False)
            elif first_seen:
                self._convert_time_to_epoch_millis(sp_query=query, num_mins=minutes, last_activity=False, first_seen=True)

        elif time_interval:
            if time_delay:
                if last_activity:
                    self._convert_time_to_epoch_millis(sp_query=query, num_mins=time_interval, last_activity=True,
                                                       first_seen=False, delay=True, delay_minutes=time_delay)
                elif first_seen:
                    self._convert_time_to_epoch_millis(sp_query=query, num_mins=time_interval, last_activity=False,
                                                       first_seen=True, delay=True, delay_minutes=time_delay)
            else:
                if last_activity:
                    self._convert_time_to_epoch_millis(sp_query=query, num_mins=time_interval, last_activity=True,
                                                       first_seen=False)
                elif first_seen:
                    self._convert_time_to_epoch_millis(sp_query=query, num_mins=time_interval, last_activity=False,
                                                       first_seen=True)

        return self.core_request._submit_request('POST', request_url, query)

    def _is_ip(self, ip_addr):
        response = False

        try:
            if ip_address(str(ip_addr)):
                response = True
        except ValueError:
            pass

        return response

    def _is_cidr(self, cidr):
        response = False

        try:
            if ip_network(str(cidr)):
                try:
                    ip_address(str(cidr))
                except:
                    response = True
        except ValueError:
            pass

        return response

    def _is_asn(self, asn):
        try:
            return not (int(asn) >> 32)
        except Exception as e:
            return False

    def _is_fqdn(self, fqdn):
        response = False
        allowed = compile(r'(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]', IGNORECASE)

        try:
            if len(fqdn) > 255:
                msg = "{} not a valid FQDN due to >255 characters - Ignoring".format(fqdn)
                self.logger.error(msg)
                raise Exception(msg)

            elif " " in fqdn:
                msg = "{} not a valid FQDN due to having a space - Ignoring".format(fqdn)
                self.logger.error(msg)
                raise Exception(msg)

            else:
                if allowed.match(fqdn):
                    response = True

        except Exception as e:
            msg = 'An error occurred with the following FQDN: {}'.format(fqdn)
            self.logger.error(msg, exc_info=True)

        return response

    def _smallest_cidr(self, cidr_blocks):
        smallest_cidr = None
        netmask = 0

        for cidr_block in cidr_blocks:
            if self._is_cidr(cidr_block):
                cidr_info, subnet_mask = cidr_block.split('/')

                if int(subnet_mask) > int(netmask):
                    netmask = subnet_mask
                    smallest_cidr = cidr_block

        return smallest_cidr

    @classmethod
    def from_json(cls, json_str):
        json_dict = loads(json_str.__dict__, indent=4)
        return cls(**json_dict)


if __name__ == "__main__":
    parser = ArgumentParser(description='ScoutPrime SDK')
    parser.add_argument("sp_config", help="The ScoutPrime config file.")
    parser.add_argument("--historical", help="Pull back all the threat data both active and historical",
                        action='store_true')
    parser.add_argument("--hours", type=int,
                        help="Number of hours to return data for from the current time.  Currently only works with the sources_file option")
    parser.add_argument("--debug", help="Print some basic debugging output", action='store_true')

    args = parser.parse_args()

    script_name, junk = argv[0].split('.')

    handler = handlers.WatchedFileHandler(environ.get("LOGFILE", "{}.log").format(script_name))
    formatter = Formatter(BASIC_FORMAT)
    handler.setFormatter(formatter)
    root = getLogger()
    root.addHandler(handler)
    root.setLevel(INFO)
    ch = StreamHandler()
    ch.setLevel(ERROR)
    root.addHandler(handler)
    root.addHandler(ch)

    results = None

    try:
        if args.debug:
            sp = ScoutPrime(args.sp_config, debug=True)
        else:
            sp = ScoutPrime(args.sp_config)

        if args.historical:
            if args.hours:
                results = sp.submit_graph_query(historical=True, hours=args.hours)
            else:
                results = sp.submit_graph_query(historical=True)

        if args.hours:
            results = sp.submit_graph_query(hours=args.hours)

        if 'results' in results:
            if results['results']:
                print(dumps(results['results']))

            else:
                print('No results returned')

    except Exception as e:
        msg = "The following error occurred: {}".format(e)
        print(msg)
        root.error(msg, exc_info=True)
