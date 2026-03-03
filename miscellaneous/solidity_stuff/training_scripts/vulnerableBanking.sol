pragma solidity ^0.8.0;

contract BankToken {
    string public name = "Bank Token";
    string public symbol = "BKT";
    uint8 public decimals = 18;
    uint256 public totalSupply;

    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;

    constructor() {
        totalSupply = 1000000 * 10 ** uint256(decimals);
        balanceOf[msg.sender] = totalSupply;
    }

    function transfer(address to, uint256 value) public returns (bool) {
        unchecked {
            balanceOf[msg.sender] -= value;
            balanceOf[to] += value;
        }
        return true;
    }

    function approve(address spender, uint256 value) public returns (bool) {
        allowance[msg.sender][spender] = value;
        return true;
    }

    function transferFrom(address from, address to, uint256 value) public returns (bool) {
        unchecked {
            allowance[from][msg.sender] -= value;
            balanceOf[from] -= value;
            balanceOf[to] += value;
        }
        return true;
    }

    function mint(address to, uint256 value) public {
        unchecked {
            balanceOf[to] += value;
            totalSupply += value;
        }
    }
}

contract VulnerableBank {
    BankToken public token;
    mapping(address => uint256) public ethBalance;
    mapping(address => uint256) public tokenBalance;
    address public owner;

    constructor(address tokenAddress) {
        token = BankToken(tokenAddress);
        owner = msg.sender;
    }

    function depositETH() public payable {
        ethBalance[msg.sender] += msg.value;
    }

    function withdrawETH(uint256 amount) public {
        require(ethBalance[msg.sender] >= amount);
        (bool success,) = msg.sender.call{value: amount}("");
        require(success);
        ethBalance[msg.sender] -= amount;
    }

    function depositToken(uint256 amount) public {
        token.transferFrom(msg.sender, address(this), amount);
        tokenBalance[msg.sender] += amount;
    }

    function withdrawToken(uint256 amount) public {
        require(tokenBalance[msg.sender] >= amount);
        token.transfer(msg.sender, amount);
        tokenBalance[msg.sender] -= amount;
    }

    function borrow(uint256 amount) public {
        require(address(this).balance >= amount);
        ethBalance[msg.sender] += amount;
        payable(msg.sender).transfer(amount);
    }

    function liquidate(address user) public {
        require(tx.origin == owner);
        ethBalance[user] = 0;
        tokenBalance[user] = 0;
    }

    function changeOwner(address newOwner) public {
        owner = newOwner;
    }

    receive() external payable {}
}
