import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------------------------------------
# APP CONFIG
# ----------------------------------------------------------
st.set_page_config(page_title="Week 10 - Task Sets 1 & 2", layout="wide")
st.title("☁️ CloudMart – Task Set 1 & 2 Dashboard")

st.markdown("""
This app completes **Task Set 1 – Data Exploration**  
and **Task Set 2 – Cost Visibility**  
for the Week 10 Cloud Resource Tagging case study.
""")

file_path = "cloudmart_multi_account.csv"

try:
    # ----------------------------------------------------------
    # ✅ CREATE BOTH TABS TOGETHER
    # ----------------------------------------------------------
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📘 Task 1 – Data Exploration",
        "💰 Task 2 – Cost Visibility",
        "🏷️ Task 3 – Tagging Compliance",
        "📊 Task 4 – Visualization Dashboard",
        "🛠️ Task 5 – Tag Remediation Workflow",
        "🧾 Task 6 – Summary Report"
    ])



    # ==========================================================
    # 📘 TAB 1 – TASK SET 1: DATA EXPLORATION
    # ==========================================================
    with tab1:
        # ----------------------------------------------------------
        # 1.1 LOAD DATASET AND DISPLAY FIRST 5 ROWS
        # ----------------------------------------------------------
        with open(file_path, "r", encoding="utf-8-sig") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        split_data = [line.split(",") for line in lines]
        df = pd.DataFrame(split_data[1:], columns=split_data[0])

        # Clean column names and quotes
        df.columns = df.columns.str.replace('"', '').str.strip()
        df = df.applymap(lambda x: x.strip().replace('"', '') if isinstance(x, str) else x)

        # Convert cost column to numeric
        if "MonthlyCostUSD" in df.columns:
            df["MonthlyCostUSD"] = pd.to_numeric(df["MonthlyCostUSD"], errors="coerce")

        st.subheader("📋 1.1 – Dataset Preview (First 5 Rows)")
        st.dataframe(df.head(), use_container_width=True)

        # -------------------------------------------
        # 🌐 GLOBAL FILTERS (shared across tabs)
        # -------------------------------------------
        st.sidebar.header("🎛️ Global Filters")

        def get_unique(col):
            return sorted(df[col].dropna().unique().tolist()) if col in df.columns else []

        dept_filter  = st.sidebar.multiselect("Department", get_unique("Department"), default=None)
        proj_filter  = st.sidebar.multiselect("Project", get_unique("Project"), default=None)
        env_filter   = st.sidebar.multiselect("Environment", get_unique("Environment"), default=None)
        svc_filter   = st.sidebar.multiselect("Service", get_unique("Service"), default=None)
        region_filter = st.sidebar.multiselect("Region", get_unique("Region"), default=None)

        # Apply filters
        filtered_df = df.copy()
        if dept_filter:  filtered_df = filtered_df[filtered_df["Department"].isin(dept_filter)]
        if proj_filter:  filtered_df = filtered_df[filtered_df["Project"].isin(proj_filter)]
        if env_filter:   filtered_df = filtered_df[filtered_df["Environment"].isin(env_filter)]
        if svc_filter:   filtered_df = filtered_df[filtered_df["Service"].isin(svc_filter)]
        if region_filter:filtered_df = filtered_df[filtered_df["Region"].isin(region_filter)]

        st.sidebar.success(f"Filters applied: {len(filtered_df)} rows displayed")



        # ----------------------------------------------------------
        # 1.2 CHECK FOR MISSING VALUES
        # ----------------------------------------------------------
        st.subheader("🔍 1.2 – Missing Values Check")
        missing_summary = df.isnull().sum().reset_index()
        missing_summary.columns = ["Column Name", "Missing Values"]
        st.dataframe(missing_summary, use_container_width=True, height=280)

        # ----------------------------------------------------------
        # 1.3 IDENTIFY COLUMNS WITH MOST MISSING VALUES
        # ----------------------------------------------------------
        st.subheader("📊 1.3 – Columns with Most Missing Values")
        most_missing = missing_summary.sort_values("Missing Values", ascending=False)
        st.bar_chart(most_missing.set_index("Column Name"))

        # ----------------------------------------------------------
        # 1.4 COUNT TAGGED VS UNTAGGED RESOURCES
        # ----------------------------------------------------------
        st.subheader("📦 1.4 – Tagged vs Untagged Resources")

        if "Tagged" in df.columns:
            tagged_counts = df["Tagged"].value_counts()
            total_resources = len(df)
            tagged = tagged_counts.get("Yes", 0)
            untagged = tagged_counts.get("No", 0)

            c1, c2, c3 = st.columns(3)
            c1.metric("Total Resources", total_resources)
            c2.metric("Tagged", tagged)
            c3.metric("Untagged", untagged)

            # ------------------------------------------------------
            # 1.5 PERCENTAGE OF UNTAGGED RESOURCES
            # ------------------------------------------------------
            st.subheader("📈 1.5 – Percentage of Untagged Resources")
            if total_resources > 0:
                percent_untagged = (untagged / total_resources) * 100
                st.metric("Untagged Resources (%)", f"{percent_untagged:.2f}%")
            else:
                st.warning("Dataset is empty – cannot compute percentage.")

            # ------------------------------------------------------
            # VISUALS SIDE BY SIDE
            # ------------------------------------------------------
            st.subheader("📊 Visual Insights")
            col1, col2 = st.columns(2)

            # Chart 1 – Cost by Department
            with col1:
                if "MonthlyCostUSD" in filtered_df.columns and "Department" in filtered_df.columns:
                    dept_cost = (
                        filtered_df.groupby("Department")["MonthlyCostUSD"].sum().reset_index()
                    )
                    fig1, ax1 = plt.subplots()
                    ax1.bar(dept_cost["Department"], dept_cost["MonthlyCostUSD"])
                    ax1.set_xlabel("Department")
                    ax1.set_ylabel("Monthly Cost (USD)")
                    ax1.set_title("💰 Cost by Department")
                    st.pyplot(fig1)

            # Chart 2 – Tagged vs Untagged
            with col2:
                fig2, ax2 = plt.subplots()
                ax2.pie(
                    [tagged, untagged],
                    labels=["Tagged", "Untagged"],
                    autopct="%1.1f%%",
                    startangle=90,
                )
                ax2.set_title("🏷️ Tagged vs Untagged Resources")
                st.pyplot(fig2)
        else:
            st.warning("⚠️ No 'Tagged' column found in dataset.")

    # ==========================================================
    # 💰 TAB 2 – TASK SET 2: COST VISIBILITY (COMPACT)
    # ==========================================================
    with tab2:
        st.header("💰 Task Set 2 – Cost Visibility")
        st.markdown("""
        This section addresses **Task Set 2** from the Week 10 case study.  
        It explores cloud cost visibility using tagging data.
        """)

        if "Tagged" in df.columns and "MonthlyCostUSD" in df.columns:
            # 2.1 Total cost by tag
            st.subheader("2.1 – Total Cost of Tagged vs Untagged Resources")
            cost_by_tag = df.groupby("Tagged")["MonthlyCostUSD"].sum().reset_index()
            st.dataframe(cost_by_tag, use_container_width=True)

            c1, c2 = st.columns(2)
            with c1:
                fig3, ax3 = plt.subplots(figsize=(3.5, 2.5))
                ax3.bar(cost_by_tag["Tagged"], cost_by_tag["MonthlyCostUSD"],
                        color=["#2E86AB", "#E27D60"])
                ax3.set_xlabel("Tag Status", fontsize=8)
                ax3.set_ylabel("Total Cost (USD)", fontsize=8)
                ax3.set_title("💰 Total Cost by Tag", fontsize=10)
                plt.tight_layout()
                st.pyplot(fig3, use_container_width=True)

            # 2.2 % of total cost untagged
            total_cost = df["MonthlyCostUSD"].sum()
            untagged_cost = cost_by_tag.loc[
                cost_by_tag["Tagged"] == "No", "MonthlyCostUSD"
            ].sum()
            with c2:
                st.metric("Untagged Cost (%)",
                        f"{(untagged_cost/total_cost*100):.2f}%" if total_cost > 0 else "N/A")

            # 2.3 Department with most untagged cost
            st.subheader("2.3 – Department with the Most Untagged Cost")
            dept_tag_cost = (
                df.groupby(["Department", "Tagged"])["MonthlyCostUSD"].sum().reset_index()
            )
            untagged_dept = (
                dept_tag_cost[dept_tag_cost["Tagged"] == "No"]
                .sort_values("MonthlyCostUSD", ascending=False)
                .head(1)
            )
            st.dataframe(untagged_dept, use_container_width=True)

            # 2.4 Project consuming most cost
            st.subheader("2.4 – Project Consuming the Most Cost Overall")
            proj_cost = df.groupby("Project")["MonthlyCostUSD"].sum().reset_index()
            proj_cost = proj_cost.sort_values("MonthlyCostUSD", ascending=False)
            st.dataframe(proj_cost.head(1), use_container_width=True)

            fig4, ax4 = plt.subplots(figsize=(4, 2.8))
            ax4.bar(proj_cost["Project"], proj_cost["MonthlyCostUSD"], color="#6A5ACD")
            ax4.set_xlabel("Project", fontsize=8)
            ax4.set_ylabel("Total Cost (USD)", fontsize=8)
            ax4.set_title("📊 Project Cost Comparison", fontsize=10)
            ax4.tick_params(axis="x", rotation=45, labelsize=7)
            plt.tight_layout()
            st.pyplot(fig4, use_container_width=True)

            # 2.5 Prod vs Dev comparison
            st.subheader("2.5 – Compare Prod vs Dev Environments")
            if "Environment" in df.columns:
                env_cost_tag = (
                    df.groupby(["Environment", "Tagged"])["MonthlyCostUSD"].sum().reset_index()
                )
                st.dataframe(env_cost_tag, use_container_width=True)

                fig5, ax5 = plt.subplots(figsize=(4, 2.8))
                for tag_status in env_cost_tag["Tagged"].unique():
                    subset = env_cost_tag[env_cost_tag["Tagged"] == tag_status]
                    ax5.bar(subset["Environment"], subset["MonthlyCostUSD"], label=tag_status)
                ax5.set_xlabel("Environment", fontsize=8)
                ax5.set_ylabel("Monthly Cost (USD)", fontsize=8)
                ax5.set_title("🏭 Prod vs Dev – Cost & Tag Quality", fontsize=10)
                ax5.legend(title="Tag", fontsize=7)
                plt.tight_layout()
                st.pyplot(fig5, use_container_width=True)
            else:
                st.warning("⚠️ No 'Environment' column found in dataset.")
        else:
            st.warning("⚠️ Missing 'Tagged' or 'MonthlyCostUSD' columns.")

    # ==========================================================
    # 🏷️ TAB 3 – TASK SET 3: TAGGING COMPLIANCE
    # ==========================================================
    with tab3:
        st.header("🏷️ Task Set 3 – Tagging Compliance")
        st.markdown("""
        This section completes **Task Set 3** of the Week 10 case study.  
        It measures tagging completeness and identifies gaps.
        """)

        # Columns used to check completeness
        tag_fields = [
            "Department", "Project", "Environment", "Owner",
            "CostCenter", "CreatedBy", "Tagged"
        ]

        if all(col in df.columns for col in tag_fields):
            # ------------------------------------------------------
            # 3.1 TAG COMPLETENESS SCORE PER RESOURCE
            # ------------------------------------------------------
            st.subheader("3.1 – Tag Completeness Score per Resource")

            df["TagCompletenessScore"] = df[tag_fields].apply(
                lambda row: sum(pd.notna(row) & (row != "")), axis=1
            )

            st.dataframe(df[["ResourceID", "TagCompletenessScore"]].head(),
                        use_container_width=True)

            # ------------------------------------------------------
            # 3.2 TOP 5 RESOURCES WITH LOWEST SCORES
            # ------------------------------------------------------
            st.subheader("3.2 – Top 5 Resources with Lowest Completeness Scores")
            lowest5 = df.nsmallest(5, "TagCompletenessScore")[["ResourceID", "TagCompletenessScore"]]
            st.dataframe(lowest5, use_container_width=True)

            # ------------------------------------------------------
            # 3.3 MOST FREQUENTLY MISSING TAG FIELDS
            # ------------------------------------------------------
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

            # ------------------------------------------------------
            # 3.4 LIST ALL UNTAGGED RESOURCES AND THEIR COSTS
            # ------------------------------------------------------
            st.subheader("3.4 – List of Untagged Resources and Costs")
            untagged_df = df[df["Tagged"].str.lower() == "no"][["ResourceID", "MonthlyCostUSD"]]
            st.dataframe(untagged_df, use_container_width=True)

            # ------------------------------------------------------
            # 3.5 EXPORT UNTAGGED RESOURCES TO CSV
            # ------------------------------------------------------
            st.subheader("3.5 – Export Untagged Resources to CSV")
            csv_path = "untagged_resources.csv"
            untagged_df.to_csv(csv_path, index=False)
            st.success(f"✅ Exported untagged resources to **{csv_path}**")
            st.download_button("⬇️ Download Untagged CSV", data=untagged_df.to_csv(index=False),
                            file_name="untagged_resources.csv", mime="text/csv")

        else:
            st.warning("⚠️ Some required tag columns are missing in the dataset.")

    # ==========================================================
    # 📊 TAB 4 – TASK SET 4: VISUALIZATION DASHBOARD
    # ==========================================================
    with tab4:
        import plotly.express as px
        st.header("📊 Task Set 4 – Visualization Dashboard")
        st.markdown("""
        Interactive dashboard exploring cost and tagging insights.
        """)

        # 4.5 Interactive filters
        st.sidebar.subheader("🎛️ Dashboard Filters")
        svc_sel = st.sidebar.multiselect("Filter by Service", sorted(df["Service"].unique()))
        region_sel = st.sidebar.multiselect("Filter by Region", sorted(df["Region"].unique()))
        dept_sel = st.sidebar.multiselect("Filter by Department", sorted(df["Department"].unique()))

        viz_df = df.copy()
        if svc_sel: viz_df = viz_df[viz_df["Service"].isin(svc_sel)]
        if region_sel: viz_df = viz_df[viz_df["Region"].isin(region_sel)]
        if dept_sel: viz_df = viz_df[viz_df["Department"].isin(dept_sel)]

        # 4.1 Pie chart – Tagged vs Untagged
        st.subheader("4.1 – Tagged vs Untagged Resources ( Pie Chart )")
        if "Tagged" in viz_df.columns:
            pie_fig = px.pie(viz_df, names="Tagged", title="Tag Distribution", color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(pie_fig, use_container_width=True)

        # 4.2 Bar chart – Cost per Department by Tagging
        st.subheader("4.2 – Cost per Department by Tagging Status")
        if "Department" in viz_df.columns and "Tagged" in viz_df.columns:
            dept_cost = viz_df.groupby(["Department", "Tagged"])["MonthlyCostUSD"].sum().reset_index()
            bar_fig = px.bar(dept_cost, x="Department", y="MonthlyCostUSD", color="Tagged",
                            barmode="group", title="Cost by Department and Tag Status")
            st.plotly_chart(bar_fig, use_container_width=True)

        # 4.3 Horizontal bar – Cost per Service
        st.subheader("4.3 – Total Cost per Service (Horizontal Bar)")
        svc_cost = viz_df.groupby("Service")["MonthlyCostUSD"].sum().reset_index()
        svc_fig = px.bar(svc_cost, y="Service", x="MonthlyCostUSD", orientation="h",
                        title="Total Cost per Service", color_discrete_sequence=["#6A5ACD"])
        st.plotly_chart(svc_fig, use_container_width=True)

        # 4.4 Environment cost overview
        st.subheader("4.4 – Cost by Environment ( Prod vs Dev vs Test )")
        if "Environment" in viz_df.columns:
            env_fig = px.bar(viz_df, x="Environment", y="MonthlyCostUSD",
                            color="Environment", title="Cost by Environment")
            st.plotly_chart(env_fig, use_container_width=True)

    # ==========================================================
    # 🛠️ TAB 5 – TASK SET 5: TAG REMEDIATION WORKFLOW
    # ==========================================================
    with tab5:
        st.header("🛠️ Task Set 5 – Tag Remediation Workflow")
        st.markdown("""
        In this section, simulate tag remediation by filling missing fields and re-evaluating cost metrics.
        """)

        # 5.1 Editable table of untagged resources
        st.subheader("5.1 – Edit Untagged Resources (Table)")
        untagged = df[df["Tagged"].str.lower() == "no"].copy()
        edited = st.data_editor(
            untagged,
            num_rows="dynamic",
            key="tag_remediation_table",
            use_container_width=True
        )

        # 5.2 Manual remediation (simulated)
        st.subheader("5.2 – Fill Missing Tags (Manual Simulation)")
        st.markdown("### 🧩 5.2 – Fill Missing Tags (Manual Simulation)")
        st.markdown("Add or update missing tag values interactively below:")

        col1, col2, col3 = st.columns(3)
        with col1:
            dept_fill = st.selectbox("Department", sorted(df["Department"].dropna().unique()), key="dept_fill")
        with col2:
            proj_fill = st.selectbox("Project", sorted(df["Project"].dropna().unique()), key="proj_fill")
        with col3:
            owner_fill = st.text_input("Owner (Email)", "example@cloudmart.com", key="owner_fill")

        if st.button("Apply Sample Tags to Missing Entries"):
            edited.loc[edited["Department"] == "", "Department"] = dept_fill
            edited.loc[edited["Project"] == "", "Project"] = proj_fill
            edited.loc[edited["Owner"] == "", "Owner"] = owner_fill
            st.success("✅ Sample tags filled where missing!")


        # 5.3 Download updated dataset
        st.subheader("5.3 – Download Updated Dataset")
        csv_data = edited.to_csv(index=False)
        st.download_button("⬇️ Download Remediated CSV", data=csv_data,
                        file_name="remediated_cloudmart.csv", mime="text/csv")

        # 5.4 Compare cost visibility before vs after
        st.subheader("5.4 – Compare Cost Visibility Before and After")
        before = df["Tagged"].value_counts()
        after = edited["Tagged"].value_counts()
        comp = pd.DataFrame({"Before": before, "After": after}).fillna(0).astype(int)
        st.dataframe(comp, use_container_width=True)

        # 5.5 Reflection
        st.subheader("5.5 – Discussion")
        st.markdown("""
        Improved tagging enhances accountability and financial reporting by making resource-level costs visible.  
        It also simplifies chargeback and governance across departments.
        """)

    # ==========================================================
    # 🧾 TAB 6 – SUMMARY REPORT
    # ==========================================================
    with tab6:
        st.header("🧾 Task 6 – Summary Report")
        st.markdown("""
        A concise summary highlighting tagging gaps, cost impact, and governance recommendations.
        """)

        # --- % of untagged resources ---
        if "Tagged" in df.columns:
            tagged_counts = df["Tagged"].value_counts()
            total_resources = len(df)
            untagged = tagged_counts.get("No", 0)
            percent_untagged = (untagged / total_resources) * 100 if total_resources > 0 else 0
        else:
            percent_untagged = 0

        # --- Total untagged cost ---
        if "MonthlyCostUSD" in df.columns:
            untagged_cost = df.loc[df["Tagged"].str.lower() == "no", "MonthlyCostUSD"].sum()
        else:
            untagged_cost = 0

        # --- Departments with missing tags ---
        tag_fields = ["Department", "Project", "Environment", "Owner", "CostCenter", "CreatedBy", "Tagged"]
        missing_by_dept = (
            df[tag_fields].isna().groupby(df["Department"]).sum()
            if "Department" in df.columns else pd.DataFrame()
        )

        # Display metrics
        c1, c2 = st.columns(2)
        c1.metric("Untagged Resources (%)", f"{percent_untagged:.2f}%")
        c2.metric("Total Untagged Cost (USD)", f"${untagged_cost:,.2f}")

        st.subheader("Departments with Most Missing Tags")
        if not missing_by_dept.empty:
            missing_summary = missing_by_dept.sum(axis=1).sort_values(ascending=False).reset_index()
            missing_summary.columns = ["Department", "Missing Tags"]
            st.dataframe(missing_summary.head(5), use_container_width=True)
        else:
            st.info("No department-level missing tag data available.")

        # --- Recommendations ---
        st.subheader("Recommendations for Governance Improvement")
        st.markdown("""
        - ✅ **Enforce mandatory tag policies** in the cloud management portal for key fields like *Department*, *Owner*, and *Cost Center*.  
        - 🧩 **Automate tag validation** via serverless scripts or AWS Config Rules to detect untagged resources in real time.  
        - 💰 **Implement cost accountability dashboards** so departments can track their own tagged vs untagged spending.  
        - 🧭 **Schedule monthly audits** to export untagged CSV reports and remediate missing information.  
        - 🪄 **Adopt tag inheritance or templates** in provisioning workflows to ensure every resource gets baseline tags.
        """)


except FileNotFoundError:
    st.error("❌ File `cloudmart_multi_account.csv` not found.")
except Exception as e:
    st.error(f"Error loading dataset: {e}")
