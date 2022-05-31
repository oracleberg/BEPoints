# This file defines the Points API and its methods
from datetime import datetime
from flask import make_response, abort

# Initialize Payers container, TimestampPayer dict, and Timeline list
Payers = {}  # {'Payer': {'Timestamp': 'Points', 'Timestamp': 'Points'}}
TimestampPayer = {}  # {'Timestamp': 'Payer', 'Timestamp': 'Payer'}
Timeline = []  # ['Timestamp', 'Timestamp']


def get_transaction(transaction):
    """
    This function pulls parameters from request and adds the transaction.

    :param transaction: Request obj with transaction details
    :return: 201 HTTP code if successful, aborts otherwise
    """
    if transaction is not None:
        points = transaction.get("points", None)
        payer = transaction.get("payer", None)
        timestamp = transaction.get("timestamp", None)
        return add_transactions(payer, points, timestamp)
    else:
        abort(400, "Please include transaction parameters in your request as documented at localhost:5000/api/ui")


def get_points(amount):
    """
    This function spends the given points.

    :param amount: Amount of points to spend
    :return: Dict of payer: points spent
    """
    total = amount.get("points", None)
    if total is not None:
        return list(spend_points(total))
    else:
        abort(400,
              "Please include a positive integer as points value in request as documented at localhost:5000/api/ui")


def read_balance():
    """
    This function returns the balance of points for each payer

    :return: Balances, which is a dict of payer: points, aborts with error message if no balance
    """
    if Payers:
        balance = {}
        for payer in Payers:
            count = 0
            for time in Payers[payer]:
                count += int(Payers[payer].get(time))
            balance.update({payer: count})
        print(Payers)
        return balance
    else:
        abort(404, "The balance is 0")


def add_transactions(payer, points, instant):
    """
    This function ingests a transaction with given params and adds it to the Payer container.

    :param payer: String that represents the responsible payer for given points
    :param points: Integer that represents the points the given payer is responsible for
    :param instant: Datetime string that timestamps the transaction
    :return: 201 HTTP status code if successful, abort with error message otherwise
    """
    if (type(payer) == str) and (type(points) == int) and validate_instant(instant):
        if points < 0:
            check_points(points, payer)
        if payer in Payers:
            Payers[payer].update({instant: points})  # Updates Timestamp for transaction
        else:
            Payers.update({payer: {instant: points}})
        TimestampPayer.update({instant: payer})
        Timeline.append(instant)
        return make_response("Transaction has been added", 201)
    elif type(payer) != str:
        abort(400, "Payer param should be a string in request")
    elif type(points) != int:
        abort(400, "Points param should be an integer in request")
    else:
        abort(500, "Did not compute. Please check documentation for your request at localhost:5000/api/ui")


def validate_instant(timestring):
    """
    This function validates that timestamp is formatted correctly.

    :param timestring: Timestamp string to be validated
    :return: True if timestamp is formatted correctly, abort or False otherwise
    """
    if type(timestring) == str:
        try:
            datetime.strptime(timestring, "%Y-%m-%dT%H:%M:%SZ")
        except TypeError:
            abort(400, "Timestamp param should be a string in the form YYYY-MM-DDThh:mm:ssZ")
        except Exception as e:
            abort(500, "Did not compute. Please check documentation for your request at localhost:5000/api/ui")
        return True
    elif type(timestring) == int:
        abort(400, "Timestamp param should be a string in the form YYYY-MM-DDThh:mm:ssZ")
    else:
        abort(500, "Did not compute. Please check documentation for your request at localhost:5000/api/ui")
    return False


def check_points(points, payer):
    """
    This function ensures payer isn't going negative from transaction.

    :param points: Amount to check
    :param payer: Payer to check
    :return: Aborts if payer would go negative
    """
    if sum(Payers[payer].values()) >= points:
        return
    else:
        abort(403, "Not enough points")


def spend_points(total):
    """
    This function "spends" the given amount of points.

    :param total: Amount of points to subtract from Payers according to the rules
    :return: Receipt if successful, abort with error message otherwise
    """
    if type(total) == int and total > 0:
        return remove_points(total)
    else:
        abort(400, "Points param should be a positive integer in request")


def remove_points(points):
    """
    This method removes the specified number of points, from specific payer if given, starting with the oldest transaction.

    :param points: Total points to be removed
    :return: Receipt, aborts with error message otherwise
    """
    balance = 0
    for i in Payers:  # Find total balance
        balance += sum(Payers[i].values())
    if balance >= points:  # Check if we have the points to remove
        receipt = {}
        time_key, pay_key = get_keys()
        check_payer(pay_key, time_key)
        while points > 0:
            time_key, pay_key = get_keys()
            points, spent = subtract_points(pay_key, points, time_key)
            if pay_key in receipt:
                receipt.update({pay_key: (receipt.pop(pay_key) - spent)})
            else:
                receipt.update({pay_key: (-spent)})
        receiptl = []
        for key, value in receipt.items():
            receiptl.append({"payer": key, "points": value})
        return receiptl
    else:
        abort(403, "Not enough points in account")


def get_keys(n=0):
    """
    This method gets the keys for the oldest timestamp viable.

    :param n: Timeline index, defaults to the oldest if called in payer agnostic mode
    :return: Keys needed to access the point value
    """
    time_key = sorted(Timeline)[n]  # Get oldest(or next) timestamp
    pay_key = TimestampPayer[time_key]  # Get associated payer
    return time_key, pay_key


def check_payer(payer, time):
    """
    This function removes any negative transactions before subtracting points

    :param payer: Payer to check for negative transactions
    :param time: timestamp of oldest transaction
    :return:
    """
    oldest = Payers[payer].get(time)
    if not any(x < 0 for x in Payers[payer].values()):
        for key, value in Payers[payer]:
            if value < 0:
                if oldest > value:
                    Payers[payer][time] = (oldest - value)
                else:
                    n = 0
                    pay_key = payer
                    time_key = time
                    while value < 0:
                        if pay_key == payer:
                            value += oldest
                            Payers[pay_key].pop(time_key)
                            TimestampPayer.pop(time_key)
                            Timeline.remove(time_key)
                            time_key, pay_key = get_keys(n + 1)
                        else:
                            n += 1
                            time_key, pay_key = get_keys(n + 1)
                Payers[payer].pop(key)
                TimestampPayer.pop(key)
                Timeline.remove(key)
                return
            else:
                continue
    else:
        return


def subtract_points(pay_key, points, time_key):
    """
    This method removes the specified points from value of time_key of pay_key.

    :param pay_key: Payer to remove points from
    :param points: Amount of points to remove
    :param time_key: Timestamp to remove points for
    :return: Point value still needing to be removed
    """
    spent = points
    current = Payers[pay_key].get(time_key)
    if current > points:
        Payers[pay_key][time_key] = (current - points)
        points = 0
    else:
        points -= current
        Payers[pay_key].pop(time_key)
        TimestampPayer.pop(time_key)
        Timeline.remove(time_key)
    return points, (spent - points)
