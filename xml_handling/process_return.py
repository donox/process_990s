import os
from datetime import datetime
import psycopg2
import xml.etree.ElementTree as ET


def extract_returns(root, file_path):
    """
    Extract data for the `returns` table from the XML file.
    """
    ein = root.findtext('.ReturnHeader/Filer/EIN', default=None)
    return_file = file_path.split('/')[-1].replace('.xml', '')  # Use file name as return ID
    return_type = root.findtext('./ReturnHeader/ReturnTypeCd', default="")
    tax_period_end_raw = root.findtext('./ReturnHeader/TaxPeriodEndDt', default="")
    tax_period_end = None
    tax_year = None
    if tax_period_end_raw:
        try:
            tax_period_end = datetime.strptime(tax_period_end_raw, "%Y-%m-%d").date()
            tax_year = tax_period_end.year

        except ValueError as e:
            print(f"Invalid date format for TaxPeriodEndDt: {tax_period_end_raw}. Error: {e}")

    tax_period_start = None  # Add logic to extract if available
    organization501c3_exempt_pf = root.findtext('./ReturnData/IRS990PF/Organization501c3ExemptPFInd', default=False)
    if organization501c3_exempt_pf:
        organization501c3_exempt_pf = True
    fmv_assets_eoy = root.findtext('./ReturnData/IRS990PF/FMVAssetsEOYAmt', default=None)
    method_of_accounting_cash = root.findtext('./ReturnData/IRS990PF/MethodOfAccountingCashInd', default=False)
    if method_of_accounting_cash:
        method_of_accounting_cash = True

    return {
        'ein': ein,
        'return_file': return_file,
        'tax_year': tax_year,
        'return_type': return_type,
        'tax_period_start': tax_period_start,
        'tax_period_end': tax_period_end,
        'organization501c3_exempt_pf': organization501c3_exempt_pf,
        'fmv_assets_eoy': fmv_assets_eoy,
        'method_of_accounting_cash': method_of_accounting_cash,
        'filename': file_path,
    }


def insert_returns(mg_trans, data):
    """
    Insert data into the `returns` table and return the generated ID.
    """
    try:
        query = """
            INSERT INTO return (ReturnFile, EIN, TaxYear, ReturnType, TaxPeriodBegin, TaxPeriodEnd, 
            Organization501c3ExemptPF, FMVAssetsEOY, MethodOfAccountingCash, FileName )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
            ON CONFLICT (EIN, TaxYear) 
            DO UPDATE SET
               ReturnFile = EXCLUDED.ReturnFile,
               ReturnType = EXCLUDED.ReturnType,
               TaxPeriodBegin = EXCLUDED.TaxPeriodBegin,
               TaxPeriodEnd = EXCLUDED.TaxPeriodEnd,
               Organization501c3ExemptPF = EXCLUDED.Organization501c3ExemptPF,
               FMVAssetsEOY = EXCLUDED.FMVAssetsEOY,
               MethodOfAccountingCash = EXCLUDED.MethodOfAccountingCash,
               FileName = EXCLUDED.FileName
            RETURNING returnid;
        """
        params = (
            data['return_file'], data['ein'], data['tax_year'], data['return_type'], data['tax_period_start'],
            data['tax_period_end'], data['organization501c3_exempt_pf'], data['fmv_assets_eoy'],
            data['method_of_accounting_cash'], data['filename'])
        return_id = mg_trans.execute(query, params=params)
        return return_id[0]

    except Exception as e:
        print(f"Error in insert_returns: {e}")
        raise e
