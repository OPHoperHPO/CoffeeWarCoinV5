from brownie import CoffeeCoin, accounts


def main():
    # data = json.load(open("vars.json"))
    # os.environ["WEB3_INFURA_PROJECT_ID"] = data["WEB3_INFURA_PROJECT_ID"]  # Deploy to Ropsten blockchain
    # os.environ["PRIVATE_KEY"] = data["PRIVATE_KEY"]

    # priv_key = web3.eth.account.decrypt(
    #     json.loads(data["DEPLOY_ACCOUNT"]), data["DEPLOY_ACCOUNT_PASSWORD"])
    # acct = accounts.add(private_key=priv_key)

    # tx = acct.deploy(CoffeeCoin, gas_limit=8000000, gas_price=web3.toWei("5", "gwei"))

    acct = accounts[0]  # Deploy to local Ganache
    tx = acct.deploy(CoffeeCoin, gas_limit=3999999, gas_price=0)
