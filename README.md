# 📌 CSV to SEPA XML Converter

This Python script, `csv_to_sepa_xml.py`, converts a **CSV file** containing payment transactions into a **SEPA-compliant XML file** (`pain.001.001.03` format).  

## 🚀 Features
✅ Reads a **CSV file** containing payment details.  
✅ **Validates IBANs** to ensure they belong to the **SEPA zone**.  
✅ **Cleans IBANs** (removes spaces and ensures proper format).  
✅ **Generates a SEPA XML file** ready for bank transactions.  
✅ **Handles errors** such as missing files, invalid formats, and non-SEPA IBANs.  


## 📌 Requirements
### 🔧 Prerequisites
- Python **3.x**  
- No external dependencies (uses only built-in Python libraries).


## 📌 Usage
### Prepare a CSV file (`transfers.csv`) e.g
Ensure your CSV file is formatted as follows:

```csv
Creditor_Name,Creditor_IBAN,Creditor_BIC,Remittance_Info,Payment_Amount
Jane Doe,DE43100500000920018963,,10.00,EUR,Test Transfer,25.5
```

### Run the Script
python csv_to_sepa_xml.py transfers.csv

### Ouput
sepa_transfer.xml