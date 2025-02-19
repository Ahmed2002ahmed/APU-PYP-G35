# -*- coding: utf-8 -*-
import os
from datetime import datetime

# 常量定义
USER_FILE = "users.txt"
ACCOUNT_FILE = "accounts.txt"
TRANSACTION_FILE = "transactions.txt"
BILL_FILE = "bills.txt"

def main():
    """主程序入口"""
    current_user = login()
    if not current_user:
        print("Login failed")
        return
    
    while True:
        print("\nCustomer Menu:")
        print("1. Check account balance")
        print("2. Transfer funds")
        print("3. Pay bills")
        print("4. Request account statement")
        print("5. Update contact information")
        print("0. Exit")
        
        choice = input("Please enter the operation number:")
        
        if choice == "1":
            check_balance(current_user["UserID"])
        elif choice == "2":
            transfer_funds(current_user["UserID"])
        elif choice == "3":
            pay_bills(current_user["UserID"])
        elif choice == "4":
            request_statement(current_user["UserID"])
        elif choice == "5":
            update_contact(current_user["UserID"])
        elif choice == "0":
            break
        else:
            print("Invalid input, please try again")

# ----------------------
# 核心功能实现
# ----------------------
#123
def login():
    """用户登录"""
    username = input("Username:")
    password = input("Password:")
    
    users = read_data_file(USER_FILE)
    for user in users:
        if user.get("Username") == username and user.get("Password") == password:
            if user.get("Role") == "customer":
                return user
    return None

def check_balance(user_id):
    """功能1：检查余额"""
    account = get_user_account(user_id)
    if account:
        print(f"Current balance: {account['Balance']}")
    else:
        print("Account information not found")

def transfer_funds(user_id):
    """功能2：转账"""
    # 获取源账户
    from_account = get_user_account(user_id)
    if not from_account:
        print("Account does not exist")
        return
    
    # 输入转账信息
    to_account_id = input("Target account ID:")
    amount = float(input("Transfer amount:"))
    
    # 验证目标账户
    to_account = get_account_by_id(to_account_id)
    if not to_account:
        print("Invalid target account")
        return
    
    # 验证余额
    if float(from_account["Balance"]) < amount:
        print("Insufficient balance")
        return
    
    # 执行转账
    new_from_balance = float(from_account["Balance"]) - amount
    new_to_balance = float(to_account["Balance"]) + amount
    
    # 更新账户文件
    update_account_balance(from_account["AccountID"], new_from_balance)
    update_account_balance(to_account_id, new_to_balance)
    
    # 记录交易
    record_transaction(
        from_account["AccountID"],
        "transfer",
        -amount,
        target_account=to_account_id
    )
    record_transaction(
        to_account_id,
        "transfer",
        amount,
        source_account=from_account["AccountID"]
    )
    
    print("Transfer successful")

def pay_bills(user_id):
    """功能3：支付账单"""
    account = get_user_account(user_id)
    if not account:
        return
    
    # 获取未付账单
    bills = [
        b for b in read_data_file(BILL_FILE)
        if b["AccountID"] == account["AccountID"] and b["Status"] == "unpaid"
    ]
    
    if not bills:
        print("No unpaid bills")
        return
    
    print("Unpaid bills:")
    for i, bill in enumerate(bills, 1):
        print(f"{i}. {bill['BillType']} - {bill['Amount']}")
    
    selection = int(input("Select the bill number to pay:")) - 1
    if 0 <= selection < len(bills):
        pay_bill(bills[selection]["BillID"], account["AccountID"])
    else:
        print("Invalid selection")

def request_statement(user_id):
    """功能4：生成账户报表"""
    account = get_user_account(user_id)
    if not account:
        return
    
    transactions = [
        t for t in read_data_file(TRANSACTION_FILE)
        if t["AccountID"] == account["AccountID"]
    ]
    
    filename = f"statement_{account['AccountID']}_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(filename, "w") as f:
        f.write(f"Account Statement {datetime.now()}\n")
        f.write(f"Account ID: {account['AccountID']}\n")
        f.write(f"Current balance: {account['Balance']}\n")
        f.write("\nTransaction records:\n")
        for t in transactions:
            f.write(f"{t['Date']} | {t['Type']} | {t['Amount']}\n")
    
    print(f"Statement generated: {filename}")

def update_contact(user_id):
    """功能5：更新联系方式"""
    users = read_data_file(USER_FILE)
    for user in users:
        if user["UserID"] == user_id:
            new_contact = input("New contact information:")
            user["Contact"] = new_contact
            write_data_file(USER_FILE, users)
            print("Contact information updated")
            return
    print("User does not exist")

# ----------------------
# 通用文件操作函数
# ----------------------

def read_data_file(filename):
    """通用文件读取函数"""
    data = []
    if not os.path.exists(filename):
        return []
    
    with open(filename, "r") as f:
        blocks = f.read().split("===")
        for block in blocks:
            if block.strip():
                record = {}
                for line in block.strip().split("\n"):
                    if ": " in line:
                        key, value = line.split(": ", 1)
                        record[key] = value
                data.append(record)
    return data

def write_data_file(filename, data):
    """通用文件写入函数"""
    with open(filename, "w") as f:
        for record in data:
            for key, value in record.items():
                f.write(f"{key}: {value}\n")
            f.write("===\n")

# ----------------------
# 辅助函数
# ----------------------

def get_user_account(user_id):
    """获取用户关联的账户"""
    accounts = read_data_file(ACCOUNT_FILE)
    for acc in accounts:
        if acc["UserID"] == user_id and acc["Status"] == "active":
            return acc
    return None

def update_account_balance(account_id, new_balance):
    """更新账户余额"""
    accounts = read_data_file(ACCOUNT_FILE)
    for acc in accounts:
        if acc["AccountID"] == account_id:
            acc["Balance"] = str(new_balance)
            write_data_file(ACCOUNT_FILE, accounts)
            return True
    return False

def record_transaction(account_id, trans_type, amount, **kwargs):
    """记录交易"""
    transaction = {
        "TransactionID": f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "AccountID": account_id,
        "Type": trans_type,
        "Amount": str(amount),
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Status": "completed"
    }
    transaction.update(kwargs)
    
    transactions = read_data_file(TRANSACTION_FILE)
    transactions.append(transaction)
    write_data_file(TRANSACTION_FILE, transactions)

def pay_bill(bill_id, account_id):
    """支付指定账单"""
    bills = read_data_file(BILL_FILE)
    for bill in bills:
        if bill["BillID"] == bill_id and bill["AccountID"] == account_id:
            bill["Status"] = "paid"
            bill["PaidDate"] = datetime.now().strftime("%Y-%m-%d")
            write_data_file(BILL_FILE, bills)
            
            # 更新账户余额
            account = get_account_by_id(account_id)
            new_balance = float(account["Balance"]) - float(bill["Amount"])
            update_account_balance(account_id, new_balance)
            
            # 记录交易
            record_transaction(
                account_id,
                "bill_payment",
                -float(bill["Amount"]),
                BillType=bill["BillType"]
            )
            print("Bill payment successful")
            return
    print("Payment failed")

def get_account_by_id(account_id):
    """根据ID获取账户"""
    accounts = read_data_file(ACCOUNT_FILE)
    for acc in accounts:
        if acc["AccountID"] == account_id:
            return acc
    return None

if __name__ == "__main__":
    main()