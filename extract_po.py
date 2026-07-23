import pdfplumber
import pandas as pd
import os
import re
from datetime import datetime

# =====================================================
# PATHS
# =====================================================

base_path = r"D:\PFPPL\Reliance PO"

pdf_folder = os.path.join(base_path, "PO")

master_file = os.path.join(base_path, "Master.xlsx")

output_file = os.path.join(
    base_path,
    "New_Nav_Output.csv"
)

# =====================================================
# READ MASTER
# =====================================================

customer_df = pd.read_excel(
    master_file,
    sheet_name="customer_master"
)

product_df = pd.read_excel(
    master_file,
    sheet_name="product_master"
)

customer_df["DC Code"] = (
    customer_df["DC Code"]
    .astype(str)
    .str.strip()
)

customer_df["Customer NO."] = (
    customer_df["Customer NO."]
    .astype(str)
    .str.strip()
)

product_df["EAN"] = (
    product_df["EAN"]
    .astype(str)
    .str.strip()
)

product_df["Item No."] = (
    product_df["Item No."]
    .astype(str)
    .str.strip()
)

customer_lookup = dict(
    zip(
        customer_df["DC Code"],
        customer_df["Customer NO."]
    )
)

product_lookup = dict(
    zip(
        product_df["EAN"],
        product_df["Item No."]
    )
)

# =====================================================
# TODAY DATE
# =====================================================

today_date = datetime.today().strftime(
    "%d-%m-%Y"
)

# =====================================================
# EXTRACT PDF DATA
# =====================================================

all_rows = []

for file in os.listdir(pdf_folder):

    if not file.lower().endswith(".pdf"):
        continue

    print(f"Processing : {file}")

    pdf_path = os.path.join(
        pdf_folder,
        file
    )

    with pdfplumber.open(pdf_path) as pdf:

        site_id = ""
        po_number = ""

        # -----------------------------------------
        # PAGE 1 HEADER DETAILS
        # -----------------------------------------

        try:

            first_page_text = (
                pdf.pages[0]
                .extract_text()
            )

            if first_page_text:

                site_match = re.search(
                    r"Site\s*:\s*([A-Z0-9]+)",
                    first_page_text,
                    re.IGNORECASE
                )

                if site_match:
                    site_id = (
                        site_match.group(1)
                        .strip()
                    )

                po_match = re.search(
                    r"PO\s*NO\.\s*:\s*(\d+)",
                    first_page_text,
                    re.IGNORECASE
                )

                if po_match:
                    po_number = (
                        po_match.group(1)
                        .strip()
                    )

        except Exception as e:

            print(
                f"Header Error : {e}"
            )

        # -----------------------------------------
        # TABLE EXTRACTION
        # -----------------------------------------

        table_started = False

        for page in pdf.pages:

            tables = page.extract_tables()

            for table in tables:

                if not table:
                    continue

                for row in table:

                    if not row:
                        continue

                    row_text = " ".join(
                        str(x)
                        for x in row
                        if x
                    )

                    if (
                        "Article No"
                        in row_text
                    ):
                        table_started = True
                        continue

                    if (
                        "Grand Total of Qty"
                        in row_text
                    ):
                        table_started = False
                        break

                    if not table_started:
                        continue

                    try:

                        if (
                            row[0]
                            and
                            str(row[0])
                            .strip()
                            .isdigit()
                        ):

                            qty = None

                            try:

                                qty = int(
                                    float(
                                        str(
                                            row[4]
                                        )
                                        .split()[0]
                                    )
                                )

                            except:
                                pass

                            ean = (
                                str(row[2])
                                .strip()
                            )

                            customer_no = (
                                customer_lookup.get(
                                    site_id,
                                    ""
                                )
                            )

                            item_no = (
                                product_lookup.get(
                                    ean,
                                    ""
                                )
                            )

                            all_rows.append({

                                "PO Number":
                                    po_number,

                                "Customer No":
                                    customer_no,

                                "Item No":
                                    item_no,

                                "Quantity":
                                    qty

                            })

                    except Exception as e:

                        print(
                            f"Row Error : {e}"
                        )

# =====================================================
# NAV FILE
# =====================================================

nav_rows = []

for po_number, group in pd.DataFrame(
    all_rows
).groupby("PO Number"):

    line_no = 10000

    for _, row in group.iterrows():

        nav_rows.append({

            "Sell-to Customer No.":
                row["Customer No"],

            "Location Code":
                "CW01",

            "OrderDate":
                today_date,

            "Code":
                row["Item No"],

            "UOM":
                "CAR",

            "Case QTY":
                row["Quantity"],

            "Line No.":
                line_no,

            "External Document no.":
                po_number

        })

        line_no += 10000

# =====================================================
# EXPORT
# =====================================================

nav_df = pd.DataFrame(nav_rows)

nav_df.to_csv(
    output_file,
    index=False,
    encoding="utf-8-sig"
)

print("\nDone")
print(output_file)