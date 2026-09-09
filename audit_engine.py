import pandas as pd


def audit_hr_data(df):
    """
    HR OpsGuard audit engine.
    Checks employee lifecycle data for common HR operations exceptions.
    """

    exceptions = []

    # ---------------------------------------------------------
    # 1. DUPLICATE EMPLOYEE IDs
    # ---------------------------------------------------------
    duplicate_ids = df[df["Emp ID"].duplicated(keep=False)]

    for _, row in duplicate_ids.iterrows():
        exceptions.append({
            "Emp ID": row["Emp ID"],
            "Category": "Employee Data",
            "Risk": "High",
            "Exception": "Duplicate employee ID detected",
            "Evidence": f"Employee ID {row['Emp ID']} appears more than once",
            "Recommended Action": "Validate employee records and remove/resolve the duplicate."
        })

    # ---------------------------------------------------------
    # 2. MISSING DOCUMENTS
    # ---------------------------------------------------------
    for _, row in df[df["Documents"].astype(str).str.lower() == "missing"].iterrows():
        exceptions.append({
            "Emp ID": row["Emp ID"],
            "Category": "Onboarding",
            "Risk": "High",
            "Exception": "Required documentation missing",
            "Evidence": "Documents = Missing",
            "Recommended Action": "Verify required documentation and update the employee record."
        })

    # ---------------------------------------------------------
    # 3. INCOMPLETE ONBOARDING
    # ---------------------------------------------------------
    for _, row in df[df["Onboarding"].astype(str).str.lower() == "incomplete"].iterrows():
        exceptions.append({
            "Emp ID": row["Emp ID"],
            "Category": "Onboarding",
            "Risk": "Medium",
            "Exception": "Onboarding process incomplete",
            "Evidence": "Onboarding = Incomplete",
            "Recommended Action": "Review outstanding onboarding activities and complete the process."
        })

    # ---------------------------------------------------------
    # 4. ACTIVE EMPLOYEE + INACTIVE PAYROLL
    # ---------------------------------------------------------
    condition = (
        (df["Employee Status"].astype(str).str.lower() == "active") &
        (df["Payroll"].astype(str).str.lower() == "inactive")
    )

    for _, row in df[condition].iterrows():
        exceptions.append({
            "Emp ID": row["Emp ID"],
            "Category": "Payroll",
            "Risk": "High",
            "Exception": "Active employee has inactive payroll status",
            "Evidence": "Employee Status = Active; Payroll = Inactive",
            "Recommended Action": "Validate employee and payroll status and coordinate correction with Payroll."
        })

    # ---------------------------------------------------------
    # 5. EXITED EMPLOYEE + ACTIVE PAYROLL
    # ---------------------------------------------------------
    condition = (
        (df["Employee Status"].astype(str).str.lower() == "exited") &
        (df["Payroll"].astype(str).str.lower() == "active")
    )

    for _, row in df[condition].iterrows():
        exceptions.append({
            "Emp ID": row["Emp ID"],
            "Category": "Payroll",
            "Risk": "High",
            "Exception": "Exited employee has active payroll status",
            "Evidence": "Employee Status = Exited; Payroll = Active",
            "Recommended Action": "Validate separation status and coordinate with Payroll to reconcile the record."
        })

    # ---------------------------------------------------------
    # 6. EXITED EMPLOYEE + MISSING EXIT DATE
    # ---------------------------------------------------------
    condition = (
        (df["Employee Status"].astype(str).str.lower() == "exited") &
        (df["Exit Date"].fillna("").astype(str).str.strip() == "")
    )

    for _, row in df[condition].iterrows():
        exceptions.append({
            "Emp ID": row["Emp ID"],
            "Category": "Employee Lifecycle",
            "Risk": "High",
            "Exception": "Exited employee has no exit date",
            "Evidence": "Employee Status = Exited; Exit Date is blank",
            "Recommended Action": "Validate the employee separation record and update the exit date."
        })

    # ---------------------------------------------------------
    # 7. EXIT DATE BEFORE JOIN DATE
    # ---------------------------------------------------------
    join_dates = pd.to_datetime(df["Join Date"], errors="coerce")
    exit_dates = pd.to_datetime(df["Exit Date"], errors="coerce")

    condition = exit_dates.notna() & join_dates.notna() & (exit_dates < join_dates)

    for _, row in df[condition].iterrows():
        exceptions.append({
            "Emp ID": row["Emp ID"],
            "Category": "Employee Lifecycle",
            "Risk": "Critical",
            "Exception": "Exit date occurs before join date",
            "Evidence": f"Join Date = {row['Join Date']}; Exit Date = {row['Exit Date']}",
            "Recommended Action": "Immediately validate the employee lifecycle dates and correct the source record."
        })

    # ---------------------------------------------------------
    # 8. MISSING APPROVAL
    # ---------------------------------------------------------
    condition = df["Approval"].astype(str).str.lower() == "no"

    for _, row in df[condition].iterrows():
        exceptions.append({
            "Emp ID": row["Emp ID"],
            "Category": "Process Controls",
            "Risk": "Medium",
            "Exception": "Required approval missing",
            "Evidence": "Approval = No",
            "Recommended Action": "Validate the required approval and update the transaction record."
        })

    # ---------------------------------------------------------
    # 9. INCOMPLETE OFFBOARDING
    # ---------------------------------------------------------
    condition = (
        (df["Employee Status"].astype(str).str.lower() == "exited") &
        (df["Offboarding"].astype(str).str.lower() == "incomplete")
    )

    for _, row in df[condition].iterrows():
        exceptions.append({
            "Emp ID": row["Emp ID"],
            "Category": "Offboarding",
            "Risk": "High",
            "Exception": "Offboarding process incomplete",
            "Evidence": "Employee Status = Exited; Offboarding = Incomplete",
            "Recommended Action": "Review outstanding offboarding activities and complete the required process."
        })

    # ---------------------------------------------------------
    # RETURN RESULTS
    # ---------------------------------------------------------
    return pd.DataFrame(exceptions)