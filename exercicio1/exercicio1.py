import csv
import operator
from pathlib import Path
from datetime import datetime, timedelta


def drop_duplicates(transaction):
    distinct_transactions = set(tuple(x) for x in transaction)
    distinct_transactions = [dict(zip(('date', 'department', 'mkt_value', 'beneficiary'), element)) for element in
                             distinct_transactions]
    return distinct_transactions


def calculate_possible_transaction_dates(transactions):
    updated_transactions = []
    for transaction in transactions:
        initial_date = transaction.get('date')
        datetime_date = datetime.strptime(initial_date, '%Y-%m-%d').date()

        list_of_possible_transaction_dates = []
        for day in [-1, 0, 1]:
            new_date = datetime_date + timedelta(days=day)
            list_of_possible_transaction_dates.append(new_date)

        transaction['list_of_possible_transaction_dates'] = sorted(list_of_possible_transaction_dates)
        updated_transactions.append(transaction)
    return updated_transactions


def reconcile_accounts(transactions_1, transactions_2):
    distinct_transactions_1 = drop_duplicates(transactions_1)
    distinct_transactions_2 = drop_duplicates(transactions_2)

    list_transactions_1 = calculate_possible_transaction_dates(distinct_transactions_1)
    transactions_2_with_match = []

    # Check if there is a match between transactions from both lists
    for transaction_1 in list_transactions_1:
        match_candidates = []
        tuple_transaction_1 = operator.itemgetter('department', 'mkt_value', 'beneficiary')(transaction_1)

        for transaction_2 in distinct_transactions_2:
            tuple_transaction_2 = operator.itemgetter('department', 'mkt_value', 'beneficiary')(transaction_2)
            if tuple_transaction_1 == tuple_transaction_2:
                match_candidates.append(transaction_2)

        if match_candidates:
            transaction_matched = False
            for possible_transaction_date in transaction_1.get('list_of_possible_transaction_dates'):
                if not transaction_matched:
                    for transaction_2 in match_candidates:
                        transaction_candidate_2 = transaction_2.get('date')
                        transaction_candidate_2 = datetime.strptime(transaction_candidate_2, '%Y-%m-%d').date()
                        if transaction_candidate_2 == possible_transaction_date:
                            # Making sure that no transactions is matched twice to each transaction on transaction2 file
                            if transaction_2 not in transactions_2_with_match:
                                transaction_1['status'] = 'FOUND'
                                transactions_2_with_match.append(transaction_2)
                                transaction_matched = True
                                break
                            else:
                                transaction_1['status'] = 'MISSING'
                else:
                    break
        else:
            transaction_1['status'] = 'MISSING'

    # Add status for transactions 2 that had no match
    transactions_2_with_no_match = [{**transaction, 'status': 'MISSING'} for transaction in distinct_transactions_2 if
                                    transaction not in transactions_2_with_match]

    # Add status for transactions 2 that had a match
    transactions_2_with_match = [{**transaction, 'status': 'FOUND'} for transaction in transactions_2_with_match]

    # Combine matching and non-matching transactions from transactions_2
    result_transaction_2 = transactions_2_with_no_match + transactions_2_with_match
    result_transaction_2 = [list(transaction.values()) for transaction in result_transaction_2]

    # Remove 'list_of_possible_transaction_dates' key from all transactions in transactions_1
    for dictionary in list_transactions_1:
        dictionary.pop('list_of_possible_transaction_dates', None)

    result_transaction_1 = [list(transaction.values()) for transaction in list_transactions_1]
    return result_transaction_1, result_transaction_2


if __name__ == "__main__":
    transactions1 = list(csv.reader(Path('transactions1.csv').open(encoding='utf-8')))
    transactions2 = list(csv.reader(Path('transactions2.csv').open(encoding='utf-8')))
    out1, out2 = reconcile_accounts(transactions1, transactions2)
