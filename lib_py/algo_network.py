# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/04_algo_network.ipynb (unless otherwise specified).

__all__ = ['NetworkInteraction', 'get_default_suggested_params', 'ApplicationTransactionRepository',
           'ASATransactionRepository', 'PaymentTransactionRepository']

# Cell

import base64
from typing import Optional

from algosdk.future.transaction import SignedTransaction
from algosdk.v2client import algod


class NetworkInteraction:
    @staticmethod
    def wait_for_confirmation(client: algod.AlgodClient, txid, log=True):
        """
        Utility function to wait until the transaction is
        confirmed before proceeding.
        """
        print('1:NetworkInteraction.wait_for_confirmation')
        last_round = client.status().get('last-round')
        txinfo = client.pending_transaction_info(txid)
        while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
            if log:
                print("Waiting for confirmation")
            print('1:NetworkInteraction.wait_for_confirmation', {'last_round': last_round, 'txinfo': txinfo})
            last_round += 1
            client.status_after_block(last_round)
            txinfo = client.pending_transaction_info(txid)
        if log:
            print(f"Transaction {txid} confirmed in round {txinfo.get('confirmed-round')}.")
        return txinfo

    @staticmethod
    def get_default_suggested_params(client: algod.AlgodClient):
        """
        Gets default suggested params with flat transaction fee and fee amount of 1000.
        :param client:
        :return:
        """
        print('1:NetworkInteraction.get_default_suggested_params')
        suggested_params = client.suggested_params()

        suggested_params.flat_fee = True
        suggested_params.fee = 1000

        return suggested_params

    @staticmethod
    def submit_asa_creation(client: algod.AlgodClient, transaction: SignedTransaction) -> Optional[int]:
        """
        Submits a ASA creation transaction to the network. If the transaction is successful the ASA's id is returned.
        :param client:
        :param transaction:
        :return:
        """
        print('1:NetworkInteraction.submit_asa_creation')
        txid = client.send_transaction(transaction)

        NetworkInteraction.wait_for_confirmation(client, txid)

        try:
            ptx = client.pending_transaction_info(txid)
            return ptx["asset-index"]
        except Exception as e:
            # TODO: Proper logging needed.
            print(e)
            print('Unsuccessful creation of Algorand Standard Asset.')

    @staticmethod
    def submit_transaction(client: algod.AlgodClient, transaction: SignedTransaction, log=True) -> Optional[str]:
        print('1:NetworkInteraction.submit_transaction')
        txid = client.send_transaction(transaction)

        NetworkInteraction.wait_for_confirmation(client, txid, log)

        return txid

    @staticmethod
    def compile_program(client: algod.AlgodClient, source_code):
        """
        :param client: algorand client
        :param source_code: teal source code
        :return:
            Decoded byte program
        """
        print('1:NetworkInteraction.compile_program')
        compile_response = client.compile(source_code)
        return base64.b64decode(compile_response['result'])

# Cell

import base64
from algosdk.v2client import algod
from algosdk.future import transaction as algo_txn
from typing import List, Any, Optional, Union
from algosdk import account as algo_acc
from algosdk.future.transaction import Transaction, SignedTransaction


def get_default_suggested_params(client: algod.AlgodClient):
    """
    Gets default suggested params with flat transaction fee and fee amount of 1000.
    :param client:
    :return:
    """
    print('2:get_default_suggested_params')
    suggested_params = client.suggested_params()

    suggested_params.flat_fee = True
    suggested_params.fee = 1000

    return suggested_params



# Cell

