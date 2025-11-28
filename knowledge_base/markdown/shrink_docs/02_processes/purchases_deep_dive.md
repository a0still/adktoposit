# Purchases Deep Dive Guide

## When should I research purchases in my store?

**Purchases may be driving increases in ending inventory levels**, especially if purchases are unnecessary or contain errors. When the **Inventory Recap Report (IRR)** shows high purchase variance, investigate to identify the specific purchase components causing the issue.

**Key Indicators for Purchase Research:**
- **Purchases column on IRR is higher than normal** for a department
- **Book vs SKU variance is driven by purchases** (not SKU changes or markdowns)
- **Inventory levels growing faster than sales** suggest over-purchasing
- **Month-over-month purchase increases** without corresponding sales growth

**Why Research Purchases:**
- Identify receiving errors that inflate inventory value
- Find vendor billing issues or short-shipments
- Detect unnecessary purchases that create overstock
- Correct financial transactions that impact Book inventory

---

## What purchase components require the most research?

Focus research efforts on purchase components that typically contain the most exceptions and errors:

### High-Priority Components (RED - Most Research Needed)

**1. Invoice Payments (Pay from Receipt - PFR Receivings)**
- **What it is:** Receivings that have been invoiced and paid for
- **Why research:** Most common source of purchase variance
- **How to research:** Use **Custom Reports tab → NG Receiving Detail** report
- **What to look for:** Quantity discrepancies, receiving errors, vendor issues

**2. Retail Corrections**
- **What it is:** Financial corrections to purchase values
- **Why research:** Can indicate pricing errors or system issues
- **How to research:** Review correction logs and approval records
- **What to look for:** Unexplained value adjustments, repeated corrections

**3. Warehouse Trucks**
- **What it is:** Merchandise received from Distribution Centers
- **Why research:** High volume increases error probability
- **How to research:** Use receiving reports and BOL (Bill of Lading) verification
- **What to look for:** Mis-picks, short-shipments, receiving to wrong items

### Medium-Priority Components (GREEN - Easier Research, Fewer Exceptions)

**1. MTRs (Merchandise Transfer Requests)**
- **What it is:** Transfers between stores
- **Why research:** Can create inventory imbalances
- **How to research:** Review transfer logs and confirmations
- **What to look for:** Uncompleted transfers, quantity mismatches

**2. Property Loss Claims (Through WCS)**
- **What it is:** Claims filed through Walmart Claims Services
- **Why research:** May indicate theft or damage issues
- **How to research:** Review claim documentation and approvals
- **What to look for:** Frequent claims, high-value losses

**3. Return Center Claims**
- **What it is:** Returns processed through Return Center
- **Why research:** Can affect purchase reconciliation
- **How to research:** Review return processing records
- **What to look for:** Processing delays, quantity discrepancies

**4. Shrink Result (Month After Inventory Only)**
- **What it is:** Financial adjustments after physical inventory
- **Why research:** Post-inventory corrections
- **How to research:** Review inventory adjustment records
- **What to look for:** Large post-inventory adjustments

### Other Purchase Components (Standard Research)

**Additional Components to Monitor:**
- **CFT Alcohol Payments** (where applicable)
- **Claim Chargebacks** (Vendor charge-backs)
- **Claims Filed** (Proof of Deliveries, WMDC Return Request Claims)
- **Credit Memos** (Vendor credits)
- **Journal Entries** (Credits or debits)
- **Merchandise Transmittals** (Internal transfers)
- **Optical Labs** (Walmart Vision Centers only)
- **Pay from Scan Transactions** (Scan-based payments)
- **State Charges/Fees** (CRV charges where applicable)
- **Warehouse Credits** (DC credits and adjustments)

---

## How do I research purchases using the Custom Reports tab?

When the IRR shows purchases driving variance, use this step-by-step process to investigate the details:

### Step 1: Identify Purchase Variance on the IRR

**What to do:**
1. Open the **Inventory Recap Report (IRR)**
2. Look at the **Purchases column** for each department
3. Identify departments with **unusually high purchases** compared to normal
4. Note which departments are driving the purchase variance

### Step 2: Access Custom Reports for Purchase Details

**Navigation Path:**
1. Go to the **Custom Reports tab** in the IRR Dashboard
2. Look for **purchase-related reports** in the available reports list
3. Select the appropriate report based on your investigation needs

### Step 3: Use Specific Purchase Reports

**For Receiving Issues (Most Common):**
- **Report Name:** "NG Receiving Detail"
- **What it shows:** Detailed receiving transactions with quantities, dates, vendors
- **How to use:** Filter by department and date range to investigate specific receiving issues
- **What to look for:** Quantity mismatches, missing receivings, vendor errors

**For General Purchase Research:**
- **Report Name:** "Purchase Transaction Detail"
- **What it shows:** All purchase transactions by component type
- **How to use:** Filter by department and component to identify problem areas
- **What to look for:** Unusual transaction patterns, high-value adjustments

