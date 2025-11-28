# Book vs SKU Deep Dive Guide

## What is Book vs SKU variance?

**Book vs SKU variance is the BEST PREDICTOR/INDICATOR of shrink, NOT actual shrink itself.**

The **Book vs SKU variance** measures the difference between what the financial records say the store should have (Book) and what the system thinks the store has (SKU).

**Key Definitions:**
- **Book Inventory** = Financial records based on transactions (what the store should have)
- **SKU Inventory** = System on-hand inventory calculated from current on-hands and prices (approximately 50% accurate)
- **Book vs SKU Variance** = The difference between Book and SKU (indicates RISK or LIKELIHOOD of shrink)
- **Actual Shrink** = Book minus Physical Count during annual physical inventory (measured once per year)

## What transactions impact both Book and SKU inventory?

These transactions affect **both** the financial records (Book) **and** the system on-hands (SKU) simultaneously:

**Transactions that update Book AND SKU:**
- **MTR - Merchandise** (Merchandise Transfer Requests between stores)
- **Warehouse claims** (Claims processed through the warehouse)
- **Merchandise sales** (Items sold to customers)
- **Merchandise refunds** (Customer returns)
- **RCTR/Dot.com claims** (Return Center and online order claims)
- **Supplier claims** (Claims filed with vendors)
- **Virtual claims** (Electronic claim processing)
- **Store Use** (Merchandise used by the store)
- **Markdowns** (Price reductions taken)
- **Markups** (Price increases applied)
- **Donations** (Merchandise donated)
- **In Transit** (Merchandise in transit between locations)
- **Finalized warehouse invoices** (Completed DC deliveries)

**Why this matters:**
- These transactions keep Book and SKU aligned
- Both values change together, so variance is not created
- Normal daily operations that don't increase Book vs SKU variance

## What transactions impact only SKU inventory?

These transactions affect **only** the system on-hands (SKU), not the financial records (Book), creating temporary variance:

**Transactions that update only SKU:**
- **On-hand changes** (Manual on-hand adjustments in the system)
- **Scanned out stolen** (Items marked as stolen in the system)
- **Inventory increases** (On-hand quantities increased)
- **Inventory decreases** (On-hand quantities decreased)
- **Open receivings (finalized)** (Receiving completed but not yet invoiced)

**Important Exception:**
- The **dollar value of open receivings** will impact Book **only on inventory day** when invoices are finalized

**Why this matters:**
- These transactions create Book vs SKU variance temporarily
- SKU changes immediately but Book doesn't update until later
- This is expected and acceptable for daily operations
- Understanding this helps avoid confusion when investigating variance

## What transactions impact only Book inventory?

These transactions affect **only** the financial records (Book), not the system on-hands (SKU), creating or adjusting variance:

**Transactions that update only Book:**
- **HO (Home Office) journal entries** (Corporate-level financial adjustments)
- **Retail corrections** (Price or value corrections in the financial system)
- **Sales adjustments** (Financial adjustments to sales records)
- **MTR - Financial** (Auto MTRs for financial transfers only)
- **EDI - Releasing for payment** (Electronic Data Interchange invoice releases)
- **PODs (Proof of Delivery)** (Delivery confirmations)
- **Claim chargebacks** (Vendor claim charge-backs)
- **Credit memos** (Vendor credits issued)
- **CFT payments** (Cash Flow Through payments, such as alcohol)
- **Pay from scan accruals** (Accrued payment amounts)
- **After inventory adjustment** (Month after physical inventory only)
- **Pre-charged invoices** (Invoices charged before merchandise arrives)
- **119x entries** (Specific financial entry codes)
- **Unfinalized invoices** (Invoices not yet completed)

**Why this matters:**
- These transactions create or change Book vs SKU variance
- Book changes immediately but SKU remains the same
- Important to understand when investigating unexplained variance
- Some variance from these transactions is expected and acceptable

## How do I know if my Book vs SKU variance is normal?

Understanding which transactions affect Book, SKU, or both helps determine if variance is expected or requires investigation:

**Normal, Expected Variance:**
- Temporary variance from open receivings (will resolve when invoiced)
- Variance from pre-charged invoices (merchandise not yet received)
- Variance from HO journal entries (corporate adjustments)

**Variance Requiring Investigation:**
- Consistently increasing variance month-over-month
- Large, unexplained changes in variance
- Variance concentrated in specific departments
- Negative variance (SKU higher than Book) without explanation

**Action Steps:**
1. Review the **Inventory Recap Report (IRR)** monthly
2. Compare Book vs SKU variance to previous months
3. Identify which category is driving the variance (SKU changes, purchases, markdowns, sales)
4. Use the IRR Dashboard tabs to drill deeper into the specific transactions
5. Partner with Asset Protection if theft is suspected

## Related Topics

- [Inventory Terminology](../01_core_concepts/inventory_terminology.md)
- [IRR Reporting](irr_reporting.md)
- [Troubleshooting Book vs SKU Variance](../05_troubleshooting/book_sku_variance.md)