# File: app_streamlit/pages/dashboard/purchase_form.py
"""
Token purchase form component.

This module provides the credit card form for purchasing tokens.
"""

import streamlit as st
import time
from components.api_client import APIClient

api_client = APIClient()


def show_purchase_form(username: str):
    """
    Display the token purchase form with credit card input.

    Args:
        username: Current user's username for the purchase.
    """
    st.subheader("Purchase Tokens")

    with st.form("purchase_tokens_form"):
        st.write("**Select Token Package:**")
        col_pkg1, col_pkg2 = st.columns(2)

        with col_pkg1:
            tokens_to_add = st.number_input("Number of tokens", min_value=1, max_value=1000, value=10,
                                            help="Select how many tokens you want to purchase")
        with col_pkg2:
            price = tokens_to_add * 0.10
            st.metric("Total Price", f"${price:.2f}")

        st.divider()
        st.write("**Payment Information** (Demo - No real charges)")

        col_card1, col_card2 = st.columns(2)
        with col_card1:
            card_number = st.text_input("Card Number", placeholder="1234 5678 9012 3456", max_chars=19)
            card_name = st.text_input("Cardholder Name", placeholder="JOHN DOE")

        with col_card2:
            col_exp1, col_exp2 = st.columns(2)
            with col_exp1:
                exp_month = st.selectbox("Exp. Month",
                                         ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"])
            with col_exp2:
                exp_year = st.selectbox("Exp. Year", ["2025", "2026", "2027", "2028", "2029", "2030"])
            cvv = st.text_input("CVV", placeholder="123", max_chars=4, type="password")

        st.divider()
        agree_terms = st.checkbox("I agree to the terms and conditions",
                                  help="This is a demo - no real payment")

        if st.form_submit_button("Complete Purchase", type="primary", use_container_width=True):
            _process_purchase(username, tokens_to_add, price, card_number, card_name, cvv, agree_terms)


def _process_purchase(username, tokens, price, card_number, card_name, cvv, agree_terms):
    """Validate and process the token purchase."""
    errors = []
    if not card_number or len(card_number.replace(" ", "")) < 13:
        errors.append("Invalid card number (minimum 13 digits)")
    if not card_name or len(card_name.strip()) < 3:
        errors.append("Cardholder name is required")
    if not cvv or len(cvv) < 3:
        errors.append("CVV must be 3-4 digits")
    if not agree_terms:
        errors.append("You must agree to the terms and conditions")

    if errors:
        for error in errors:
            st.error(error)
        return

    with st.spinner("Processing payment..."):
        time.sleep(1.5)
        result = api_client.add_tokens(username, tokens)

        if "error" in result:
            st.error(f"Transaction failed: {result['error']}")
            return

        st.session_state["tokens"] = result["new_balance"]
        st.success("Payment Successful!")

        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Transaction Details:**\n- Tokens: {tokens}\n- Amount: ${price:.2f}\n"
                    f"- Card: **** {card_number[-4:] if len(card_number) >= 4 else '****'}")
        with col2:
            prev_balance = result['new_balance'] - tokens
            st.info(f"**Balance:**\n- Previous: {prev_balance}\n- Added: +{tokens}\n"
                    f"- Current: **{result['new_balance']}**")

        st.balloons()
        time.sleep(2)
        st.rerun()
