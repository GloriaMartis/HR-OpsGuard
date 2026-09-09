import streamlit as st
import pandas as pd
from audit_engine import audit_hr_data
from gemini_agent import generate_hr_insights

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="HR OpsGuard",
    page_icon="🛡️",
    layout="wide"
)

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.title("🛡️ HR OpsGuard")
st.subheader("AI-Powered HR Operations Audit")

st.markdown(
    "Audit employee lifecycle data, identify operational exceptions, "
    "prioritize risks, and generate recommended actions."
)

st.divider()

# ---------------------------------------------------------
# FILE UPLOAD
# ---------------------------------------------------------
st.header("📂 Upload HR Operations Data")

uploaded_file = st.file_uploader(
    "Upload an Excel file",
    type=["xlsx"]
)

# ---------------------------------------------------------
# AUDIT
# ---------------------------------------------------------
if uploaded_file is not None:

    try:
        df = pd.read_excel(uploaded_file)

        st.success(
            f"Successfully loaded {len(df)} HR records."
        )

        with st.expander("Preview HR Data"):
            st.dataframe(
                df,
                width="stretch"
            )

        if st.button("🔍 Run HR Audit", type="primary"):

            results = audit_hr_data(df)

            st.session_state["audit_results"] = results
            st.session_state["hr_data"] = df

    except Exception as e:
        st.error(f"Unable to read the file: {e}")


# ---------------------------------------------------------
# DISPLAY AUDIT RESULTS
# ---------------------------------------------------------
if "audit_results" in st.session_state:

    results = st.session_state["audit_results"]
    df = st.session_state["hr_data"]

    st.divider()

    st.header("📊 Audit Summary")

    total_records = len(df)
    total_exceptions = len(results)

    critical = len(
        results[results["Risk"] == "Critical"]
    )

    high = len(
        results[results["Risk"] == "High"]
    )

    medium = len(
        results[results["Risk"] == "Medium"]
    )

    exception_rate = (
        total_exceptions / total_records * 100
        if total_records > 0 else 0
    )

    # -----------------------------------------------------
    # SUMMARY METRICS
    # -----------------------------------------------------
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Records Audited",
        total_records
    )

    col2.metric(
        "Exceptions",
        total_exceptions
    )

    col3.metric(
        "🔴 Critical",
        critical
    )

    col4.metric(
        "🟠 High",
        high
    )

    col5.metric(
        "Exception Rate",
        f"{exception_rate:.1f}%"
    )

    # -----------------------------------------------------
    # TOP FINDINGS
    # -----------------------------------------------------
    st.subheader("🔎 Top Findings")

    if total_exceptions > 0:

        category_counts = (
            results["Category"]
            .value_counts()
            .reset_index()
        )

        category_counts.columns = [
            "Category",
            "Exceptions"
        ]

        # Used later by Ask HR OpsGuard
        top_category = category_counts.iloc[0]["Category"]
        top_count = category_counts.iloc[0]["Exceptions"]

        st.dataframe(
            category_counts,
            width="stretch",
            hide_index=True
        )

    else:

        top_category = "None"
        top_count = 0

    # -----------------------------------------------------
    # EXCEPTION DETAILS
    # -----------------------------------------------------
    st.subheader("🚨 Exception Details")

    if total_exceptions > 0:

        st.dataframe(
            results,
            width="stretch",
            hide_index=True
        )

    else:

        st.success(
            "No exceptions detected. "
            "HR data passed all configured audit checks."
        )

    # -----------------------------------------------------
    # HR OPSGUARD AI INSIGHTS
    # -----------------------------------------------------
    st.divider()

    st.header("🤖 HR OpsGuard AI Insights")

    if total_exceptions > 0:

        if st.button(
            "✨ Generate AI Insights",
            type="primary"
        ):

            with st.spinner(
                "Gemini is analyzing the HR audit results..."
            ):

                ai_insights = generate_hr_insights(
                    results
                )

            st.markdown(ai_insights)

        st.info(
            "AI-generated insights are based on the audit results. "
            "HR professionals should validate exceptions before "
            "taking action."
        )

    else:

        st.success(
            "No exceptions available for AI analysis."
        )

    # -----------------------------------------------------
    # ASK HR OPSGUARD
    # -----------------------------------------------------
    st.divider()

    st.header("💬 Ask HR OpsGuard")

    question = st.text_input(
        "Ask a question about the audit results",
        placeholder="Example: What is the biggest risk?"
    )

    if question:

        q = question.lower()

        if (
            "biggest" in q
            or "highest" in q
            or "risk" in q
        ):

            if critical > 0:

                st.write(
                    f"The audit identified **{critical} Critical** "
                    "exception(s). These should receive the highest "
                    "priority for HR review."
                )

            elif high > 0:

                st.write(
                    f"The audit identified **{high} High-risk** "
                    "exception(s). These should be prioritized "
                    "for timely HR review."
                )

            else:

                st.write(
                    "No Critical or High-risk exceptions "
                    "were identified."
                )

        elif (
            "category" in q
            or "process" in q
        ):

            if total_exceptions > 0:

                st.write(
                    f"The category with the most exceptions is "
                    f"**{top_category}** with "
                    f"**{top_count} exception(s)**."
                )

            else:

                st.write(
                    "No exception categories were identified."
                )

        elif (
            "recommend" in q
            or "improve" in q
        ):

            if total_exceptions > 0:

                st.write(
                    f"Consider reviewing the recurring "
                    f"**{top_category}** exceptions and "
                    "strengthening the related validation "
                    "or process-control step."
                )

            else:

                st.write(
                    "No process improvements are required "
                    "based on the current audit results."
                )

        else:

            st.write(
                "Try asking: **What is the biggest risk?**, "
                "**Which process has the most exceptions?**, "
                "or **What should HR improve?**"
            )