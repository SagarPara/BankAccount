from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from typing import Annotated
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
# from langgraph.prebuilt import tools_conditions
from langgraph.checkpoint.memory import MemorySaver
import streamlit as st


import os
from dotenv import load_dotenv
load_dotenv(override=True)

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-4.o-mini", temperature=0)


# Create Class State
class State(BaseModel):
    account_holder: str = Field(descrition = "Name of the account holder")
    balance: float = Field(description="Current balance in the account")
    transaction_history: list[str] = Field(description = "List of transaction history")

# Deposit Amount
def deposit(state: State, amount: float) -> State:
    if amount > 0:
        state.balance += amount
        state.transaction_history.append(f"Deposited Amount in Rs. {amount}")
        return state

# Withdrawn Amount
def withdraw(state: State, amount: float) -> State:
    if amount <= state.balance:
        state.balance -= amount
        state.transaction_history.append(f"Withdrawn Amount in Rs. {amount}")
        return state

# Balance Amount
def get_balance(state: State) -> float:
    return state.balance

# Transaction History
def get_transaction_history(state: State) -> list[str]:
    return state.transaction_history



def tools_condition(state: State) -> str:
    """ Decide which tool node to go to next based on transaction type"""
    last_action = state.transaction_history[-1] if state.transaction_history else ""
    if "Deposit" in last_action:
        return "Deposit"
    elif "Withdraw" in last_action:
        return "Withdraw"
    else:
        return "Balance"



# add State graph
graph_builder = StateGraph(State)

# add Nodes
graph_builder.add_node("Deposit", deposit)
graph_builder.add_node("Withdraw", withdraw)
graph_builder.add_node("Balance", get_balance)
graph_builder.add_node("History", get_transaction_history)

# add edges
graph_builder.add_edge(START, "Balance")
graph_builder.add_conditional_edges("Balance", tools_condition, {"Deposit": "Deposit", "Withdraw": "Withdraw", "Balance": "Balance"})

graph_builder.add_edge("Deposit", "Balance")
graph_builder.add_edge("Withdraw", "Balance")
graph_builder.add_edge("Balance", "History")
graph_builder.add_edge("History", END)

memory_saver = MemorySaver()
graph = graph_builder.compile(checkpointer=[memory_saver])




### Streamlit App
def app():
    st.title("🏦 Bank Account Management (LangGraph + Streamlit)")
    st.write("Manage your bank account using a smart AI-powered system!")

    if "account_state" not in st.session_state:
        st.session_state.account_state = None

    # Step 1: Create Account
    account_holder = st.text_input("Enter Account Holder Name:")
    initial_deposit = st.number_input("Enter Initial Deposit Amount (Rs):", min_value=0.0, value=0.0, step=100.0)

    if st.button("Create Account"):
        st.session_state.account_state = State(
            account_holder=account_holder,
            balance=initial_deposit,
            transaction_history=[f"Account created with Rs. {initial_deposit}"]
        )
        st.success(f"Account created successfully for {account_holder}!")

    # Step 2: Perform Transactions
    if st.session_state.account_state:
        state = st.session_state.account_state

        st.subheader("💰 Deposit Money")
        deposit_amount = st.number_input("Enter Deposit Amount (Rs):", min_value=0.0, value=0.0, step=100.0, key="deposit")
        if st.button("Deposit"):
            state = deposit(state, deposit_amount)
            st.session_state.account_state = state
            st.success(f"Deposited Rs. {deposit_amount} successfully!")

        st.subheader("🏧 Withdraw Money")
        withdraw_amount = st.number_input("Enter Withdraw Amount (Rs):", min_value=0.0, value=0.0, step=100.0, key="withdraw")
        if st.button("Withdraw"):
            if withdraw_amount <= state.balance:
                state = withdraw(state, withdraw_amount)
                st.session_state.account_state = state
                st.success(f"Withdrew Rs. {withdraw_amount} successfully!")
            else:
                st.error("Insufficient funds!")

        st.subheader("📊 Account Balance")
        if st.button("Check Balance"):
            balance = get_balance(state)
            st.info(f"Current Balance: Rs. {balance}")

        st.subheader("🧾 Transaction History")
        if st.button("Show History"):
            history = get_transaction_history(state)
            for t in history:
                st.write("-", t)

# -----------------------------
# Run Streamlit App
# -----------------------------
if __name__ == "__main__":
    app()
