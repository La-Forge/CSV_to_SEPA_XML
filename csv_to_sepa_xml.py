import csv
import xml.etree.ElementTree as ET
from datetime import datetime
import re
import sys

# List of SEPA countries
SEPA_COUNTRIES = {
    "AT", "BE", "BG", "CH", "CY", "CZ", "DE", "DK", "EE", "ES", "FI", "FR", "GB", "GI", "GR", "HR", "HU", "IE", "IS",
    "IT", "LI", "LT", "LU", "LV", "MC", "MT", "NL", "NO", "PL", "PT", "RO", "SE", "SI", "SK", "SM", "VA"
}

# Function to clean IBAN (remove spaces)
def clean_iban(iban):
    return re.sub(r"\s+", "", iban)

# Function to read CSV file
def read_csv(file_path):
    transactions = []
    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row["iban"] = clean_iban(row["iban"])  # Clean IBAN
                row["amount"] = float(row["amount"])  # Convert amount to float
                transactions.append(row)
    except FileNotFoundError:
        print(f"Error: The file {file_path} does not exist.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)

    return transactions

# Function to generate SEPA XML file
def generate_sepa_xml(transactions, output_file):
    # Validate IBANs
    for row in transactions:
        iban_country = row["iban"][:2]
        if iban_country not in SEPA_COUNTRIES:
            print(f"Error: IBAN {row['iban']} ({row['beneficiary_name']}) is not in the SEPA zone.")
            sys.exit(1)

    # Create SEPA XML root element
    ns = "urn:iso:std:iso:20022:tech:xsd:pain.001.001.03"
    ET.register_namespace('', ns)
    root = ET.Element("{urn:iso:std:iso:20022:tech:xsd:pain.001.001.03}Document")
    cstmrCdtTrfInitn = ET.SubElement(root, "{urn:iso:std:iso:20022:tech:xsd:pain.001.001.03}CstmrCdtTrfInitn")

    # Payment information
    grpHdr = ET.SubElement(cstmrCdtTrfInitn, "GrpHdr")
    ET.SubElement(grpHdr, "MsgId").text = f"SEPA-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    ET.SubElement(grpHdr, "CreDtTm").text = datetime.now().isoformat()
    ET.SubElement(grpHdr, "NbOfTxs").text = str(len(transactions))
    ET.SubElement(grpHdr, "CtrlSum").text = str(sum(row["amount"] for row in transactions))

    # Initiator
    initgPty = ET.SubElement(grpHdr, "InitgPty")
    ET.SubElement(initgPty, "Nm").text = "La Forge"

    # Payment details
    pmtInf = ET.SubElement(cstmrCdtTrfInitn, "PmtInf")
    ET.SubElement(pmtInf, "PmtInfId").text = "BatchTransfer"
    ET.SubElement(pmtInf, "PmtMtd").text = "TRF"
    ET.SubElement(pmtInf, "NbOfTxs").text = str(len(transactions))
    ET.SubElement(pmtInf, "CtrlSum").text = str(sum(row["amount"] for row in transactions))

    # Payment type information
    pmtTpInf = ET.SubElement(pmtInf, "PmtTpInf")
    svcLvl = ET.SubElement(pmtTpInf, "SvcLvl")
    ET.SubElement(svcLvl, "Cd").text = "SEPA"

    # Requested execution date
    ET.SubElement(pmtInf, "ReqdExctnDt").text = datetime.now().strftime("%Y-%m-%d")

    # Debtor details
    dbtr = ET.SubElement(pmtInf, "Dbtr")
    ET.SubElement(dbtr, "Nm").text = "La Forge"

    dbtrAcct = ET.SubElement(pmtInf, "DbtrAcct")
    id_element = ET.SubElement(dbtrAcct, "Id")
    ET.SubElement(id_element, "IBAN").text = "FRXXXXXXXXXXXXXXXXXXXX"

    dbtrAgt = ET.SubElement(pmtInf, "DbtrAgt")
    finInstnId = ET.SubElement(dbtrAgt, "FinInstnId")
    ET.SubElement(finInstnId, "BIC").text = "BNPAFRPPXXX"

    # Individual transactions
    for row in transactions:
        cdtTrfTxInf = ET.SubElement(pmtInf, "CdtTrfTxInf")
        pmtId = ET.SubElement(cdtTrfTxInf, "PmtId")
        ET.SubElement(pmtId, "EndToEndId").text = row["reference"]

        amt = ET.SubElement(cdtTrfTxInf, "Amt")
        instdAmt = ET.SubElement(amt, "InstdAmt", Ccy=row["currency"])
        instdAmt.text = f"{row['amount']:.2f}"

        cdtr = ET.SubElement(cdtTrfTxInf, "Cdtr")
        ET.SubElement(cdtr, "Nm").text = row["beneficiary_name"]

        cdtrAcct = ET.SubElement(cdtTrfTxInf, "CdtrAcct")
        id_element = ET.SubElement(cdtrAcct, "Id")
        ET.SubElement(id_element, "IBAN").text = row["iban"]

        cdtrAgt = ET.SubElement(cdtTrfTxInf, "CdtrAgt")
        finInstnId = ET.SubElement(cdtrAgt, "FinInstnId")
        ET.SubElement(finInstnId, "BIC").text = row.get("bic", "N/A")

        rmtInf = ET.SubElement(cdtTrfTxInf, "RmtInf")
        ET.SubElement(rmtInf, "Ustrd").text = row.get("remittance_info", "Payment")

    # Save the XML file
    tree = ET.ElementTree(root)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    print(f"✅ SEPA XML file successfully generated: {output_file}")

# Main function
def main():
    if len(sys.argv) != 3:
        print("Usage: python csv_to_sepa_xml.py <path_to_CSV_file> <output_XML_file>")
        sys.exit(1)

    csv_file_path = sys.argv[1]
    xml_output_file = sys.argv[2]

    transactions = read_csv(csv_file_path)
    generate_sepa_xml(transactions, xml_output_file)

if __name__ == "__main__":
    main()
