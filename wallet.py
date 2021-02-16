import subprocess
from subprocess import Popen,PIPE
import json
from web3 import Web3
#from web3.auto.gethdev import w3
from constants import BTC, ETH, BTCTEST
from pprint import pprint
from bit import PrivateKeyTestnet
from bit.network import NetworkAPI
from web3 import Web3, middleware, Account
from web3.gas_strategies.time_based import medium_gas_price_strategy
from web3.middleware import geth_poa_middleware
import os
from dotenv import load_dotenv
from pathlib import Path
from getpass import getpass
config = load_dotenv()

import constants

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

#w3.eth.setGasPriceStrategy(medium_gas_price_strategy)

# latest_block = w3.eth.blockNumber
# print(latest_block)

# balance_node1 = w3.eth.getBalance('0xEA2fd54e74428ED37CD5c843D9c023bFaBb6588F')
# print(balance_node1)


# private_key="0x4ec846fe37112d968395ba56b7cebf7e775b30d1aca72b9fcfeecd0294d11146"
# my_account = Account.from_key(private_key)

#print(my_account.address)

#including a mnemonic with prefunded test tokens for testing
mnemonic = os.getenv('MNEMONIC')

# command = './derive -g --mnemonic --cols=path,address,privkey,pubkey --format=json'
# p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
# (output, error) = p.communicate()
# p_status = p.wait()
# keys = json.loads(output)
# print(keys)


def derive_wallets(coin=BTC, mnemonic=mnemonic, depth=3):
    subst = { "coin": coin, "mnemonic": mnemonic, "depth": depth, "format": "json" }
    command =  "php derive -g --mnemonic='{mnemonic}' --coin={coin} --numderive={depth} --format={format} ".format(**subst)
    print("COMMAND " + command)
    p = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        shell=True)
    output, err = p.communicate()
    print("OUTPUT " + str(output) + " \n ERROR " + str(err))
    p_status = p.wait()
    keys = json.loads(output)
    return keys


def priv_key_to_account(coin, priv_key):
    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    if coin == BTCTEST:
        return PrivateKeyTestnet(priv_key)


def create_raw_tx(coin, account, recipient, amount):
    if coin == ETH:
        gasEstimate = w3.eth.estimateGas(
        {"from": account.address, "to": recipient, "value": amount}
        )
        return {
        "from": account.address,
        "to": recipient,
        "value": amount,
        "gasPrice": w3.eth.gasPrice,
        "gas": gasEstimate,
        "nonce": w3.eth.getTransactionCount(account.address),
        "chainId": w3.net.chainId,
    }
    
    if coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(recipient, amount, BTC)])

def send_tx(coin, account, to, amount):
    if coin == ETH:
        raw_tx = create_raw_tx(coin, account, to, amount)
        signed = account.signTransaction(raw_tx)
        return w3.eth.sendRawTransaction(signed.rawTransaction)
    if coin == BTCTEST:
        raw_tx = create_raw_tx(coin, account, to, amount)
        signed = account.sign_transaction(raw_tx)
        return NetworkAPI.broadcast_tx_testnet(signed)

coins = {
    ETH: derive_wallets(ETH),
    BTCTEST: derive_wallets(BTCTEST)
}

print(coin)

#coins[BTC][0]['privkey']