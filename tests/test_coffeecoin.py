from brownie import accounts, CoffeeCoin
import brownie


def deploy_token():
    minter = accounts[0]
    user = accounts[1]
    contract = minter.deploy(CoffeeCoin)
    return user, minter, contract,


def test_name():
    user, minter, contract = deploy_token()
    assert contract.name() == "CoffeeWarCoin"


def test_symbol():
    user, minter, contract = deploy_token()
    assert contract.symbol() == "CWC"


def test_decimals():
    user, minter, contract = deploy_token()
    assert contract.decimals() == 18


def test_totalSupply():
    user, minter, contract = deploy_token()
    assert contract.totalSupply() == 8 * 10 ** (8 + 18);


def test_balanceOf():
    user, minter, contract = deploy_token()
    assert contract.balanceOf(user) == 0
    assert contract.balanceOf(minter) == contract.totalSupply()


def test_allowance_and_approve():
    user, minter, contract = deploy_token()
    contract.frozeTransactions(False)
    assert contract.allowance(minter, user) == 0
    assert contract.allowance(user, minter) == 0

    contract.approve(user, 100)
    assert contract.allowance(minter, user) == 100

    try:
        contract.approve(minter, 100)
        assert False
    except brownie.exceptions.VirtualMachineError:
        assert True

    try:
        contract.approve(minter, 100, {'from': user})
        assert False
    except brownie.exceptions.VirtualMachineError as e:
        assert True

    try:
        contract.approve(user, 0)
        assert False
    except brownie.exceptions.VirtualMachineError:
        assert True

    contract.frozeTransactions(True)
    try:
        contract.approve(user, 100)  # require(frozenTransactions != true, "frozenTransactions != true");
        assert False
    except brownie.exceptions.VirtualMachineError:
        assert True


def test_transfer():

    user, minter, contract = deploy_token()
    contract.frozeTransactions(False)
    try:  # require(balances[msg.sender] >= tokens, "Check balance");
        contract.transfer(minter, 100, {'from': user})
        assert False
    except brownie.exceptions.VirtualMachineError:
        assert True

    try:  # You can't transfer coins to your account"
        contract.transfer(minter, 100, {'from': minter})
        assert False
    except brownie.exceptions.VirtualMachineError:
        assert True

    try:  # "tokens should be > 0"
        contract.transfer(user, 0, {'from': minter})
        assert False
    except brownie.exceptions.VirtualMachineError:
        assert True

    contract.transfer(user, 100, {'from': minter})
    assert contract.balanceOf(user) == 100

    contract.transfer(minter, 100, {'from': user})
    assert contract.balanceOf(user) == 0

    contract.frozeTransactions(True)
    try:
        contract.transfer(user, 100)  # require(frozenTransactions != true, "frozenTransactions != true");
        assert False
    except brownie.exceptions.VirtualMachineError:
        assert True


def test_transferFrom():
    user, minter, contract = deploy_token()
    contract.frozeTransactions(False)
    try:  # "Use Transfer for this");
        contract.transferFrom(minter, user, 100, {'from': minter})
        assert False
    except brownie.exceptions.VirtualMachineError:
        assert True

    contract.transfer(user, 150)
    contract.approve(minter, 100, {'from': user})

    try:  # "balances[from]>= tokens");
        contract.transferFrom(user, minter, 200, {'from': minter})
        assert False
    except brownie.exceptions.VirtualMachineError:
        assert True

    try:  # "allowed[from][msg.sender] >=  tokens"
        contract.transferFrom(user, minter, 102, {'from': minter})
        assert False
    except brownie.exceptions.VirtualMachineError:
        assert True

    try:  # "tokens > 0"
        contract.transferFrom(user, minter, 0, {'from': minter})
        assert False
    except brownie.exceptions.VirtualMachineError:
        assert True

    contract.frozeTransactions(True)
    try:
        contract.transferFrom(user, minter, 1, {'from': minter})  # require(frozenTransactions != true, "frozenTransactions != true");
        assert False
    except brownie.exceptions.VirtualMachineError:
        assert True
    contract.frozeTransactions(False)

    contract.transferFrom(user, minter, 1, {'from': minter})  # Base operations
    assert contract.balanceOf(minter) == 8 * 10 ** (8 + 18) - 149





