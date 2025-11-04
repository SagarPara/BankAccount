### basic bank account - project
### bank_account.py


import os
from dotenv import load_dotenv
import streamlit as st
# from langchain_openai import ChatOpenAI

load_dotenv(override=True)

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# initialize the LLM
# llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# -------------------------
# Define BankAccount class
# -------------------------
class BankAccount:
    def __init__(self, account_holder:str, initial_balance:float=0.0):
        self.account_holder = account_holder
        self.balance = initial_balance
        self.transaction_history = []


    def deposit(self, amount:float):
        if amount > 0:
            self.balance += amount
            self.transaction_history.append(f"Deposited: Rs. {amount}")
        else:
            raise ValueError("Deposit amount must be positive.")

        
    def withdraw(self, amount:float):
        if amount <= self.balance:
            self.balance -= amount
            self.transaction_history.append(f"Wthdrawn: Rs. {amount}")
        else:
            raise ValueError("Insufficient funds for withdrawal.")

    def get_balance(self) -> float:
        return self.balance


    def get_transaction_history(self) -> list:
        return self.transaction_history


st.title("Basic Bank Account Management System")
account_holder = st.text_input("Enter Account Holder Name:")
initial_deposit = st.number_input("Enter Initital Deposit Amount(Rs. ):", min_value=0.0, value=0.0, step=100.0)

if st.button("Create Account"):
    account = BankAccount(account_holder, initial_deposit)
    st.success(f"Account created for {account_holder} with initial deposit of Rs. {initial_deposit}")
    st.session_state['account'] = account

if 'account' in st.session_state:
    account = st.session_state['account']
    
    st.subheader("Deposit Money")
    deposit_amount = st.number_input("Enter Deposit Amount(Rs. ):", min_value=0.0, value=0.0, step=100.0, key="deposit")
    if st.button("Deposit"):
        try:
            account.deposit(deposit_amount)
            st.success(f"Deposited Rs. {deposit_amount} successfully!")
        except ValueError as e:
            st.error(str(e))
    
    
    st.subheader("Withdraw Money")
    withdraw_amount = st.number_input("Enter Withdraw Amount(Rs. ):", min_value=0.0, value=0.0, step=100.0, key="withdraw")
    if st.button("Withdraw"):
        try:
            account.withdraw(withdraw_amount)
            st.success(f"Withdrew Rs. {withdraw_amount} successfully!")
        except ValueError as e:
            st.error(str(e))
    
    if st.button("Check Balance"):
        balance = account.get_balance()
        st.info(f"Current Balance: Rs. {balance}")
    
    if st.button("Transaction History"):
        history = account.get_transaction_history()
        if history:
            st.subheader("Transaction History:")
            for transaction in history:
                st.write(transaction)
        else:
            st.info("No transactions yet.")

