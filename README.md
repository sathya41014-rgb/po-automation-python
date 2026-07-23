# PO Automation Python

A Python-based automation tool that extracts Purchase Order (PO) data from PDF files and converts it into ERP-ready CSV files.

## Features

- Extracts PO Number
- Extracts Vendor Details
- Extracts Delivery Address
- Extracts Site Code
- Extracts Item Code
- Extracts EAN Code
- Extracts Product Description
- Extracts Quantity and UOM
- Generates ERP-ready CSV output
- Supports multi-page Purchase Orders

## Technologies Used

- Python
- pdfplumber
- pandas
- Regular Expressions (re)

## Project Structure

```
po-automation-python/
│── extract_po.py
│── requirements.txt
│── sample/
│   ├── Sample_Reliance_Style_PO.pdf
│   └── sample_output.csv
```

## How to Run

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the script:

```bash
python extract_po.py
```

## Sample Input

A fictional Purchase Order PDF is included in the `sample` folder for demonstration purposes.

## Sample Output

The script generates an ERP-ready CSV containing:

- PO Number
- Site
- Item Code
- EAN
- Description
- Quantity
- UOM

## License

MIT License
