# Markup, Markdown, and UPC Automation Guide

## How do markups affect inventory?

**Markups** increase inventory levels (increase the retail value of merchandise).

**Impact on Inventory:**
- Taking **more markups than needed** causes **shrink** (inventory value inflated, then drops at physical count)
- Taking **less markups than needed** causes **overages** (inventory value understated)

**When markups are needed:**
- Price increases due to cost changes
- Seasonal pricing adjustments
- Correcting underpriced merchandise

## How do markdowns affect inventory?

**Markdowns** decrease inventory levels (reduce the retail value of merchandise).

**Impact on Inventory:**
- Taking **more markdowns than needed** causes **overages** (inventory value reduced too much)
- Taking **less markdowns than needed** causes **shrink** (aged inventory not properly valued)

**When markdowns are needed:**
- Clearance of seasonal merchandise
- Damaged or defective goods
- Overstocked items requiring price reductions
- Competitive pricing adjustments

## What is UPC Automation?

**UPC Automation** is a system that automatically processes markups and markdowns based on on-hand changes when a price change occurred on an item in the last **50 days**.

**How UPC Automation Works:**
1. System detects a price change on an item within the last 50 days
2. System detects an on-hand change for that item
3. System automatically applies the appropriate markup or markdown
4. The adjustment appears as **GSS_AUTO** or **UpcAuto** on the Detail Departmental Markdown Report

**Why this matters:**
- Automates the markup/markdown process for efficiency
- Ensures price changes are reflected in inventory value
- Reduces manual processing requirements

## When does UPC Automation NOT apply?

UPC Automation will **not** process automatic markups/markdowns for the following exceptions:

**UPC Automation Exceptions:**
- **Cost department corrections** (Financial adjustments to department costs)
- **Cross reference errors with unlike counts** (Mismatched item references)
- **CVP (Customer Value Program) corrections** (Special program pricing adjustments)
- **Department hand keys** (Manual department entry corrections)
- **HO (Home Office) Clearance** (Markup reversals only from corporate clearance)
- **Optical manual adjustments** (Walmart Vision Center manual corrections)

**Why these exceptions exist:**
- These situations require manual review and approval
- Automated processing could create errors
- Special business rules apply

## How do I correct an incorrect UPC Automation?

If an item was automatically marked up or down by UPC Automation but **should not have been** (meets one of the exception criteria above):

**Correction Process:**
1. Verify the item meets one of the UPC Automation exception criteria
2. Access the **Miscellaneous MUMD Form in WAVE** system
3. Complete the form to correct the incorrect price change
4. Submit for processing

**Where to find UPC Automation transactions:**
- Review the **Detail Departmental Markdown Report**
- Look for transactions labeled **GSS_AUTO** or **UpcAuto**
- These identify automated markup/markdown transactions

**Important:** Only correct UPC Automation if the item truly meets an exception criteria. If the automation was correct, do not reverse it.

## Related Topics

- [IRR Reporting](../03_systems/irr_reporting.md)
- [Seasonality Impact](seasonality_impact.md)
- [Common Questions - Markdowns](../04_faqs/common_questions.md)