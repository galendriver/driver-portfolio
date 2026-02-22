// Google Apps Script — adds live_price and total_value columns to balances sheet
// Usage: Extensions → Apps Script → paste this → Run → authorize when prompted

function addLivePriceColumns() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const lastRow = sheet.getLastRow();

  // Add headers in columns L (12) and M (13)
  sheet.getRange("L1").setValue("live_price");
  sheet.getRange("M1").setValue("total_value");

  // Header formatting
  const headerRange = sheet.getRange("L1:M1");
  headerRange.setFontWeight("bold");
  headerRange.setBackground("#d9ead3");

  for (let row = 2; row <= lastRow; row++) {
    const yfSymbol    = sheet.getRange(row, 6).getValue();  // col F: yf_symbol
    const cgId        = sheet.getRange(row, 7).getValue();  // col G: cg_id
    const manualValue = sheet.getRange(row, 8).getValue();  // col H: manual_value
    const shares      = sheet.getRange(row, 5).getValue();  // col E: shares

    let priceFormula = "";

    if (yfSymbol) {
      // Stocks: use GOOGLEFINANCE directly
      // Crypto with -USD suffix (BTC-USD, ETH-USD, WLD-USD): convert to CURRENCY: format
      if (yfSymbol.endsWith("-USD")) {
        const symbol = yfSymbol.replace("-USD", "");
        priceFormula = `=IFERROR(GOOGLEFINANCE("CURRENCY:${symbol}USD"), "")`;
      } else {
        priceFormula = `=IFERROR(GOOGLEFINANCE("${yfSymbol}", "price"), "")`;
      }
    } else if (manualValue !== "") {
      // Private equity, 401k — show manual value as price placeholder
      priceFormula = `=${manualValue}`;
    }
    // cg_id only rows (RNDR, stETH, NEAR etc.) — Python handles pricing; leave blank

    // Total value formula
    let totalFormula = "";
    if (shares !== "" && shares !== 0) {
      totalFormula = `=IF(L${row}<>"", E${row}*L${row}, "")`;
    } else if (manualValue !== "") {
      totalFormula = `=${manualValue}`;
    }

    if (priceFormula) sheet.getRange(row, 12).setFormula(priceFormula);
    if (totalFormula) sheet.getRange(row, 13).setFormula(totalFormula);
  }

  // Format columns L and M as currency
  sheet.getRange(`L2:M${lastRow}`).setNumberFormat("$#,##0.00");

  // Auto-resize columns
  sheet.autoResizeColumns(12, 2);

  SpreadsheetApp.getUi().alert("Done! live_price and total_value columns added.");
}
