import streamlit as st
import pandas as pd

from services.receipt_ai_service import extract_receipt_details
from services.claim_service import (
    save_claim,
    get_user_claims
)


def render_receipt_claim():

    st.subheader("🧾 Receipt Claim Assistant")

    st.info(
        "Upload a receipt or bill image. AI will extract claim details and prepare a reimbursement form."
    )

    receipt_file = st.file_uploader(
        "Upload receipt image",
        type=["png", "jpg", "jpeg"],
        key="receipt_upload"
    )

    if receipt_file:
        st.image(
            receipt_file,
            caption="Uploaded Receipt",
            use_container_width=True
        )

        if st.button("Extract Claim Details"):
            with st.spinner("Reading receipt and extracting claim details..."):
                extracted = extract_receipt_details(receipt_file)

            st.session_state.extracted_claim = extracted

    if "extracted_claim" in st.session_state:

        claim = st.session_state.extracted_claim

        st.markdown("### Review Claim Form")

        vendor_name = st.text_input("Vendor Name", claim.get("vendor_name", ""))
        receipt_date = st.text_input("Receipt Date", claim.get("receipt_date", ""))
        amount = st.text_input("Amount", str(claim.get("amount", "")))
        currency = st.text_input("Currency", claim.get("currency", ""))
        tax_amount = st.text_input("Tax Amount", str(claim.get("tax_amount", "")))

        category_options = [
            "Visa",
            "Travel",
            "Food",
            "Hotel",
            "Transport",
            "Office",
            "Medical",
            "Other"
        ]

        extracted_category = claim.get("category", "Other")

        if extracted_category not in category_options:
            extracted_category = "Other"

        category = st.selectbox(
            "Category",
            category_options,
            index=category_options.index(extracted_category)
        )

        payment_method = st.text_input(
            "Payment Method",
            claim.get("payment_method", "")
        )

        invoice_number = st.text_input(
            "Invoice / Receipt Number",
            claim.get("invoice_number", "")
        )

        description = st.text_area(
            "Description",
            claim.get("description", "")
        )

        confidence_score = st.text_input(
            "AI Confidence Score",
            str(claim.get("confidence_score", ""))
        )

        final_claim = {
            "vendor_name": vendor_name,
            "receipt_date": receipt_date,
            "amount": amount,
            "currency": currency,
            "tax_amount": tax_amount,
            "category": category,
            "payment_method": payment_method,
            "invoice_number": invoice_number,
            "description": description,
            "confidence_score": confidence_score,
            "status": "Submitted"
        }

        if st.button("Submit Claim"):
            save_claim(
                st.session_state.user["id"],
                st.session_state.user["email"],
                final_claim
            )

            st.success("Claim submitted successfully.")
            del st.session_state.extracted_claim
            st.rerun()

    st.markdown("---")
    st.markdown("### My Claims")

    claims = get_user_claims(st.session_state.user["id"])

    if claims:
        claims_df = pd.DataFrame(
            claims,
            columns=[
                "Claim ID",
                "Vendor",
                "Date",
                "Amount",
                "Currency",
                "Category",
                "Status",
                "Created At"
            ]
        )

        st.dataframe(claims_df)
    else:
        st.info("No claims submitted yet.")