# -*- coding: utf-8 -*-
"""
Created on Thu May 25 07:36:42 2023

@author: ArnoldKigonya
"""

from datetime import datetime
from random import choice

import gspread
import streamlit as st
from pytz import timezone

from Functions import functions as fx

st.set_page_config(page_title="Fraternity Trust Fund", page_icon="💰")

# is_alvin = False

is_logged_in = st.session_state.get("is_logged_in", False)

if not is_logged_in:
    with st.form(key="alvin_login"):
        user = st.text_input("Authorised User", value="Alvin Mulumba", disabled=True)
        entered_password = st.text_input("Enter your password", type="password")

        login = st.form_submit_button("Enter")

    if login:
        is_alvin = fx.is_alvin(entered_password)
        if is_alvin:
            st.session_state["is_logged_in"] = True
        else:
            st.error("❌ Please enter Alvin's password to access this page")
else:
    years = fx.get_years_since_2022()
    months = fx.get_all_months()

    sheet_credentials = st.secrets["sheet_credentials"]
    gc = gspread.service_account_from_dict(sheet_credentials)

    forms_sidebar_selection = st.sidebar.selectbox(
        "What would you like to enter?", ("Payments", "Costs", "UAP")
    )

    if forms_sidebar_selection == "Payments":
        names = fx.get_all_names()

        st.title(":blue[Payments]")

        with st.form(key="payments", clear_on_submit=True):
            st.markdown(
                "**Hi Alvin, please choose the month and year for which you are entering data**"
            )

            month, year = st.columns(2)

            with month:
                selected_month = st.selectbox("Month", months)

            with year:
                selected_year = st.selectbox("Year", years)

            st.write("---")

            st.markdown("**Member Payments**")

            name_column, amount = st.columns(2)

            name_column.markdown("_Name_")
            amount.markdown("_Amount_")

            name_input = dict()

            emoji_options = ["😃", "😄", "🐪", "😊", "🙂", "😎", "💰", "😁"]

            counter = 1

            for name in names:
                amount_key = f"key{counter}"

                name_input[name] = amount_key

                emoji = choice(emoji_options)

                with name_column:
                    st.write(emoji, " ", name)
                    st.write("")
                with amount:
                    st.text_input(
                        placeholder="ugx",
                        label=" ",
                        label_visibility="collapsed",
                        disabled=False,
                        key=amount_key,
                    )

                counter += 1

            submitted = st.form_submit_button("Save")

            if submitted:
                with st.spinner("Validating Payments Form..."):
                    payments_form_isvalid = True
                    validation_list = list()

                    payments_for_insertion = []
                    timezone = timezone("Africa/Nairobi")

                    for name, amount_key in name_input.items():
                        amount_entered = st.session_state.get(amount_key, "")

                        if amount_entered.strip():
                            amount_paid = int(amount_entered.strip())
                        else:
                            continue

                        timestamp = datetime.now(timezone).strftime(
                            "%d-%b-%Y %H:%M:%S" + " EAT"
                        )

                        date_string = f"1 {selected_month} {selected_year}"
                        data_date = datetime.strptime(date_string, "%d %B %Y").date()

                        data = [
                            timestamp,
                            selected_month,
                            name,
                            amount_paid,
                            selected_year,
                            data_date,
                        ]

                        payments_for_insertion.append(data)
                        validation_list.append(amount_paid)

                payments_form_isvalid = all(item > 0 for item in validation_list)
                if not payments_form_isvalid:
                    st.error("🚨 All payments entered must be greater than zero")

                if payments_form_isvalid:
                    with st.spinner("Saving payments data..."):
                        fraternity_sheet = gc.open_by_key(st.secrets["sheet_key"])
                        worksheet = fraternity_sheet.worksheet("Payments")

                        all_values = worksheet.get_all_values()

                        next_row_index = len(all_values) + 1

                        worksheet.append_rows(
                            payments_for_insertion,
                            value_input_option="user_entered",
                            insert_data_option="insert_rows",
                            table_range=f"a{next_row_index}",
                        )

                        st.success(
                            "✅ Payments Saved Successfully. Feel free to close the application"
                        )

    if forms_sidebar_selection == "Costs":
        st.title(":red[Costs]")

        with st.form(key="costs", clear_on_submit=True):
            st.markdown(
                "**Hi Alvin, please choose the month and year for which you are entering data**"
            )

            month, year = st.columns(2)

            with month:
                selected_month = st.selectbox("Month", months)

            with year:
                selected_year = st.selectbox("Year", years)

            st.write("---")

            st.markdown("**Monthly Fund Costs**")

            item, amount, narrative = st.columns(3)

            item.markdown("_Cost Item_")
            amount.markdown("_Amount_")
            narrative.markdown("_Narrative_")

            identifier = dict()

            counter = 1

            for i in range(0, 3):
                item_key = f"key{counter}"
                amount_key = f"key{counter + 1}"
                narrative_key = f"key{counter + 2}"

                identifier[i] = [item_key, amount_key, narrative_key]

                with item:
                    st.text_input(
                        label=" ",
                        label_visibility="collapsed",
                        disabled=False,
                        key=item_key,
                    )
                with amount:
                    st.text_input(
                        placeholder="ugx",
                        label=" ",
                        label_visibility="collapsed",
                        disabled=False,
                        key=amount_key,
                    )
                with narrative:
                    st.text_input(
                        label=" ",
                        label_visibility="collapsed",
                        disabled=False,
                        key=narrative_key,
                    )

                counter += 3

            submitted = st.form_submit_button("Save")

            if submitted:
                costs_for_insertion = []
                timezone = timezone("Africa/Nairobi")

                with st.spinner("Validating form..."):
                    cost_form_entry_isValid = True

                    for identifier, input_list in identifier.items():
                        cost_item = st.session_state.get(input_list[0], "")
                        cost_amount = st.session_state.get(input_list[1], "")
                        cost_narrative = st.session_state.get(input_list[2], "")

                        if (
                            not cost_item.strip()
                            and not cost_amount.strip()
                            and not cost_narrative.strip()
                        ):
                            continue

                        if cost_item.strip():
                            if cost_amount.strip():
                                cost_amount_value = int(cost_amount.strip())
                                if cost_amount_value <= 0:
                                    cost_form_entry_isValid = False
                                    st.error(
                                        "🚨 Please enter a cost amount greater than zero"
                                    )
                            else:
                                cost_form_entry_isValid = False
                                st.error("⚠️ Cost amount cannot be blank")

                        if cost_amount.strip() and not cost_item.strip():
                            cost_form_entry_isValid = False
                            st.error("⚠️ Cost item cannot be blank")

                        if cost_form_entry_isValid:
                            timestamp = datetime.now(timezone).strftime(
                                "%d-%b-%Y %H:%M:%S" + " EAT"
                            )

                            date_string = f"1 {selected_month} {selected_year}"
                            data_date = datetime.strptime(
                                date_string, "%d %B %Y"
                            ).date()

                            data = [
                                timestamp,
                                selected_month,
                                cost_item.strip(),
                                cost_amount_value,
                                cost_narrative.strip(),
                                selected_year,
                                data_date,
                            ]

                            costs_for_insertion.append(data)

                if costs_for_insertion:
                    with st.spinner("Saving Cost data..."):
                        fraternity_sheet = gc.open_by_key(st.secrets["sheet_key"])
                        worksheet = fraternity_sheet.worksheet("Costs")

                        all_values = worksheet.get_all_values()

                        next_row_index = len(all_values) + 1

                        worksheet.append_rows(
                            costs_for_insertion,
                            value_input_option="user_entered",
                            insert_data_option="insert_rows",
                            table_range=f"a{next_row_index}",
                        )

                        st.success(
                            "✅ Cost data Saved Successfully. Feel free to close the application"
                        )

    if forms_sidebar_selection == "UAP":
        st.title(":green[UAP]")

        with st.form(key="UAP", clear_on_submit=True):
            st.markdown(
                "**Hi Alvin, please choose the month and year for which you are entering data**"
            )

            month, year = st.columns(2)

            with month:
                selected_month = st.selectbox("Month", months)

            with year:
                selected_year = st.selectbox("Year", years)

            st.write("---")

            st.markdown("**UAP Portfolio Monthly Details**")

            st.caption("_As shown in the Investment Statement_")

            counter = 0

            opening_key = f"key{counter}"
            closing_key = f"key{counter + 1}"
            interest_key = f"key{counter + 2}"

            holder_column, dummy_column = st.columns(2)

            with holder_column:
                st.text_input(
                    label="Opening Balance",
                    placeholder="ugx",
                    disabled=False,
                    help="Please enter a value greater than zero",
                    key=opening_key,
                )

                st.text_input(
                    placeholder="ugx",
                    label="Closing Balance",
                    disabled=False,
                    help="Please enter a value greater than zero",
                    key=closing_key,
                )

                st.text_input(
                    label="Interest Rate",
                    placeholder="%",
                    help="Please enter a value greater than zero",
                    disabled=False,
                    key=interest_key,
                )

            submitted = st.form_submit_button("Save")

            if submitted:
                is_valid = True

                with st.spinner("🔍 Validating form..."):
                    uap_opening = st.session_state.get(opening_key, "")
                    uap_closing = st.session_state.get(closing_key, "")
                    uap_interest = st.session_state.get(interest_key, "")

                    uap_interest_value = 0
                    uap_opening_value = 0
                    uap_closing_value = 0

                    if uap_opening.strip():
                        uap_opening_value = float(uap_opening.strip())
                        if uap_opening_value <= 0.0:
                            is_valid = False
                            st.error(
                                "🚨 Please enter an opening balance greater than zero"
                            )
                    else:
                        is_valid = False
                        st.error("⚠️ Opening Balance cannot be blank")

                    if uap_closing.strip():
                        uap_closing_value = float(uap_closing.strip())
                        if uap_closing_value <= 0.0:
                            is_valid = False
                            st.error(
                                "🚨 Please enter a closing balance greater than zero"
                            )
                    else:
                        is_valid = False
                        st.error("⚠️ Closing Balance cannot be blank")

                    if uap_interest.strip():
                        if uap_interest.endswith("%"):
                            uap_interest_value = float(uap_interest.strip("%")) / 100.0
                        else:
                            uap_interest_value = float(uap_interest.strip()) / 100.0
                        if uap_interest_value <= 0.0:
                            is_valid = False
                            st.error(
                                "🚨 Please enter an interest rate greater than zero"
                            )
                    else:
                        is_valid = False
                        st.error("⚠️ Interest rate cannot be blank")

                if is_valid:
                    st.info("👍 Form is Valid")

                    with st.spinner("Saving UAP data..."):
                        timezone = timezone("Africa/Nairobi")

                        timestamp = datetime.now(timezone).strftime(
                            "%d-%b-%Y %H:%M:%S" + " EAT"
                        )

                        date_string = f"1 {selected_month} {selected_year}"
                        data_date = datetime.strptime(date_string, "%d %B %Y").date()

                        data = [
                            timestamp,
                            selected_month,
                            selected_year,
                            uap_closing_value,
                            uap_opening_value,
                            uap_interest_value,
                            data_date,
                        ]

                        fraternity_sheet = gc.open_by_key(st.secrets["sheet_key"])
                        worksheet = fraternity_sheet.worksheet("UAP Portfolio")

                        all_values = worksheet.get_all_values()

                        next_row_index = len(all_values) + 1

                        worksheet.append_row(
                            data,
                            value_input_option="user_entered",
                            insert_data_option="insert_rows",
                            table_range=f"a{next_row_index}",
                        )

                        st.success(
                            "✅ UAP data Saved Successfully. Feel free to close the application"
                        )