class ApplicationTransactionRepository:
    """
    Initializes transaction related to applications.
    """

    @classmethod
    def create_application(cls,
                           client: algod.AlgodClient,
                           creator_private_key: str,
                           approval_program: bytes,
                           clear_program: bytes,
                           global_schema: algo_txn.StateSchema,
                           local_schema: algo_txn.StateSchema,
                           app_args: Optional[List[Any]],
                           sign_transaction: bool = True) -> Union[Transaction, SignedTransaction]:
        """
        Initiates a transaction that represents application creation. The transaction is optionally signed using the
        provided private key.
        :param client: algorand client.
        :param creator_private_key: private key of the creator of the application.
        :param approval_program: encoded source code in bytes for the approval program.
        :param clear_program: encoded source code in bytes for the clear program.
        :param global_schema: global schema for the application.
        :param local_schema: local schema for the application.
        :param app_args: list of arguments for the application.
        :param sign_transaction: boolean value that determines whether the created transaction should be signed or not.
        :return:
            Returns SignedTransaction or Transaction depending on the boolean property sign_transaction.
        """
        print('2:ApplicationTransactionRepository.create_application')
        creator_address = algo_acc.address_from_private_key(private_key=creator_private_key)
        suggested_params = get_default_suggested_params(client=client)

        txn = algo_txn.ApplicationCreateTxn(sender=creator_address,
                                            sp=suggested_params,
                                            on_complete=algo_txn.OnComplete.NoOpOC.real,
                                            approval_program=approval_program,
                                            clear_program=clear_program,
                                            global_schema=global_schema,
                                            local_schema=local_schema,
                                            app_args=app_args)

        if sign_transaction:
            txn = txn.sign(private_key=creator_private_key)

        return txn

    @classmethod
    def call_application(cls,
                         client: algod.AlgodClient,
                         caller_private_key: str,
                         app_id: int,
                         on_complete: algo_txn.OnComplete,
                         app_args: Optional[List[Any]] = None,
                         sign_transaction: bool = True) -> Union[Transaction, SignedTransaction]:
        """
        Creates a transaction that represents an application call.
        :param client: algorand client.
        :param caller_private_key: the private key of the caller of the application.
        :param app_id: the application id which identifies the app.
        :param on_complete: Type of the application call.
        :param app_args: Arguments of the application.
        :param sign_transaction: boolean value that determines whether the created transaction should be signed or not.
        :return:
        Returns SignedTransaction or Transaction depending on the boolean property sign_transaction.
        """
        print('2:ApplicationTransactionRepository.call_application')
        caller_address = algo_acc.address_from_private_key(private_key=caller_private_key)
        suggested_params = get_default_suggested_params(client=client)

        txn = algo_txn.ApplicationCallTxn(sender=caller_address,
                                          sp=suggested_params,
                                          index=app_id,
                                          app_args=app_args,
                                          on_complete=on_complete)

        if sign_transaction:
            txn = txn.sign(private_key=caller_private_key)

        return txn


# Cell

