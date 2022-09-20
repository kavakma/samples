import requests
import json

with open('apikey.txt') as f:
    api_key = f.read()



orgid = "111111"

def getnwlist():
    # returns a list of all networks in an organization
    # on failure returns a single record with 'null' name and id
    url = "https://api.meraki.com/api/v1/organizations/%s/networks" % (orgid)
    response = requests.get(url=url, headers={'X-Cisco-Meraki-API-Key': api_key, 'Content-Type': 'application/json'})
    print (response.text)
    return response

def createbranchlist():
    with open("wifinetworklist.csv", "a") as a:
        a.write("branchname,id,branchtype\n")
        Branch = getnwlist()
        networks = Branch.json()
        for get_id in networks:
            id = get_id['id']
            site = get_id['name']
            type = get_id['productTypes']
            print(f"checking site {site}")
            if "wireless" in type:
                a.write(f"{site},{id},{type}\n")

def createbranchSSIDlist():
    Branch = getnwlist()
    networks = Branch.json()
    for get_id in networks:
        id = get_id['id']
        site = get_id['name']
        print(f"checking site {site}")
        ssid_data = ssidDetails(id)
        for item in ssid_data:
            if "errors" in item:
                # this is for the sites returning different response than expected, it is not a list like ones having SSIDs
                # instead they return a dict:
                # {\"errors\":[\"This endpoint only supports wireless networks\"]}
                # there must be a prettier way than catching the "errors" str :)
                print(f" Branch {site} has no SSIDS")
                continue

def ssidNumberOneCheck():
    result = False
    # to check if SSID number 1 is yogaowt in the branch list, IF NOT DONT RUN THE OTHERS
    with open("btwifibatchlist.txt") as r:
        for line in r.readlines():
            netid = line.rstrip()
            url = f"https://api.meraki.com/api/v1/networks/{netid}/wireless/ssids/1"
            response = requests.get(url=url, headers={'X-Cisco-Meraki-API-Key': api_key, 'Content-Type': 'application/json'})
            resp = response.json()
            print(netid)
            print(resp["name"])
            if (resp["name"] == "Guest"):
                result = True
            elif (resp["name"] == "Guest-Wifi"):
                result = True
                print (f"Branch netid {netid} already configured in its slot 1")
            else:
                result = False
                print (f"Branch netid {netid} has a different SSID in its slot 1, fix that first before running the script again !!!!!")
                break

    return result

def checkfirewallrules(netid):
    url = f"https://api.meraki.com/api/v1/networks/{netid}/wireless/ssids/1/firewall/l3FirewallRules"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Cisco-Meraki-API-Key": api_key
    }
    response = requests.request('GET', url, headers=headers)
    print (response.json())

def updatefwrules(netid):
    url = f"https://api.meraki.com/api/v1/networks/{netid}/wireless/ssids/1/firewall/l3FirewallRules"
    payload = '''{
        "rules": [
            {
                "comment": "Guest-Wifi Ranges",
                "policy": "allow",
                "protocol": "any",
                "destPort": "any",
                "destCidr": "1.0.0.0/16"
            },
            {
                "protocol": "any",
                "policy": "allow",
                "destPort": "any",
                "destCidr": "192.168.22.0/23",
                "comment": "Guest-Wifi BT Services"
            },
            {
                "comment": "Meraki MX Farm - DC1",
                "destCidr": "10.0.254.0/28",
                "destPort": "any",
                "policy": "allow",
                "protocol": "any"
            },
            {
                "comment": "Meraki MX Farm - DC2",
                "destCidr": "10.1.254.0/28",
                "destPort": "any",
                "policy": "allow",
                "protocol": "any"
            },
            {
                "comment": "Meraki new MX Farm - DC1",
                "destCidr": "10.0.254.128/28"",
                "destPort": "any",
                "policy": "allow",
                "protocol": "any"
            },
            {
                "comment": "Meraki new MX Farm - DC2",
                "destCidr": "10.1.254.128/28",
                "destPort": "any",
                "policy": "allow",
                "protocol": "any"
            },
            {
                "comment": "RFC1918_172.16.0.0/12",
                "destCidr": "172.16.0.0/12",
                "destPort": "any",
                "policy": "deny",
                "protocol": "any"
            },
            {
                "comment": "RFC1918_192.168.0.0/16",
                "destCidr": "192.168.0.0/16",
                "destPort": "any",
                "policy": "deny",
                "protocol": "any"
            },
            {
                "comment": "RFC1918_10.0.0.0/8",
                "destCidr": "10.0.0.0/8",
                "destPort": "any",
                "policy": "deny",
                "protocol": "any"
            }
        ],
        "allowLanAccess": false
    }'''


    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Cisco-Meraki-API-Key": api_key
    }
    response = requests.request('PUT', url, headers=headers, data=payload)
    print(response)


def main():
    #createbranchlist()  # this will be when there is a major change in shop configurations etc, we already have the file once created
    ssidNumberOneCheck()  # run this once and then check the outputs
    with open("guestwifibatchlist.txt") as r:
        for line in r.readlines():
            netid = line.rstrip()
            checkfirewallrules(netid)
            updatefwrules(netid)

main()