**For Vendor-Specific Issues:**
- **Report Name:** "Vendor Purchase Summary"
- **What it shows:** Purchase totals by vendor and department
- **How to use:** Identify vendors with consistently high purchase variance
- **What to look for:** Vendor-specific patterns, repeated issues

### Step 4: Analyze the Purchase Data

**Key Analysis Points:**

**1. Identify the Purchase Component**
- Look at the **transaction type** field in the report
- Determine if variance is from **receivings, corrections, transfers, or other components**
- Focus on the **RED priority components** first (receivings, corrections, warehouse)

**2. Review Transaction Details**
- **Check dates** - Are purchases concentrated in specific time periods?
- **Check vendors** - Are specific vendors causing issues?
- **Check quantities** - Are quantities unusually high or low?
- **Check values** - Are dollar amounts consistent with expectations?

**3. Look for Patterns**
- **Receiving errors** - Consistently lower quantities than invoiced
- **Vendor issues** - Same vendor showing problems repeatedly
- **Timing patterns** - Errors occurring on specific days or shifts
- **Department patterns** - Certain departments having more issues

### Step 5: Take Action Based on Findings

**If Receiving Errors Found:**
1. **Review receiving procedures** with the receiving team
2. **Verify BOL quantities** against actual received merchandise
3. **Train associates** on proper receiving documentation
4. **Contact vendors** about consistent shipping errors

**If Vendor Billing Issues Found:**
1. **Document discrepancies** with specific invoices and dates
2. **Contact vendor representatives** to resolve billing errors
3. **Submit claims** for short-shipments or incorrect charges
4. **Monitor future shipments** from problematic vendors

**If Process Issues Found:**
1. **Update procedures** to prevent future errors
2. **Train affected associates** on correct processes
3. **Implement additional controls** for high-error areas
4. **Monitor improvements** in following months

---

## What are common purchase research scenarios?

### Scenario 1: High Receivings Driving Variance

**Situation:** IRR shows purchases high, investigation reveals receiving issues

**Research Steps:**
1. Go to **Custom Reports tab → NG Receiving Detail**
2. Filter by the high-variance department and recent date range
3. Review receiving quantities vs. invoice quantities
4. Identify specific vendors or items with consistent discrepancies
5. Document findings and contact receiving team

**Expected Findings:**
- Receivings with lower quantities than invoiced
- Missing documentation for received merchandise
- Vendor short-shipments not properly documented

### Scenario 2: Retail Corrections Causing Issues

**Situation:** Purchase variance driven by financial corrections

**Research Steps:**
1. Review correction logs in the system
2. Identify who made corrections and why
3. Verify if corrections were justified and properly approved
4. Look for patterns in correction timing or amounts

**Expected Findings:**
- Corrections made without proper investigation
- System pricing errors requiring frequent corrections
- Associates adjusting values without physical verification

### Scenario 3: Warehouse Truck Issues

**Situation:** DC deliveries causing purchase variance

**Research Steps:**
1. Review warehouse receiving reports
2. Compare BOL quantities to actual received quantities
3. Check for mis-picks or wrong items shipped
4. Document pattern of DC shipping errors

**Expected Findings:**
- Consistent short-shipments from specific DCs
- Wrong items shipped requiring corrections
- Damage during transit not properly documented

---

## How do I prevent future purchase issues?

### Proactive Prevention Strategies

**1. Improve Receiving Accuracy**
- **Count everything received** - Never trust BOL quantities without verification
- **Document discrepancies immediately** - Note shortages or overages on receiving documents
- **Train receiving team** on proper procedures and documentation
- **Verify item numbers** to ensure receiving to correct merchandise

**2. Monitor Vendor Performance**
- **Track vendor error rates** by department and time period
- **Address consistent issues** with vendor representatives
- **Document all discrepancies** for future reference
- **Consider alternative vendors** for consistently problematic suppliers

**3. Strengthen Financial Controls**
- **Require justification** for all retail corrections
- **Implement approval workflows** for high-value adjustments
- **Review correction patterns** monthly for unusual activity
- **Audit purchase transactions** regularly for compliance

**4. Use Data Proactively**
- **Review purchase trends** monthly before variance becomes problematic
- **Set alerts** for unusual purchase patterns or increases
- **Monitor component breakdowns** to identify emerging issues
- **Track improvement metrics** after implementing changes

---

## Related Topics

- [Using Custom Reports for Purchases](using_custom_reports_for_purchases.md) - Step-by-step Custom Reports guidance
- [Root Cause Analysis](root_cause_analysis.md) - Systematic investigation methodology
- [IRR Reporting](../03_systems/irr_reporting.md) - Understanding IRR metrics and tabs
- [Common Questions - Purchases](../04_faqs/common_questions.md) - FAQ about purchase research
