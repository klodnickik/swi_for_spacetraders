# from flask import Flask
from flask import Flask, render_template, flash, redirect, url_for, request, session, abort
import api_requests as Api
import config as Config
import logging


app = Flask(__name__)
app.secret_key = Config.SECRET_KEY


@app.route('/')
def index():

    if 'game_token' in session:
        user_logged = True
    else:
        user_logged = False

    return render_template('index.html', user_logged=user_logged)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['game_token'] = request.form['game_token']
        return redirect(url_for('index'))
    return '''
        <p>Please provide game token</p>
        <form method="post">
            <p><input type=text name=game_token>
            <p><input type=submit value=Login>
        </form>
    '''

@app.route('/logout')
def logout():
    session.pop('game_token', None)
    return redirect(url_for('index'))


@app.route("/status")
def status_page():

    bearer_token = session['game_token']
    request_status, agent_status = Api.get_agent_status(bearer_token)
    if request_status != 200: abort(403)

    request_status, list_of_contracts = Api.get_list_of_contracts(bearer_token)
    request_status, list_of_ships = Api.get_list_of_ships(bearer_token)

    # Enrich list of list

    for ship in list_of_ships:
        # find contract
        for contract in list_of_contracts:
            if ship['waypoint'] == contract['destination']:
                ship["contract_waypoint"] = True
                ship["contract_id"] = contract['contract_id']
                ship["contract_trade_symbol"] = contract['symbol']

        # check for other ships
        for ship2 in list_of_ships:
            if ship2['waypoint'] == ship['waypoint'] and ship2['ship_symbol'] != ship['ship_symbol']:
                ship["enable_transfer"] = True


    logging.info("Status page requested")
    return render_template('status.html', agent_status=agent_status, list_of_contracts=list_of_contracts, list_of_ships=list_of_ships)


@app.route("/accept_contract", methods=['POST'])
def accept_contract_action():
    bearer_token = session['game_token']
    contract_id = request.form['contract_id']
    logging.info("Contract accepted action for contract {}".format(contract_id))
    message = Api.accept_contract_action(bearer_token, contract_id)
    flash(message)
    return redirect(url_for('status_page'))


@app.route("/fulfill_contract", methods=['POST'])
def fulfill_contract_action():
    bearer_token = session['game_token']
    contract_id = request.form['contract_id']
    logging.info("Fulfill contract {}".format(contract_id))
    message = Api.fulfill_contract_action(bearer_token, contract_id)
    flash(message)
    return redirect(url_for('status_page'))


@app.route("/ship_action", methods=['POST'])
def ship_action():
    bearer_token = session['game_token']
    ship_symbol = request.form['ship_symbol']
    ship_action_type = request.form['ship_requested_action']

    logging.info("(ship_action)","Ship {} requested action {}".format(ship_symbol, ship_action_type))
    message = Api.spaceship_command_action(bearer_token, ship_symbol, ship_action_type)
    flash(message)
    return redirect(url_for('status_page'))


@app.route("/ship_extract_action", methods=['POST'])
def ship_extract_action():
    ship_symbol = request.form['ship_symbol']
    ship_action_type = request.form['ship_requested_action']

    logging.info("(ship_action)","Ship {} requested action {}".format(ship_symbol, ship_action_type))
    message = Api.spaceship_extract_action(session['game_token'], ship_symbol, ship_action_type)
    flash(message)
    return redirect(url_for('status_page'))


@app.route("/fly_ship", methods=['POST'])
def ship_fly_action():
    ship_symbol = request.form['ship_symbol']
    ship_waypoint = request.form['ship_waypoint']
    ship_frame = request.form['ship_frame']

    system_waypoint = ship_waypoint[0:7]
    logging.info ("System waypoint".format(system_waypoint))
    
    request_status, system_waypoints = Api.get_system_waypoints(session['game_token'], system_waypoint, "ALL")

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
    message = Api.spaceship_fly_action(session['game_token'], ship_symbol, dest_waypoint_symbol)
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
        available_ships_json = Api.get_list_of_avaliable_for_purchase_ships(session['game_token'], shipyard['symbol'])

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

    message = Api.buy_ship_action(session['game_token'], ship_type, waypoint)
    flash(message)
    return redirect(url_for('status_page'))




@app.route("/marketplace_page", methods=['POST'])
def marketplace_page():
    market_waypoint = request.form['market_waypoint']
    ship_symbol = request.form['ship_symbol']
    ship_status = request.form['ship_status']

    avaliable_goods = Api.get_list_of_avaliable_for_purchase_goods(session['game_token'], market_waypoint)

    return render_template('marketplace_page.html', avaliable_goods=avaliable_goods,market_waypoint=market_waypoint, ship_symbol=ship_symbol, ship_status=ship_status)



@app.route("/market_transaction", methods=['POST'])
def market_transaction():
    product_symbol = request.form['product_symbol']
    market_waypoint = request.form['market_waypoint']
    units = request.form['units']
    transaction_type = request.form['transaction_type']
    ship_symbol = request.form['ship_symbol']


    logging.info("Requested transaction {} of {} units product {} in market {}".format(
        transaction_type,
        units,
        product_symbol,
        market_waypoint))
    

    message = Api.market_transaction_action(session['game_token'], transaction_type, product_symbol, units, market_waypoint, ship_symbol )
    flash(message)
    return redirect(url_for('status_page'))



@app.route("/deliver_good_for_contract", methods=['POST'])
def deliver_good_for_contract_action():
    contract_id = request.form['contract_id']
    contract_trade_symbol = request.form['contract_trade_symbol']
    ship_symbol = request.form['ship_symbol']
    units = 0

    cargo = Api.get_cargo(session['game_token'], ship_symbol)

    for product in cargo:
        if product['symbol'] == contract_trade_symbol:
            units = product['units']

    if units > 0:
        logging.info("Ship {} delivered {} units of {} for contract {}".format(ship_symbol, units, contract_trade_symbol, contract_id))
        message = Api.deliver_contract_action(session['game_token'], contract_id, ship_symbol, contract_trade_symbol, units )
    else:
        message = "Lack of {} required by contract. No action.".format(contract_trade_symbol)
        logging.info(message)
    flash(message)
    return redirect(url_for('status_page'))



@app.route("/transfer_between_ships", methods=['POST'])
def transfer_between_ships_page():
    ship_waypoint = request.form['ship_waypoint']
    ship_symbol = request.form['ship_symbol']

    cargo = Api.get_cargo(session['game_token'], ship_symbol)

    destinations = ['jettison']
    # list of destinations

    request_status, list_of_ships = Api.get_list_of_ships(session['game_token'])

    for ship in list_of_ships:
        if ship['waypoint'] == ship_waypoint and ship_symbol != ship['ship_symbol']:
                destinations.append(ship['ship_symbol'])

    return render_template ('transfer_page.html', ship_symbol=ship_symbol, cargo=cargo, destinations=destinations)



@app.route("/transfer_products", methods=['POST'])
def transfer_products_action():
    destination = request.form['destination']
    product_symbol = request.form['product_symbol']
    market_waypoint = request.form['market_waypoint']
    ship_symbol = request.form['ship_symbol']
    units = request.form['units']

    logging.info("Transfer {} units of {} from {} to {}".format(
        units,
        product_symbol,
        ship_symbol,
        destination
    ))

    message = Api.transfer_products_action(session['game_token'], ship_symbol, destination, product_symbol, units)    

    flash(message)
    return redirect(url_for('status_page'))


@app.errorhandler(403)
def page_not_found(error):
    return render_template('incorrect_token.html'), 403