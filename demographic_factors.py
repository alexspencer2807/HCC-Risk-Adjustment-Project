import pandas as pd
import ast
from datetime import datetime

def load_table_1(file_path):
    df = pd.read_excel(file_path, sheet_name=0, header=0)
    df.columns = ['Variable', 'Description Label', 'Community, NonDual, Aged', 'Community, NonDual, Disabled',
                  'Community, FBDual, Aged', 'Community, FBDual, Disabled', 'Community, PBDual, Aged',
                  'Community, PBDual, Disabled', 'Institutional']
    return df

def load_table_2(file_path):
    df = pd.read_excel(file_path, usecols=['MemberID', 'DOB', 'Gender', 'Medicaid Dual Status', 'OREC', 'LTI', 'RAFT Code', 'Default Factor Code', 'Medicaid', 'Frailty Indicator', 'Medicaid Add on Factor'])
    return df

def standardize_dob(date_str):
    if pd.isnull(date_str):
        return pd.NaT
    if isinstance(date_str, datetime):
        return date_str
    try:
        return datetime.strptime(date_str.replace('/', '-'), '%d-%m-%Y')
    except ValueError:
        return pd.NaT

def calculate_age(dob):
    today = datetime.today()
    return today.year - dob.year - ((today.month < dob.month) | ((today.month == dob.month) & (today.day < dob.day)))

def map_patient_data(LTI, medicaid_dual_status, OREC, Age, Gender):
    age_groups = {
        (0, 34): "0-34 Years",
        (35, 44): "35-44 Years",
        (45, 54): "45-54 Years",
        (55, 59): "55-59 Years",
        (60, 64): "60-64 Years",
        (65, 69): "65-69 Years",
        (70, 74): "70-74 Years",
        (75, 79): "75-79 Years",
        (80, 84): "80-84 Years",
        (85, 89): "85-89 Years",
        (90, 94): "90-94 Years",
        (95, float('inf')): "95 Years or Over"
    }
    def categorize_age(age):
        for age_range, label in age_groups.items():
            if age_range[0] <= age <= age_range[1]:
                return label
        return "None of the Above"
    
    def categorize_gender(gender):
        if gender == 'F':
            return "Female"
        elif gender == 'M':
            return "Male"
        return "None of the Above"
    
    age_category = categorize_age(Age)
    gender_category = categorize_gender(Gender)
    
    if LTI == 'Y':
        patient_category = f"Institutional, {age_category}, {gender_category}"
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
        
        patient_category += f", {age_category}, {gender_category}"
    return patient_category

def extract_target_value(member_id, patient_category, df):
    parts = patient_category.split(', ')
    if len(parts) < 3:
        print(f"Invalid patient category format for MemberID {member_id}: {patient_category}")
        return None
    
    community_type = parts[0]
    dual_status = parts[1] if len(parts) > 2 else None
    age_category = parts[-2]
    gender = parts[-1]
    
    if gender not in df['Variable'].values:
        print(f"Gender not found in table 1 for MemberID {member_id}: {gender}")
        return None
    
    gender_section_start = df[df['Variable'] == gender].index[0]
    next_gender_index = df[df['Variable'].shift(-1) == ('Male' if gender == 'Female' else 'Female')].index
    gender_section_end = next_gender_index[0] if not next_gender_index.empty else len(df)
    
    gender_section = df.iloc[gender_section_start:gender_section_end]
    
    if age_category not in gender_section['Variable'].values:
        print(f"Age category not found in gender section for MemberID {member_id}: {age_category}")
        return None
    
    age_row = gender_section[gender_section['Variable'] == age_category]
    
    if not age_row.empty:
        if 'Institutional' in patient_category:
            return age_row['Institutional'].values[0]
        elif 'PBDual' in patient_category:
            if 'Aged' in patient_category:
                return age_row['Community, PBDual, Aged'].values[0]
            else:
                return age_row['Community, PBDual, Disabled'].values[0]
        elif 'FBDual' in patient_category:
            if 'Aged' in patient_category:
                return age_row['Community, FBDual, Aged'].values[0]
            else:
                return age_row['Community, FBDual, Disabled'].values[0]
        elif 'NonDual' in patient_category:
            if 'Aged' in patient_category:
                return age_row['Community, NonDual, Aged'].values[0]
            else:
                return age_row['Community, NonDual, Disabled'].values[0]
    return None

def process_code_1(table_1_path, table_2_path, output_path):
    df_table_1 = load_table_1(table_1_path)
    df_table_2 = load_table_2(table_2_path)
    
    print("Table 1 DataFrame:")
    print(df_table_1.head())
    
    df_table_2['DOB'] = df_table_2['DOB'].apply(standardize_dob)
    df_table_2['Age'] = df_table_2['DOB'].apply(calculate_age)
    df_table_2['Patient Category'] = df_table_2.apply(lambda x: map_patient_data(x['LTI'], x['Medicaid Dual Status'], x['OREC'], x['Age'], x['Gender']), axis=1)
    df_table_2['Target Value'] = df_table_2.apply(lambda x: extract_target_value(x['MemberID'], x['Patient Category'], df_table_1), axis=1)
    
    print("Table 2 DataFrame with Calculations:")
    print(df_table_2.head())
    
    df_table_2.to_excel(output_path, index=False)
    print(f"Data has been saved to {output_path}")


def main():
    # Define file paths
    table_1_path = 'C:/Users/Spencerdm/OneDrive/Documents/ADT Project/Rate Announcement 2024.xlsx'
    table_2_path = 'C:/Users/Spencerdm/Downloads/For HCC (1).xlsx'
    output_path = 'C:/Users/Spencerdm/Downloads/output files/processed_output.xlsx'
    
    # Call the processing function
    process_code_1(table_1_path, table_2_path, output_path)

if __name__ == "__main__":
    main()
