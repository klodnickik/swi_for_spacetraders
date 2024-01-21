import requests
import logging
import config as Config

contract_product = []

def get_agent_status():
    endpoint = 'https://api.spacetraders.io/v2/my/agent'

    request_response = requests.get(endpoint, headers={"Authorization": "Bearer " + Config.bearer_token})
    agent_status_response = request_response.json()
    request_response_code = request_response.status_code

    if request_response_code != 200:
            logging.error("Response code: {}".format(request_response_code))
            logging.error(agent_status_response)
    else:
            logging.debug(agent_status_response)


    response = {
    'agent_symbol' : agent_status_response['data']['symbol'],
    'headquarters' : agent_status_response['data']['headquarters'],
    'credits' : agent_status_response['data']['credits'],
    'shipCount' : agent_status_response['data']['shipCount']  }

    return request_response_code, response 



def get_list_of_contracts():

    endpoint = 'https://api.spacetraders.io/v2/my/contracts'
    list_of_contracts_raw = requests.get(endpoint, headers={"Authorization": "Bearer " + Config.bearer_token})
    list_of_contracts_json = list_of_contracts_raw.json()

    if ( list_of_contracts_raw.status_code == 200):
        response = []
        for contract in list_of_contracts_json['data']:
            deadline = contract['terms']['deadline']
            contract_id = contract['id']
            deliver_list = contract['terms']['deliver']
            payment_on_fulfilled = contract['terms']['payment']['onFulfilled']
            payment_on_accepted = contract['terms']['payment']['onAccepted']
            fulfilled = contract['fulfilled']
            accepted = contract['accepted']


            for item in deliver_list:
                symbol = item['tradeSymbol']
                destination = item['destinationSymbol']
                units_required = item['unitsRequired']
                units_fulfilled = item['unitsFulfilled']
                contract_product.append(symbol)
        
            response_json = {
                'contract_id' : contract_id,
                'deadline' : deadline,
                'symbol' : symbol,
                'destination' : destination,
                'units_required': units_required,
                'units_fulfilled' : units_fulfilled,
                'accepted' : accepted,
                'fulfilled' : fulfilled,
                'payment_on_fulfilled' : payment_on_fulfilled,
                'payment_on_accepted' : payment_on_accepted  }
            response.append(response_json)

    else:
        logging.error("Response code: {}".format(list_of_contracts_raw.status_code))
        logging.error(list_of_contracts_json)


    return list_of_contracts_raw.status_code, response 
    




def accept_contract_action(contract_id):
           
    endpoint = 'https://api.spacetraders.io/v2/my/contracts/' + contract_id + '/accept'
    headers = { 'Authorization' : 'Bearer ' + Config.bearer_token }

    request_response_raw = requests.post(endpoint, headers=headers)
    request_response = request_response_raw.json()

    logging.debug("(accept_contract_action)", request_response)
    
    if (request_response_raw.status_code == 200):
        logging.info("(accept_contract_action)", "Response code 200")
        if request_response['data']['contract']['accepted'] == "true":
            message = "Contract {} has been accepted succesfully".format(contract_id)
            logging.info("(accept_contract_action)", message)
        else:
            message = "Contract {} has NOT been accepted, some error?".format(contract_id)
            logging.warning("(accept_contract_action)", message)
    else:
        logging.warning("(accept_contract_action)", "Response code {}".format(request_response_raw.status_code))
        message = "Unexpected response from API .... "

    return message




def get_list_of_ships():

    endpoint = 'https://api.spacetraders.io/v2/my/ships'
    ship_status_response = requests.get(endpoint, headers={"Authorization": "Bearer " + Config.bearer_token}).json()

    response = []

    for ship in ship_status_response['data']:

        cargo_list = []

        for item in ship['cargo']['inventory']:
            cargo_json = {
                'symbol' : item['symbol'],
                'units' : item['units']
            }
            cargo_list.append(cargo_json)

        response_json = {
            'ship_symbol' : ship['symbol'],
            'waypoint' : ship['nav']['waypointSymbol'], 
            'status' : ship['nav']['status'],
            'fuel_current' : ship['fuel']['current'],
            'fuel_capacity' : ship['fuel']['capacity'],
            'cargo_units' : ship['cargo']['units'],
            'cargo_capacity' : ship['cargo']['capacity'],
            'destination' : ship['nav']['route']['destination']['symbol'],
            'frame' : ship['frame']['symbol'],
            # 'inventory' : ship['cargo']['inventory'],
            'inventory' : cargo_list,            
            'arrival' : ship['nav']['route']['arrival']
        }
        response.append(response_json)
        request_status = "OK"

    return request_status, response



def spaceship_command_action(ship_symbol, ship_command):

    endpoint = 'https://api.spacetraders.io/v2/my/ships/' + ship_symbol + '/' + ship_command

    ship_request_response_raw = requests.post(endpoint, headers={"Authorization": "Bearer " + Config.bearer_token})
    ship_request_response = ship_request_response_raw.json()

    if ship_request_response_raw.status_code == 200:
        message = "Action {} on ship {} requested succesfully (response code 200)".format(ship_command, ship_symbol)
        logging.info(message)
    else:
        message = "Action {} on ship {} requested with ERROR  (response code {})".format(ship_command, ship_symbol, str(ship_request_response_raw.status_code))
        logging.warning(message)

    return message