def test_burn():
    user, minter, contract = deploy_token()

    try:  # balances[msg.sender] >= amount
        contract.burn(100, {'from': user})
        assert False
    except brownie.exceptions.VirtualMachineError:
        assert True

    try:  # "ERC20: amount > 0");
        contract.burn(0, {'from': user})
        assert False
    except brownie.exceptions.VirtualMachineError:
        assert True

    contract.burn(150, {'from': minter})

    assert contract.balanceOf(minter) == 8 * 10 ** (8 + 18) - 150


def test_mint():
    user, minter, contract = deploy_token()
    try:  # "ERC20: amount > 0");
        contract.mint(user, 0, {'from': minter})
        assert False
    except brownie.exceptions.VirtualMachineError:
        assert True

    try:  # "ERC20: only the creator of the smart contract can add new tokens to the balance
        contract.mint(minter, 1000, {'from': user})
        assert False
    except brownie.exceptions.VirtualMachineError:
        assert True

    contract.mint(user, 1000, {'from': minter})
    contract.setICOContractAddress(user, {'from': minter})
    contract.mint(user, 1000, {'from': user})

    assert contract.totalSupply() == 8 * 10 ** (8 + 18) + 2000
    assert contract.balanceOf(user) == 2000


def test_events():
    user, minter, contract = deploy_token()
    contract.frozeTransactions(False)
    assert "Transfer" in contract.tx.events.keys()
    assert contract.tx.events["Transfer"][0][0]["_from"] == "0x0000000000000000000000000000000000000000"
    assert contract.tx.events["Transfer"][0][0]["_to"] == minter.address
    assert contract.tx.events["Transfer"][0][0]["_value"] == 8 * 10 ** (8 + 18)

    events = contract.approve(user, 100, {"from": minter}).events

    assert "Approval" in events.keys()
    assert events["Approval"][0][0]["_owner"] == minter.address
    assert events["Approval"][0][0]["_spender"] == user.address
    assert events["Approval"][0][0]["_value"] == 100

    events = contract.transfer(user, 100, {"from": minter}).events

    assert "Transfer" in events.keys()
    assert events["Transfer"][0][0]["_from"] == minter.address
    assert events["Transfer"][0][0]["_to"] == user.address
    assert events["Transfer"][0][0]["_value"] == 100

    events = contract.transferFrom(minter, user, 100, {"from": user}).events

    assert "Transfer" in events.keys()
    assert events["Transfer"][0][0]["_from"] == minter.address
    assert events["Transfer"][0][0]["_to"] == user.address
    assert events["Transfer"][0][0]["_value"] == 100

    events = contract.mint(user, 100, {"from": minter}).events

    assert "Transfer" in events.keys()
    assert events["Transfer"][0][0]["_from"] == "0x0000000000000000000000000000000000000000"
    assert events["Transfer"][0][0]["_to"] == user.address
    assert events["Transfer"][0][0]["_value"] == 100

    events = contract.burn(100, {"from": minter}).events
    assert "Transfer" in events.keys()
    assert events["Transfer"][0][0]["_from"] == minter.address
    assert events["Transfer"][0][0]["_to"] == "0x0000000000000000000000000000000000000000"
    assert events["Transfer"][0][0]["_value"] == 100


def test_frozeTransactions():
    user, minter, contract = deploy_token()

    try:  # "ERC20: only the creator of the smart contract can add new tokens to the balance
        contract.frozeTransactions(False, {"from": user})
        assert False
    except brownie.exceptions.VirtualMachineError:
        assert True
    contract.setICOContractAddress(user, {'from': minter})
    contract.frozeTransactions(True, {"from": user})
    contract.frozeTransactions(True, {"from": minter})
    contract.frozeTransactions(False, {"from": minter})

def test_setICOContractAddress():
    user, minter, contract = deploy_token()
    contract.setICOContractAddress(user, {'from': minter})
    try:  # "ERC20: "msg.sender == minter");
        contract.setICOContractAddress(minter, {"from": user})
        assert False
    except brownie.exceptions.VirtualMachineError:
        assert True