class ASATransactionRepository:
    """
    Initializes transactions related to Algorand Standard Assets
    """

    @classmethod
    def create_asa(cls,
                   client: algod.AlgodClient,
                   creator_private_key: str,
                   unit_name: str,
                   asset_name: str,
                   total: int,
                   decimals: int,
                   note: Optional[bytes] = None,
                   manager_address: Optional[str] = None,
                   reserve_address: Optional[str] = None,
                   freeze_address: Optional[str] = None,
                   clawback_address: Optional[str] = None,
                   url: Optional[str] = None,
                   default_frozen: bool = False,
                   sign_transaction: bool = True) -> Union[Transaction, SignedTransaction]:
        """
        :param client:
        :param creator_private_key:
        :param unit_name:
        :param asset_name:
        :param total:
        :param decimals:
        :param note:
        :param manager_address:
        :param reserve_address:
        :param freeze_address:
        :param clawback_address:
        :param url:
        :param default_frozen:
        :param sign_transaction:
        :return:
        """
        print('2:ASATransactionRepository.create_application')

        suggested_params = get_default_suggested_params(client=client)

        creator_address = algo_acc.address_from_private_key(private_key=creator_private_key)

        txn = algo_txn.AssetConfigTxn(sender=creator_address,
                                      sp=suggested_params,
                                      total=total,
                                      default_frozen=default_frozen,
                                      unit_name=unit_name,
                                      asset_name=asset_name,
                                      manager=manager_address,
                                      reserve=reserve_address,
                                      freeze=freeze_address,
                                      clawback=clawback_address,
                                      url=url,
                                      decimals=decimals,
                                      note=note)

        if sign_transaction:
            txn = txn.sign(private_key=creator_private_key)

        return txn

    @classmethod
    def create_non_fungible_asa(cls,
                                client: algod.AlgodClient,
                                creator_private_key: str,
                                unit_name: str,
                                asset_name: str,
                                note: Optional[bytes] = None,
                                manager_address: Optional[str] = None,
                                reserve_address: Optional[str] = None,
                                freeze_address: Optional[str] = None,
                                clawback_address: Optional[str] = None,
                                url: Optional[str] = None,
                                default_frozen: bool = False,
                                sign_transaction: bool = True) -> Union[Transaction, SignedTransaction]:
        """
        :param client:
        :param creator_private_key:
        :param unit_name:
        :param asset_name:
        :param note:
        :param manager_address:
        :param reserve_address:
        :param freeze_address:
        :param clawback_address:
        :param url:
        :param default_frozen:
        :param sign_transaction:
        :return:
        """
        print('2:ASATransactionRepository.create_non_fungible_asa')

        return ASATransactionRepository.create_asa(client=client,
                                                   creator_private_key=creator_private_key,
                                                   unit_name=unit_name,
                                                   asset_name=asset_name,
                                                   total=1,
                                                   decimals=0,
                                                   note=note,
                                                   manager_address=manager_address,
                                                   reserve_address=reserve_address,
                                                   freeze_address=freeze_address,
                                                   clawback_address=clawback_address,
                                                   url=url,
                                                   default_frozen=default_frozen,
                                                   sign_transaction=sign_transaction)

    @classmethod
    def asa_opt_in(cls,
                   client: algod.AlgodClient,
                   sender_private_key: str,
                   asa_id: int,
                   sign_transaction: bool = True) -> Union[Transaction, SignedTransaction]:
        """
        Opts-in the sender's account to the specified asa with an id: asa_id.
        :param client:
        :param sender_private_key:
        :param asa_id:
        :param sign_transaction:
        :return:
        """
        print('2:ASATransactionRepository.asa_opt_in')

        suggested_params = get_default_suggested_params(client=client)
        sender_address = algo_acc.address_from_private_key(sender_private_key)

        txn = algo_txn.AssetTransferTxn(sender=sender_address,
                                        sp=suggested_params,
                                        receiver=sender_address,
                                        amt=0,
                                        index=asa_id)

        if sign_transaction:
            txn = txn.sign(private_key=sender_private_key)

        return txn

    @classmethod
    def asa_transfer(cls,
                     client: algod.AlgodClient,
                     sender_address: str,
                     receiver_address: str,
                     asa_id: int,
                     amount: int,
                     revocation_target: Optional[str],
                     sender_private_key: Optional[str],
                     sign_transaction: bool = True) -> Union[Transaction, SignedTransaction]:
        """
        :param client:
        :param sender_address:
        :param receiver_address:
        :param asa_id:
        :param amount:
        :param revocation_target:
        :param sender_private_key:
        :param sign_transaction:
        :return:
        """
        print('2:ASATransactionRepository.asa_transfer')
        suggested_params = get_default_suggested_params(client=client)

        txn = algo_txn.AssetTransferTxn(sender=sender_address,
                                        sp=suggested_params,
                                        receiver=receiver_address,
                                        amt=amount,
                                        index=asa_id,
                                        revocation_target=revocation_target)

        if sign_transaction:
            txn = txn.sign(private_key=sender_private_key)

        return txn

    @classmethod
    def change_asa_management(cls,
                              client: algod.AlgodClient,
                              current_manager_pk: str,
                              asa_id: int,
                              manager_address: Optional[str] = None,
                              reserve_address: Optional[str] = None,
                              freeze_address: Optional[str] = None,
                              clawback_address: Optional[str] = None,
                              strict_empty_address_check: bool = True,
                              sign_transaction: bool = True) -> Union[Transaction, SignedTransaction]:
        """
        Changes the management properties of a given ASA.
        :param client:
        :param current_manager_pk:
        :param asa_id:
        :param manager_address:
        :param reserve_address:
        :param freeze_address:
        :param clawback_address:
        :param strict_empty_address_check:
        :param sign_transaction:
        :return:
        """
        print('2:ASATransactionRepository.change_asa_management')

        params = get_default_suggested_params(client=client)

        current_manager_address = algo_acc.address_from_private_key(private_key=current_manager_pk)

        txn = algo_txn.AssetConfigTxn(
            sender=current_manager_address,
            sp=params,
            index=asa_id,
            manager=manager_address,
            reserve=reserve_address,
            freeze=freeze_address,
            clawback=clawback_address,
            strict_empty_address_check=strict_empty_address_check)

        if sign_transaction:
            txn = txn.sign(private_key=current_manager_pk)

        return txn


# Cell

class PaymentTransactionRepository:

    @classmethod
    def payment(cls,
                client: algod.AlgodClient,
                sender_address: str,
                receiver_address: str,
                amount: int,
                sender_private_key: Optional[str],
                sign_transaction: bool = True) -> Union[Transaction, SignedTransaction]:
        """
        Creates a payment transaction in ALGOs.
        :param client:
        :param sender_address:
        :param receiver_address:
        :param amount:
        :param sender_private_key:
        :param sign_transaction:
        :return:
        """
        print('2:PaymentTransactionRepository.payment')
        suggested_params = get_default_suggested_params(client=client)

        txn = algo_txn.PaymentTxn(sender=sender_address,
                                  sp=suggested_params,
                                  receiver=receiver_address,
                                  amt=amount)

        if sign_transaction:
            txn = txn.sign(private_key=sender_private_key)

        return txn