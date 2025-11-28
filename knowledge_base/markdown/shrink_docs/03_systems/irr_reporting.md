# Inventory Recap Report (IRR) System Guide

## What is the Inventory Recap Report (IRR)?

The **Inventory Recap Report (IRR)** is a monthly reporting tool that tracks key inventory and shrink metrics at **store and department level**.

**Purpose of the IRR:**
- Primary tool for identifying shrink indicators and drivers
- Tracks monthly performance trends
- Provides historical data for comparison
- Helps prioritize which departments need investigation

**Key Metrics Tracked on the IRR:**
- **Book Inventory** - Financial records of what the store should have
- **SKU Inventory** - System on-hand inventory (approximately 50% accurate)
- **Book vs SKU Variance** - The best predictor/indicator of potential shrink
- **Purchases** - Merchandise bought and invoiced
- **Markdowns** - Price reductions taken
- **Sales** - Merchandise sold to customers

**Historical Reporting:** The IRR provides access to previous months' data, allowing trend analysis and year-over-year comparisons.

## What is the IRR Drilldown tool?

The **IRR Drilldown** is a **Power BI tool** that provides deeper analysis and transaction-level detail beyond the standard IRR report.

**Purpose of IRR Drilldown:**
- Directs Store Managers toward specific issues impacting the store
- Identifies problems at a **transactional level** rather than just summary level
- Provides detailed views of what's driving variance
- Allows investigation of specific items or transactions

**When to Use IRR Drilldown:**
- After identifying high-variance departments on the standard IRR
- When investigating specific shrink drivers (purchases, markdowns, on-hand changes)
- To analyze transaction patterns and trends
- To drill into item-level detail for root cause analysis

## What is the difference between IRR Tool and IRR Drilldown?

Both tools present similar information but with different levels of detail and timeframes:

### IRR Tool (Standard Report):
- **Updated:** Monthly
- **Data Range:** Shows 24 rolling months of data
- **Format:** Graph and summary views
- **Use Case:** High-level department variance identification
- **Best For:** Monthly shrink reviews, identifying problem departments

### IRR Drilldown (Power BI Tool):
- **Updated:** Monthly (with more recent transaction data)
- **Data Range:** Shows up to 36 rolling months of data in graph form
- **Format:** Detailed transaction views AND graphs
- **Use Case:** Deep-dive investigation of specific issues
- **Best For:** Root cause analysis, transaction-level research

**Key Difference:** The IRR Drilldown provides a **detailed view of transactions** impacting the store in the most recent month, while the standard IRR focuses on summary-level trends.

## What should I look for when researching the IRR?

Follow this systematic approach when reviewing the **Inventory Recap Report (IRR)**:

### Step 1: Review Departmental Information

**What to review:**
- **Book vs SKU variance by department** - Which departments have the highest variance?
- **Inventory levels** - Are any departments growing faster than sales?
- **Trend direction** - Are variances increasing, decreasing, or stable?

**Focus areas:**
- Identify the top 3-5 departments with highest Book vs SKU variance
- Look for departments with unusual patterns or significant changes

### Step 2: Identify Primary Shrink Growth Alerts

**Primary Alerts Indicating Shrink Growth:**

1. **Month-over-Month Book Inventory Growth**
   - Book Inventory increasing without corresponding sales increases
   - Suggests merchandise is being purchased but not sold (theft or operational issues)
   - Compare current month Book to previous month Book

2. **Month-over-Month Book vs SKU Growth**
   - Book vs SKU variance getting larger each month
   - Indicates shrink risk is increasing
   - Requires immediate investigation and action

**How to identify:**
- Compare current month to previous month
- Look for increasing trends over multiple months
- Flag departments where variance is growing consistently

### Step 3: Review Same-Month Alerts and Item Alerts

**What to check:**
- **Same-month comparisons** - Compare current January to last January (year-over-year)
- **Item-level alerts** - Which specific items are driving department variance?
- **Pattern recognition** - Are the same items or departments problematic month after month?

### Step 4: Identify Drivers of Red Flags

Once a department shows high variance, determine which category is driving the problem:

**Variance Drivers to Investigate:**

1. **On-Hand Changes**
   - **OH (On-Hand) Changes** - Manual on-hand adjustments
   - **Scanned Out Stolen** - Items documented as stolen
   - **Inventory Increases/Decreases** - System on-hand adjustments
   - **Analysis:** Are associates adjusting on-hands frequently? Why?

2. **Markdowns**
   - Are markdown dollars higher or lower than expected?
   - Are markdowns being taken appropriately for aged/damaged merchandise?
   - **Analysis:** Could low markdowns be hiding shrink?

3. **Purchases**
   - Are purchases significantly higher than normal?
   - Are receiving errors inflating purchase variance?
   - **Analysis:** Review receiving processes and vendor accuracy

4. **Sales**
   - Are sales lower than expected given inventory levels?
   - Could theft be causing merchandise to leave without being sold?
   - **Analysis:** Partner with Asset Protection to investigate

**Next Step:** Use the IRR Dashboard tabs (Purchases, Sales, etc.) to drill deeper into the identified driver.

## How do I use the IRR to measure improvement?

Track progress over time using the **Inventory Recap Report (IRR)** monthly:

**Metrics to Monitor:**
- **Book vs SKU variance trend** - Is it decreasing after implementing actions?
- **Department-level changes** - Are problem departments improving?
- **Category drivers** - Are the specific drivers (purchases, markdowns, etc.) getting better?
- **Overall store variance** - Is total store shrink risk decreasing?

**Success Indicators:**
- Decreasing Book vs SKU variance month-over-month
- Fewer departments in "red flag" status
- Improved on-hand accuracy (smaller SKU adjustments)
- Better alignment between Book and SKU

**Use IRR for Accountability:** Review IRR results in weekly management meetings to track action plan effectiveness and adjust strategies as needed.

## Related Topics

- [Shrink Definition](../01_core_concepts/shrink_definition.md)
- [Book vs SKU Deep Dive](book_vs_sku.md)
- [Root Cause Analysis](../02_processes/root_cause_analysis.md)
- [Troubleshooting Book vs SKU Variance](../05_troubleshooting/book_sku_variance.md)