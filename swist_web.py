from flask import Flask
from flask import render_template, flash, redirect, url_for, request
import api_requests as Api
import config as Config
import logging


app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/status")
def status_page():

    request_status, agent_status = Api.get_agent_status()
    request_status, list_of_contracts = Api.get_list_of_contracts()
    request_status, list_of_ships = Api.get_list_of_ships()


    logging.info("Status page requested")
    return render_template('status.html', agent_status=agent_status, list_of_contracts=list_of_contracts, list_of_ships=list_of_ships)


@app.route("/accept_contract", methods=['POST'])
def accept_contract_action():
    contract_id = request.form['contract_id']
    logging.info("Contract accepted action for contract {}".format(contract_id))
    message = Api.accept_contract_action(contract_id)
    flash(message)
    return redirect(url_for('status_page'))


@app.route("/ship_action", methods=['POST'])
def ship_action():
    ship_symbol = request.form['ship_symbol']
    ship_action_type = request.form['ship_requested_action']

    logging.info("(ship_action)","Ship {} requested action {}".format(ship_symbol, ship_action_type))
    message = Api.spaceship_command_action(ship_symbol, ship_action_type)
    flash(message)
    return redirect(url_for('status_page'))


@app.route("/ship_extract_action", methods=['POST'])
def ship_extract_action():
    ship_symbol = request.form['ship_symbol']
    ship_action_type = request.form['ship_requested_action']

    logging.info("(ship_action)","Ship {} requested action {}".format(ship_symbol, ship_action_type))
    message = Api.spaceship_extract_action(ship_symbol, ship_action_type)
    flash(message)
    return redirect(url_for('status_page'))


@app.route("/fly_ship", methods=['POST'])
def ship_fly_action():
    ship_symbol = request.form['ship_symbol']
    ship_waypoint = request.form['ship_waypoint']
    ship_frame = request.form['ship_frame']

    system_waypoint = ship_waypoint[0:7]
    logging.info ("System waypoint".format(system_waypoint))
    
    request_status, system_waypoints = Api.get_system_waypoints(system_waypoint, "ALL")

    return render_template('fly_ship.html', 
                           ship_symbol=ship_symbol,
                           ship_waypoint=ship_waypoint,
                           ship_frame=ship_frame,
                           system_waypoints=system_waypoints)



@app.route("/fly_command", methods=['POST'])
def fly_ship_action():
    ship_symbol = request.form['ship_symbol']
    dest_waypoint_symbol = request.form['dest_waypoint_symbol']
    logging.info("(fly_ship_action)","Ship {} requested command to fly to {}".format(ship_symbol, dest_waypoint_symbol))
    message = Api.spaceship_fly_action(ship_symbol, dest_waypoint_symbol)
    flash(message)
    return redirect(url_for('status_page'))


@app.route("/purchase_ship_page", methods=['POST'])
def purchase_ship_page():
    headquarter = request.form['headquarter']
    system_waypoint = headquarter[0:7]
    logging.info ("System waypoint: {}".format(system_waypoint))
    request_status, system_waypoints = Api.get_system_waypoints(system_waypoint, "SHIPYARD")
    logging.debug("Identified {} shipyards".format(system_waypoints))

    available_ships = []

    for shipyard in system_waypoints:
        available_ships_json = Api.get_list_of_avaliable_for_purchase_ships(shipyard['symbol'])

        for ship_type in available_ships_json['data']['shipTypes']:
            print (ship_type)

            available_ship_json = {
                'waypoint' : shipyard['symbol'],
                'ship_type' : ship_type['type'] 
            }

            available_ships.append(available_ship_json)

    return render_template('purchase_ship.html', available_ships=available_ships)


@app.route("/buy_ship", methods=['POST'])
def buy_ship_action():
    ship_type = request.form['ship_type']
    waypoint = request.form['waypoint']

    logging.info("Requested purchase of ship {} in shipyard {}".format(ship_type, waypoint ))

    message = Api.buy_ship_action(ship_type, waypoint)
    flash(message)
    return redirect(url_for('status_page'))