def spaceship_extract_action(ship_symbol, ship_command):

    endpoint = 'https://api.spacetraders.io/v2/my/ships/' + ship_symbol + '/' + ship_command

    ship_request_response_raw = requests.post(endpoint, headers={"Authorization": "Bearer " + Config.bearer_token})
    ship_request_response = ship_request_response_raw.json()

    if ship_request_response_raw.status_code == 201:
        
        message = "Mining succesful. Extracted {} of {}. Cooldown {} seconds".format(
            ship_request_response['data']['extraction']['yield']['units'],
            ship_request_response['data']['extraction']['yield']['symbol'],
            ship_request_response['data']['cooldown']['totalSeconds'],
        )
    else: 
        message = "Mining NOT succesful. Error code {} ({})".format(
            ship_request_response_raw.status_code,
            ship_request_response['error']['message']
        )
        logging.warning(message)

    return message


def get_system_waypoints(system, traits):

    if traits == "ALL":
        endpoint = 'https://api.spacetraders.io/v2/systems/' + system + '/waypoints'   
    else:
        endpoint = 'https://api.spacetraders.io/v2/systems/' + system + '/waypoints?traits=' + traits    

    # endpoint = 'https://api.spacetraders.io/v2/systems/' + system + '/waypoints'
    response = []
    response_page = 0

    headers = { 'Authorization' : 'Bearer ' + Config.bearer_token }


    request_response_raw = requests.get(endpoint, headers=headers)
    system_waypoints_response = request_response_raw.json()


    meta_total = system_waypoints_response['meta']['total']
    meta_page = system_waypoints_response['meta']['page']
    meta_limit = system_waypoints_response['meta']['limit']

    logging.info("System waypoint api request metadata: total {}, limit {}".format(meta_total, meta_limit))


    while (len(response) < meta_total):
        response_page = response_page + 1
        payload = {'page': response_page}
        request_response_raw = requests.get(endpoint, params=payload, headers=headers)
        system_waypoints_response = request_response_raw.json()


        for waypoint in system_waypoints_response['data']:
                marketplace = False
                trading_hub = False
                shipyard = False

                for trail in waypoint['traits']:
                    if ( trail['symbol'] == 'MARKETPLACE'): marketplace = True
                    elif ( trail['symbol'] == 'TRADING_HUB'): trading_hub = True
                    elif ( trail['symbol'] == 'SHIPYARD'): shipyard = True

                    traits_symbol=trail['symbol']

                response_json = {
                    'symbol' : waypoint['symbol'],
                    'type' : waypoint['type'],
                    'traits' : waypoint['traits'],
                    'traits_symbol': traits_symbol,
                    'faction' : waypoint['faction']['symbol'],
                    'marketplace' : marketplace,
                    'trading_hub' : trading_hub,
                    'shipyard' : shipyard
                }
                response.append(response_json)

        print("Imported {} waypoints, expectedtotal {}".format(len(response), meta_total))

    request_status = "OK"
    return request_status, response




def spaceship_fly_action(ship_symbol, dest_waypoint_symbol):

    endpoint = 'https://api.spacetraders.io/v2/my/ships/' + ship_symbol + '/navigate'
    parameter = { 'waypointSymbol' : dest_waypoint_symbol }
        
    headers = { 'Authorization' : 'Bearer ' + Config.bearer_token,
                'Content-Type': 'application/json',
                'Accept' : 'application/json' }

    request_response_raw = requests.post(endpoint, json=parameter, headers=headers)
    request_response = request_response_raw.json()

    if ( request_response_raw.status_code == 200):
        response = {
            'fuel_consumed' : request_response['data']['fuel']['consumed']['amount'],
            'fuel_capacity' : request_response['data']['fuel']['capacity'],
            'nav_destination' : request_response['data']['nav']['waypointSymbol'],
            'arrival_time' : request_response['data']['nav']['route']['arrival'],
            'status' : request_response['data']['nav']['status'],
            'flight_mode' : request_response['data']['nav']['flightMode']
        }
        message = "Ship {} will reach {} at {} (flight Mode {}, consumed fuel {})".format(ship_symbol,
                                                            request_response['data']['nav']['waypointSymbol'],
                                                            request_response['data']['nav']['route']['arrival'],
                                                            request_response['data']['nav']['flightMode'],
                                                            request_response['data']['fuel']['consumed']['amount'] )
    else:
        logging.warning("Resonse code {}".format(request_response_raw.status_code) )
        logging.warning(request_response)
        message = "Error .. command not executed ..."


    return message



def get_list_of_avaliable_for_purchase_ships(waypoint):

    system_waypoint = waypoint[0:7]
    endpoint = 'https://api.spacetraders.io/v2/systems/' + system_waypoint + '/waypoints/'+ waypoint + '/shipyard'
    avaliable_ship = requests.get(endpoint, headers={"Authorization": "Bearer " + Config.bearer_token}).json()

  
    return avaliable_ship



def buy_ship_action(ship_symbol, waypoint):

    endpoint = 'https://api.spacetraders.io/v2/my/ships'
    parameter = { 'shipType' : ship_symbol,
                 'waypointSymbol' : waypoint }
        
    headers = { 'Authorization' : 'Bearer ' + Config.bearer_token,
                'Content-Type': 'application/json',
                'Accept' : 'application/json' }

    request_response_raw = requests.post(endpoint, json=parameter, headers=headers)
    request_response = request_response_raw.json()

    if (request_response_raw.status_code == 201):
        cost_of_ship = request_response['data']['transaction']['price']
        message = "Purchase succesful, cost of ship {} was {}".format(ship_symbol, cost_of_ship)
        logging.info(message)
    else:
        message = "Transaction NOT completed. ({})".format(request_response['error']['message'])
        logging.warning(message)

    return message