## Deep Diving Markup/Markdown & UPC Automation

### Markups
* Increase inventory levels
* Taking **more than needed** causes **shrink**
* Taking **less than needed** causes **overages**

### Markdowns
* Decrease inventory levels
* Taking **more than needed** causes **overages**
* Taking **less than needed** causes **shrink**

### Understanding UPC Automation
**UPC automation** takes markups and markdowns based on on-hand changes if there was a price change on an item in the last **50 days**, *except* for the following situations:

* Cost department corrections
* Cross reference errors with unlike counts
* CVP (Customer Value Program) corrections
* Department hand keys
* HO (Home Office) Clearance: Markup reversals only
* Optical manual adjustments

UPC automation markups and markdowns will show as **GSS_AUTO** or **UpcAuto** on the Detail Departmental Markdown Report.

If the correction *meets the criteria above* (i.e., should NOT have been automated), you will need to complete the **Miscellaneous MUMD Form in WAVE** to correct the price change.