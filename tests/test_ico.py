from brownie import accounts, CoffeeCoin, CoffeeICO, web3
import brownie


def deploy_token():
    minter = accounts[0]
    user = accounts[1]
    contract = minter.deploy(CoffeeCoin)

    ico = accounts[0].deploy(CoffeeICO, contract, 3, web3.toWei("3", "ether"), web3.toWei("5", "ether"))
    contract.setICOContractAddress(ico, {"from": minter})
    return user, minter, contract, ico


def test_contribute():
    user, minter, contract, ico = deploy_token()
    ico.contribute({'from': user, 'value': web3.toWei("3", "wei")})
    assert ico.isOpen() is True and contract.frozenTransactions() is True

    ico.contribute({'from': user, 'value': web3.toWei("4", "ether")})  # Softcap
    assert ico.isOpen() is True and contract.frozenTransactions() is False

    ico.contribute({'from': user, 'value': web3.toWei("6", "ether")})  # Hardcap
    assert ico.isOpen() is False and contract.frozenTransactions() is False

    user, minter, contract, ico = deploy_token()
    ico.contribute({'from': user, 'value': web3.toWei("6", "ether")})  # Hardcap
    assert ico.isOpen() is False and contract.frozenTransactions() is False

    user, minter, contract, ico = deploy_token()

    try:
        ico.contribute({'from': user, 'value': 0})  # msg.value>0"
        assert False
    except brownie.exceptions.VirtualMachineError:
        assert True

    ico.closeICO({"from": minter})
    try:
        ico.contribute({'from': user, 'value': 4})  # isOpen
        assert False
    except brownie.exceptions.VirtualMachineError:
        assert True


def test_close():
    user, minter, contract, ico = deploy_token()

    try:
        ico.closeICO({"from": user})  # msg.sender == mintor,
        assert False
    except brownie.exceptions.VirtualMachineError:
        assert True

    assert ico.isOpen() == True
    ico.closeICO({"from": minter})
    assert ico.isOpen() == False
