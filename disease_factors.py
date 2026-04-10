import pandas as pd
import ast
import datetime

def load_table_1(file_path):
    df = pd.read_excel(file_path, sheet_name=0, header=1)
    df.columns = ['Variable', 'Description Label', 'Community, NonDual, Aged', 'Community, NonDual, Disabled',
                  'Community, FBDual, Aged', 'Community, FBDual, Disabled', 'Community, PBDual, Aged',
                  'Community, PBDual, Disabled', 'Institutional']
    return df

def load_table_2(file_path):
    df = pd.read_excel(file_path, usecols=['MemberID', 'LTI', 'Medicaid Dual Status', 'OREC', 'Diag_Code'])
    return df

def preprocess_icd_codes(icd_code_str):
    try:
        icd_codes = ast.literal_eval(icd_code_str)
        if isinstance(icd_codes, list):
            return icd_codes
        else:
            return []
    except (ValueError, SyntaxError):
        return []

def extract_hcc_codes(icd_code_str, icd_to_hcc_dict):
    icd_codes = preprocess_icd_codes(icd_code_str)
    hcc_codes = [f"HCC{icd_to_hcc_dict.get(icd_code)}" for icd_code in icd_codes if icd_code in icd_to_hcc_dict]
    return hcc_codes

def map_patient_data(LTI, medicaid_dual_status, OREC):
    if LTI == 'Y':
        patient_category = "Institutional"
    else:
        patient_category = "Community"
        if medicaid_dual_status in [1, 3, 5, 6]:
            patient_category += ", PBDual"
        elif medicaid_dual_status in [2, 4, 8]:
            patient_category += ", FBDual"
        elif medicaid_dual_status == 9:
            patient_category += ", NonDual"
        else:
            patient_category += ", Unknown"
        if OREC == 0:
            patient_category += ", Aged"
        elif OREC == 1:
            patient_category += ", Disabled"
        else:
            patient_category += ", None of the Above"
    return patient_category

def extract_target_values(hcc_codes, patient_category, df):
    target_value = 0
    category_mapping = {
        'Institutional': 'Institutional',
        'PBDual': 'Community, PBDual',
        'FBDual': 'Community, FBDual',
        'NonDual': 'Community, NonDual'
    }
    for hcc_code in hcc_codes:
        if hcc_code in df['Variable'].values:
            hcc_row = df[df['Variable'] == hcc_code]
            if not hcc_row.empty:
                for key, value in category_mapping.items():
                    if key in patient_category:
                        if 'Aged' in patient_category:
                            column = f"{value}, Aged"
                        elif 'Disabled' in patient_category:
                            column = f"{value}, Disabled"
                        else:
                            column = value
                        if column in hcc_row.columns:
                            target_value += hcc_row[column].values[0]
    return target_value

def process_code_2(table_1_path, table_2_path, icd_to_hcc_path, output_path):
    df_table_1 = load_table_1(table_1_path)
    print("Table 1 Columns:")
    print(df_table_1.columns)
    print("Number of Columns in Table 1:", len(df_table_1.columns))
    
    df_table_2 = load_table_2(table_2_path)
    df_icd_to_hcc = pd.read_csv(icd_to_hcc_path, header=None)
    icd_to_hcc_dict = dict(zip(df_icd_to_hcc.iloc[:, 0], df_icd_to_hcc.iloc[:, 3]))
    
    df_table_2['HCC Codes'] = df_table_2['Diag_Code'].apply(lambda x: extract_hcc_codes(x, icd_to_hcc_dict))
    df_table_2['Patient Category'] = df_table_2.apply(lambda x: map_patient_data(x['LTI'], x['Medicaid Dual Status'], x['OREC']), axis=1)
    df_table_2['Target Value'] = df_table_2.apply(lambda x: extract_target_values(x['HCC Codes'], x['Patient Category'], df_table_1), axis=1)
    df_table_2.to_excel(output_path, index=False)
    print(f"Data has been saved to {output_path}")

