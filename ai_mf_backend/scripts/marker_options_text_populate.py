import os
import sys

from django.db import connection

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ai_mf_backend.config.v1.django_settings")

import django
django.setup()

from ai_mf_backend.models.v1.database.mf_reference_table import MFMarkerOptionsText

def truncate_marker_options_text_table():
    with connection.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE mf_marker_options_text RESTART IDENTITY CASCADE;")
    print("Truncated mf_marker_options_text table and reset identity.")

def populate_marker_options_text():
    
    mapping_dict = {
        1: [
            ('Very High', 6),
            ('Moderately High', 4), ('Moderate', 3),
            ('Low to Moderate', 2), ('Low', 1), ('High', 5)
        ],
        3: [
            ('Close ended scheme', 2),
            ('Interval scheme', 3),
            ('Open ended scheme', 1)
        ],
        12: [('N', 2), ('Y', 1)],
        13: [('N', 2), ('Y', 1)],
        18: [('Y', 1), ('N', 2)],
        24: [('INR000002813', 1), ('INR000000221', 2), ('INR000004017', 3)],
        25: [
            ('Board of Trustees of IIFCL Mutual Fund (IDF)', 47),
            ('Board of Trustees, HSBC Mutual Fund', 14),
            ('Angel One Trustee Ltd.', 45),
            ('Aditya Birla Sun Life Trustee Company Private Limited', 6),
            ('360 ONE Asset Trustee Limited', 30),
            ('DSP Trustee Private Limited', 10),
            ('Deutsche Trustee Services (India) Private Limited', 48),
            ('Edelweiss Trusteeship Company Limited', 12),
            ('Franklin Templeton Trustee Services Private Limited', 15),
            ('Goldman Sachs Trustee Company (India) Private Limited', 49),
            ('Groww Trustee Limited', 39),
            ('HDFC Trustee Company Limited', 3),
            ('NJ Trustee Private Limited', 34),
            ('Axis Mutual Fund Trustee Limited', 8),
            ('Bajaj Finserv Mutual Fund Trustee Ltd.', 25),
            ('Bandhan Mutual Fund Trustee Limited', 13),
            ('Bank of India Trustee Services Private Limited', 31),
            ('Baroda BNP Paribas Trustee India Pvt. Ltd.', 21),
            ('Baroda Trustee India Private Limited', 22),
            ('Board of Trustees', 46),
            ('Zerodha Trustee Private Limited', 35),
            ('WhiteOak Capital Trustee Limited', 28),
            ('Union Trustee Company Pvt. Ltd.', 27),
            ('Unifi Mutual Fund Trustee Pvt. Ltd.', 44),
            ('UTI Trustee Company Private Limited', 7),
            ('Trust AMC Trustee Private Limited', 41),
            ('Taurus Investment Trust Company Limited', 43),
            ('Tata Trustee Company Private Limited', 11),
            ('Sundaram Trustee Company Limited', 20),
            ('Shriram Trustees Ltd.', 42),
            ('Samco Trustee Pvt. Ltd', 40),
            ('SREI Mutual Fund Trust Pvt. Ltd.', 58),
            ('SBI Mutual Fund Trustee Company Private Limited', 1),
            ('Helios Trustee Private Limited', 37),
            ('ICICI Prudential Trust Limited', 2),
            ('IDBI MF Trustee Company Ltd.', 50),
            ('IL&FS AMC Trustee Limited', 51),
            ('ING Vysya Mutual Fund', 52),
            ('ITI Mutual Fund Trustee Private Limited', 32),
            ('Invesco Trustee Company Pvt. Ltd.', 16),
            ('JM Financial Trustee Company Private Limited', 29),
            ('JPMorgan Mutual Fund India Pvt. Ltd.', 53),
            ('Kotak Mahindra Trustee Co. Limited', 5),
            ('L&T Mutual Fund Trustee Limited', 54),
            ('LIC Mutual Fund Trustee Private Limited', 23),
            ('Mahindra Manulife Trustee Private Limited', 24),
            ('Mirae Asset Trustee Company Private Limited', 9),
            ('Motilal Oswal Trustee Company Limited', 17),
            ('Quantum Trusteee Company Private Ltd.', 38),
            ('Navi Trustee Limited', 33),
            ('Nippon Life India Trustee Limited', 4),
            ('Not Available', 55),
            ('Old Bridge Mutual Fund Trustee Private Limited', 41),
            ('PGIM India Trustees Private Limited', 26),
            ('PPFAS Trustee Company Pvt. Ltd.', 16),
            ('PineBridge Investments Trustee Company (India) Private Limited', 56),
            ('Principal Trustee Company Private Limited', 57),
            ('Quant Capital Trustee Limited', 18)
        ],
        26: [
            ('Orbis Financial Corporation Ltd.', 13),
            ('SBI-SG Global Securities Services Pvt. Ltd.', 6),
            ('Standard Chartered Bank', 11),
            ('Stock Holding Corporation of India Limited.', 12),
            ('The Bank of Nova Scotia', 10),
            ('DBS Bank Limited', 7),
            ('J P Morgan Chase Bank', 1),
            ('ICICI Bank Limited', 3),
            ('HSBC Limited', 4),
            ('HDFC Bank Limited', 2),
            ('Deutsche Bank A.G.', 9),
            ('Citibank N.A', 5),
            ('Axis Bank Ltd.', 8)
        ],
        27: [('Y', 1), ('N', 2)],
        29: [('Commodity', 5), ('Hybrid', 3), ('Other', 4), ('Debt', 2), ('Equity', 1)],
        31: [
            ('Index - Nifty Next 50', 27),
            ('Index - Sensex', 26),
            ('Index Funds - Other', 28),
            ('Infrastructure', 18),
            ('Interval Funds - Half Yearly', 32),
            ('MNC', 19),
            ('Interval Funds - Monthly', 34),
            ('Technology', 11),
            ('Small cap Fund', 9),
            ('Silver', 30),
            ('Short & Mid Term', 22),
            ('Service Industry', 17),
            ('Pharma & Health Care', 13),
            ('Multi Cap Fund', 7),
            ('Mid Cap Fund', 8),
            ('Media & Entertainment', 16),
            ('Interval Funds - Quarterly', 33),
            ('Interval Funds - Yearly', 31),
            ('Large & Mid Cap', 5),
            ('Large Cap Fund', 6),
            ('Auto', 14),
            ('Banks & Financial Services', 10),
            ('Consumption', 12),
            ('Debt', 34),
            ('Debt - Infrastructure', 20),
            ('Debt Oriented', 2),
            ('Energy & Power', 15),
            ('Equity Oriented', 1),
            ('Flexi Cap Fund', 4),
            ('Gilt Fund with 10 year constant duration', 22),
            ('Global', 20),
            ('Gold', 29),
            ('Hybrid', 3),
            ('Index', 24),
            ('Index - Nifty', 25)
        ]
    }

    truncate_marker_options_text_table()

    count = 0
    for marker_id, options in mapping_dict.items():
        for option_text, position in options:
            MFMarkerOptionsText.objects.create(
                marker_id_id=marker_id,
                option=option_text,
                position=position                )
            count += 1

    print(f"Inserted {count} records into MFMarkerOptionsText.")

if __name__ == "__main__":
    populate_marker_options_text()