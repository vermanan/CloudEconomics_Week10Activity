import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# ----------------------------------------------------------
# APP CONFIG
# ----------------------------------------------------------
st.set_page_config(page_title="CloudMart – Task Sets 1 & 2", layout="wide")

st.title("☁️ CloudMart – Task Set 1 & 2 Dashboard")
st.markdown("""
This app completes **Task Set 1 – Data Exploration**  
and **Task Set 2 – Cost Visibility**  
for the Week 10 Cloud Resource Tagging case study.
""")

file_path = "cloudmart_multi_account.csv"

try:
    # ----------------------------------------------------------
    # LOAD DATASET (unchanged)
    #----------------------------------------------------------
    with open(file_path, "r", encoding="utf-8-sig") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    split_data = [line.split(",") for line in lines]
    df = pd.DataFrame(split_data[1:], columns=split_data[0])

    df.columns = df.columns.str.replace('"', '').str.strip()
    df = df.applymap(lambda x: x.strip().replace('"', '') if isinstance(x, str) else x)

    if "MonthlyCostUSD" in df.columns:
        df["MonthlyCostUSD"] = pd.to_numeric(df["MonthlyCostUSD"], errors="coerce")

    # ----------------------------------------------------------
    # GLOBAL SIDEBAR FILTERS (KEEP — FIXED)
    #----------------------------------------------------------
    st.sidebar.header("🎛️ Global Filters")

    def multiselect_or_all(label, col):
        if col not in df.columns:
            return []
        vals = sorted(df[col].dropna().unique())
        selected = st.sidebar.multiselect(label, vals, default=vals)
        return selected or vals

    dept_filter = multiselect_or_all("Department", "Department")
    proj_filter = multiselect_or_all("Project", "Project")
    env_filter = multiselect_or_all("Environment", "Environment")
    svc_filter = multiselect_or_all("Service", "Service")
    region_filter = multiselect_or_all("Region", "Region")

    # APPLY FILTERS (global)
    filtered_df = df[
        df["Department"].isin(dept_filter) &
        df["Project"].isin(proj_filter) &
        df["Environment"].isin(env_filter) &
        df["Service"].isin(svc_filter) &
        df["Region"].isin(region_filter)
    ].copy()

    st.sidebar.success(f"Filters applied: {len(filtered_df)} rows displayed")

    # ----------------------------------------------------------
    # CREATE TABS (Same as original)
    #----------------------------------------------------------
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📘 Task 1 – Data Exploration",
        "💰 Task 2 – Cost Visibility",
        "🏷️ Task 3 – Tagging Compliance",
        "📊 Task 4 – Visualization Dashboard",
        "🛠️ Task 5 – Tag Remediation Workflow"
    ])

    # ==========================================================
    # 📘 TAB 1 – DATA EXPLORATION (Unmodified)
    # ==========================================================
    with tab1:
        st.subheader("📋 1.1 Dataset Preview (First 5 Rows)")
        st.dataframe(filtered_df.head(), use_container_width=True)

        st.subheader("🔍 1.2 Missing Values Check")
        missing_summary = df.isnull().sum().reset_index()
        missing_summary.columns = ["Column Name", "Missing Values"]
        st.dataframe(missing_summary, use_container_width=True)

        st.subheader("📊 1.3 Columns with Most Missing Values")
        st.bar_chart(missing_summary.set_index("Column Name"))

        st.subheader("📦 1.4 Tagged vs Untagged Resources")
        if "Tagged" in df.columns:
            tagged = (df["Tagged"] == "Yes").sum()
            untagged = (df["Tagged"] == "No").sum()
            total = len(df)

            c1, c2, c3 = st.columns(3)
            c1.metric("Total Resources", total)
            c2.metric("Tagged", tagged)
            c3.metric("Untagged", untagged)

            st.subheader("📈 1.5 Percentage Untagged Resources")
            pct = (untagged / total * 100) if total else 0
            st.metric("Untagged (%)", f"{pct:.2f}%")

            st.subheader("📊 Visual Insights")
            col1, col2 = st.columns(2)

            # Chart 1
            with col1:
                if "Department" in filtered_df.columns:
                    dept_cost = filtered_df.groupby("Department")["MonthlyCostUSD"].sum().reset_index()
                    fig1, ax1 = plt.subplots(figsize=(3.5, 2.5))
                    ax1.bar(dept_cost["Department"], dept_cost["MonthlyCostUSD"])
                    ax1.set_title("💰 Cost by Department")
                    plt.tight_layout()
                    st.pyplot(fig1)

            # Chart 2
            with col2:
                fig2, ax2 = plt.subplots(figsize=(3.5, 2.5))
                ax2.pie([tagged, untagged], labels=["Tagged", "Untagged"], autopct="%1.1f%%")
                ax2.set_title("🏷️ Tag Distribution")
                st.pyplot(fig2)

    # ==========================================================
    # 💰 TAB 2 – COST VISIBILITY (FULL & FIXED)
    # ==========================================================
    with tab2:
        st.header("💰 Task 2 – Cost Visibility")
        st.markdown("""
        This section completes **Task Set 2** from the Week 10 case study.  
        It analyzes cloud cost visibility using tag completeness.
        """)

        cost_df = filtered_df.copy()

        # -----------------------------------------
        # 2.1 – Cost of Tagged vs Untagged
        # -----------------------------------------
        st.subheader("2.1 – Total Cost of Tagged vs Untagged Resources")

        if "Tagged" in cost_df.columns:
            cost_by_tag = (
                cost_df.groupby("Tagged")["MonthlyCostUSD"]
                .sum().reset_index()
            )
            st.dataframe(cost_by_tag, use_container_width=True)

            tagged_cost = cost_by_tag.loc[cost_by_tag["Tagged"] == "Yes", "MonthlyCostUSD"].sum()
            untagged_cost = cost_by_tag.loc[cost_by_tag["Tagged"] == "No", "MonthlyCostUSD"].sum()
            total_cost = tagged_cost + untagged_cost

            colA, colB = st.columns(2)

            # Small bar chart
            with colA:
                fig3, ax3 = plt.subplots(figsize=(3.5, 2.5))
                ax3.bar(cost_by_tag["Tagged"], cost_by_tag["MonthlyCostUSD"],
                        color=["#2E86AB", "#E27D60"])
                ax3.set_title("💰 Total Cost by Tag Status", fontsize=10)
                ax3.set_ylabel("Total Cost (USD)")
                plt.tight_layout()
                st.pyplot(fig3)

            # -----------------------------------------
            # 2.2 – % of total cost that is untagged
            # -----------------------------------------
            with colB:
                pct_untagged_cost = (untagged_cost / total_cost * 100) if total_cost else 0
                st.metric("2.2 – Untagged Cost (%)", f"{pct_untagged_cost:.2f}%")

            # -----------------------------------------
            # 2.3 – Department with most untagged cost
            # -----------------------------------------
            st.subheader("2.3 – Department with the Most Untagged Cost")
            if "Department" in cost_df.columns:
                untag_by_dept = (
                    cost_df[cost_df["Tagged"] == "No"]
                    .groupby("Department")["MonthlyCostUSD"]
                    .sum()
                    .sort_values(ascending=False)
                )
                st.dataframe(untag_by_dept.head(5), use_container_width=True)
            else:
                st.info("Department column not found.")

            # -----------------------------------------
            # 2.4 – Project consuming most overall cost
            # -----------------------------------------
            st.subheader("2.4 – Project Consuming the Most Total Cost")
            if "Project" in cost_df.columns:
                proj_cost = (
                    cost_df.groupby("Project")["MonthlyCostUSD"]
                    .sum()
                    .sort_values(ascending=False)
                )
                st.dataframe(proj_cost.head(5))
            else:
                st.info("Project column not found.")

            # -----------------------------------------
            # 2.5 – Prod vs Dev/Test – Cost & Tag Quality
            # -----------------------------------------
            st.subheader("2.5 – Prod vs Dev/Test — Cost & Tag Quality")
            if "Environment" in cost_df.columns:
                env_tag = (
                    cost_df.groupby(["Environment", "Tagged"])["MonthlyCostUSD"]
                    .sum()
                    .reset_index()
                )
                st.dataframe(env_tag, use_container_width=True)

                fig5, ax5 = plt.subplots(figsize=(4, 3))
                for tag_status in env_tag["Tagged"].unique():
                    subset = env_tag[env_tag["Tagged"] == tag_status]
                    ax5.bar(subset["Environment"], subset["MonthlyCostUSD"], label=tag_status)

                ax5.set_title("Environment Cost vs Tagging Status")
                ax5.set_ylabel("Monthly Cost (USD)")
                ax5.legend()
                plt.tight_layout()
                st.pyplot(fig5)
            else:
                st.info("Environment column not found.")
        else:
            st.warning("⚠️ 'Tagged' column missing – cannot compute Cost Visibility.")

    # ==========================================================
    # 🏷️ TAB 3 – TASK SET 3: TAGGING COMPLIANCE (3.1–3.5)
    # ==========================================================
    with tab3:
        st.header("🏷️ Task 3 – Tagging Compliance")
        st.markdown("""
        This section completes **Task Set 3** of the Week 10 case study.  
        It measures tagging completeness and identifies gaps.
        """)

        tag_fields = [
            "Department", "Project", "Environment", "Owner",
            "CostCenter", "CreatedBy", "Tagged"
        ]

        # Ensure all tag fields exist
        for col in tag_fields:
            if col not in df.columns:
                df[col] = None

        # 3.1 Tag completeness score per resource
        st.subheader("3.1 – Tag Completeness Score per Resource")
        df["TagCompletenessScore"] = df[tag_fields].apply(
            lambda row: sum(pd.notna(row) & (row != "")), axis=1
        )
        show_cols = ["ResourceID", "TagCompletenessScore"] if "ResourceID" in df.columns else ["TagCompletenessScore"]
        st.dataframe(df[show_cols].head(), use_container_width=True)

        # 3.2 Top 5 lowest completeness scores
        st.subheader("3.2 – Top 5 Resources with Lowest Completeness Scores")
        lowest5_cols = show_cols
        lowest5 = df.nsmallest(5, "TagCompletenessScore")[lowest5_cols]
        st.dataframe(lowest5, use_container_width=True)

        # 3.3 Most frequently missing tag fields
        st.subheader("3.3 – Most Frequently Missing Tag Fields")
        missing_counts = df[tag_fields].isna().sum().reset_index()
        missing_counts.columns = ["Tag Field", "Missing Count"]
        st.dataframe(missing_counts.sort_values("Missing Count", ascending=False),
                     use_container_width=True)

        fig6, ax6 = plt.subplots(figsize=(4, 2.8))
        ax6.bar(missing_counts["Tag Field"], missing_counts["Missing Count"], color="#FFB347")
        ax6.set_title("📊 Missing Tag Fields Count", fontsize=10)
        plt.xticks(rotation=45, ha="right", fontsize=8)
        plt.tight_layout()
        st.pyplot(fig6, use_container_width=True)

        # 3.4 list all untagged resources and their costs
        st.subheader("3.4 – List of Untagged Resources and Costs")
        if "Tagged" in df.columns:
            untagged_df = df[df["Tagged"].str.lower() == "no"][["ResourceID", "MonthlyCostUSD"]]
            st.dataframe(untagged_df, use_container_width=True)
        else:
            untagged_df = pd.DataFrame()
            st.warning("No 'Tagged' column found.")

        # 3.5 export untagged resources to CSV
        st.subheader("3.5 – Export Untagged Resources to CSV")
        if not untagged_df.empty:
            csv_data = untagged_df.to_csv(index=False)
            st.download_button(
                "⬇️ Download Untagged CSV",
                data=csv_data,
                file_name="untagged_resources.csv",
                mime="text/csv"
            )
        else:
            st.info("No untagged resources to export.")

    # ==========================================================
    # 📊 TAB 4 – TASK SET 4: VISUALIZATION DASHBOARD (FIXED)
    # ==========================================================
    with tab4:
        st.header("📊 Task 4 – Visualization Dashboard")

        # ------------------------------------------------------
        # 4.5 Interactive Dashboard Filters (WORKING VERSION)
        # ------------------------------------------------------
        st.subheader("4.5 – Interactive Dashboard Filters")

        colf1, colf2, colf3 = st.columns(3)

        with colf1:
            svc_pick = st.multiselect(
                "Service",
                sorted(filtered_df["Service"].dropna().unique()),
                default=None
            )
        with colf2:
            region_pick = st.multiselect(
                "Region",
                sorted(filtered_df["Region"].dropna().unique()),
                default=None
            )
        with colf3:
            dept_pick = st.multiselect(
                "Department",
                sorted(filtered_df["Department"].dropna().unique()),
                default=None
            )

        # Start with GLOBAL filtered DF
        viz_df = filtered_df.copy()

        # Apply 4.5 filters ONLY if user picked values
        if svc_pick:
            viz_df = viz_df[viz_df["Service"].isin(svc_pick)]
        if region_pick:
            viz_df = viz_df[viz_df["Region"].isin(region_pick)]
        if dept_pick:
            viz_df = viz_df[viz_df["Department"].isin(dept_pick)]

        st.info(f"Rows after dashboard filters: {len(viz_df)}")

        # ------------------------------------------------------
        # ALL CHARTS BELOW MUST USE viz_df
        # ------------------------------------------------------

        # 4.1 Pie chart – Tagged vs Untagged
        st.subheader("4.1 – Tagged vs Untagged Resources")
        if "Tagged" in viz_df.columns:
            pie_fig = px.pie(
                viz_df,
                names="Tagged",
                title="Tag Distribution",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(pie_fig, use_container_width=True)

        # 4.2 Cost per Department by Tagging
        st.subheader("4.2 – Cost per Department by Tagging Status")
        if "Department" in viz_df.columns:
            dept_cost = viz_df.groupby(["Department", "Tagged"])["MonthlyCostUSD"].sum().reset_index()
            bar_fig = px.bar(
                dept_cost,
                x="Department",
                y="MonthlyCostUSD",
                color="Tagged",
                barmode="group",
                title="Cost by Department and Tag Status"
            )
            st.plotly_chart(bar_fig, use_container_width=True)

        # 4.3 Total Cost per Service (Horizontal)
        st.subheader("4.3 – Total Cost per Service")
        if "Service" in viz_df.columns:
            svc_cost = viz_df.groupby("Service")["MonthlyCostUSD"].sum().reset_index()
            svc_fig = px.bar(
                svc_cost,
                y="Service",
                x="MonthlyCostUSD",
                orientation="h",
                title="Total Cost per Service"
            )
            st.plotly_chart(svc_fig, use_container_width=True)

        # 4.4 Cost by Environment
        st.subheader("4.4 – Cost by Environment")
        if "Environment" in viz_df.columns:
            env_fig = px.bar(
                viz_df,
                x="Environment",
                y="MonthlyCostUSD",
                color="Environment",
                title="Cost by Environment"
            )
            st.plotly_chart(env_fig, use_container_width=True)


    # ==========================================================
    # 🛠️ TAB 5 – TASK SET 5: TAG REMEDIATION WORKFLOW (Correct Version)
    # ==========================================================
    with tab5:
        st.header("🛠️ Task 5 – Tag Remediation Workflow")
        st.markdown("""
        In this section, we identify untagged resources, fix missing tags,
        export a corrected dataset, and compare tagging before and after remediation.
        """)

        # Make a working copy
        original = df.copy()

        # Required tag fields for remediation
        required_tags = ["Department", "Project", "Owner", "CostCenter", "CreatedBy", "Environment"]

        # ------------------------------------------------------
        # 5.1 — Show untagged resources
        # ------------------------------------------------------
        st.subheader("5.1 – Untagged Resources")

        # Untagged = any required tag missing
        untagged_mask = original[required_tags].isna().any(axis=1) | (original[required_tags] == "").any(axis=1)
        untagged_df = original[untagged_mask].copy()

        if untagged_df.empty:
            st.success("🎉 All resources are fully tagged!")
            st.stop()

        st.dataframe(untagged_df, use_container_width=True)

        st.info("Edit the missing fields below to remediate tagging.")

        # Editable version of missing rows
        edited = st.data_editor(
            untagged_df,
            use_container_width=True,
            num_rows="dynamic",
            key="remediation_editor"
        )

        # ------------------------------------------------------
        # 5.2 — Apply remediation
        # ------------------------------------------------------
        st.subheader("5.2 – Apply Remediation")

        if st.button("Apply Remediation"):
            remediated = original.copy()

            # Update only the remediated rows
            for rid in edited["ResourceID"]:
                row_new = edited[edited["ResourceID"] == rid].iloc[0]
                remediated.loc[remediated["ResourceID"] == rid, required_tags] = row_new[required_tags].values

            # Re-evaluate tagging
            remediated["Tagged"] = remediated[required_tags].notna().all(axis=1)
            remediated["Tagged"] = remediated["Tagged"].replace({True: "Yes", False: "No"})

            st.session_state["remediated_df"] = remediated
            st.success("✅ Remediation applied!")

        # If no remediation yet, stop here
        if "remediated_df" not in st.session_state:
            st.stop()

        remediated_df = st.session_state["remediated_df"]

        # ------------------------------------------------------
        # 5.3 — Download remediated dataset
        # ------------------------------------------------------
        st.subheader("5.3 – Download Remediated Dataset")

        st.download_button(
            "⬇️ Download remediated_cloudmart.csv",
            data=remediated_df.to_csv(index=False),
            file_name="remediated_cloudmart.csv",
            mime="text/csv"
        )

        # ------------------------------------------------------
        # 5.4 — Compare before vs after
        # ------------------------------------------------------
        st.subheader("5.4 – Tagging Comparison (Before vs After)")

        before_counts = original["Tagged"].value_counts()
        after_counts = remediated_df["Tagged"].value_counts()

        comparison = pd.DataFrame({
            "Before": before_counts,
            "After": after_counts
        }).fillna(0).astype(int)

        st.dataframe(comparison, use_container_width=True)

        # ------------------------------------------------------
        # 5.5 — Reflection
        # ------------------------------------------------------
        st.subheader("5.5 – Reflection")
        st.text_area(
            "How does improved tagging enhance cloud accountability and cost visibility?",
            height=140,
            value=(
                "Improved tagging makes it easy to understand which department, project, and owner "
                "is responsible for each cloud resource. When tags are complete, cost allocation "
                "becomes accurate and transparent, and untagged spending is reduced. This helps "
                "with budgeting, accountability, and overall cloud cost governance."
            )
        )


except FileNotFoundError:
    st.error("❌ File cloudmart_multi_account.csv not found.")
except Exception as e:
    st.error(f"Error loading dataset: {e}")
