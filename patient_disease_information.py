import pandas as pd
import os
from disease_factors import process_code_2  # Import the function from code 2
from demographic_factors import process_code_1  # Import the function from code 1

def calculate_adjusted_risk_score(raw_risk_score, normalization_factor, ma_coding_pattern=5.9 / 100):
    """
    Calculate the adjusted risk score based on the raw risk score, normalization factor, and MA coding pattern.

    Parameters:
    - raw_risk_score: The raw risk score to be adjusted.
    - normalization_factor: The factor used to normalize the raw risk score.
    - ma_coding_pattern: The MA coding pattern percentage as a decimal.

    Returns:
    - Adjusted risk score.
    """
    return (raw_risk_score / normalization_factor) * (1 - ma_coding_pattern)

def display_and_sum_values(file_path_1, file_path_2, output_file_path):
    # Load target value files
    df1 = pd.read_excel(file_path_1)
    df2 = pd.read_excel(file_path_2)
    
    # Ensure 'Target Value' columns are numeric
    df1['Target Value'] = pd.to_numeric(df1['Target Value'], errors='coerce').fillna(0)
    df2['Target Value'] = pd.to_numeric(df2['Target Value'], errors='coerce').fillna(0)
    
    # Merge the dataframes on 'MemberID'
    df_combined = pd.merge(df1[['MemberID', 'Target Value']], df2[['MemberID', 'Target Value']], on='MemberID', how='outer', suffixes=('_2020', '_2024'))
    
    # Fill NaN values with 0
    df_combined['Target Value_2020'] = df_combined['Target Value_2020'].fillna(0)
    df_combined['Target Value_2024'] = df_combined['Target Value_2024'].fillna(0)
    
    # Calculate the raw risk scores for 2020 and 2024
    df_combined['Raw Risk Score_2020'] = df_combined['Target Value_2020']
    df_combined['Raw Risk Score_2024'] = df_combined['Target Value_2024']
    
    # Calculate the adjusted risk scores for 2020 and 2024
    df_combined['Adjusted Risk Score_2020'] = df_combined['Raw Risk Score_2020'].apply(lambda x: calculate_adjusted_risk_score(x, normalization_factor=1.069))
    df_combined['Adjusted Risk Score_2024'] = df_combined['Raw Risk Score_2024'].apply(lambda x: calculate_adjusted_risk_score(x, normalization_factor=1.015))
    
    # Calculate the combined adjusted risk score with 30% weight from 2020 and 70% weight from 2024
    df_combined['Combined Adjusted Risk Score'] = (df_combined['Adjusted Risk Score_2020'] * 0.3) + (df_combined['Adjusted Risk Score_2024'] * 0.7)
    
    # Load HCC codes and patient categories from the output of process_code_2 (assuming they are included)
    df_hcc_codes = pd.read_excel(file_path_2, usecols=['MemberID', 'HCC Codes', 'Patient Category'])  # Adjust columns as needed
    
    # Assuming age and patient data are included in the demographic file
    df_patient_data = df1[['MemberID', 'Age']]  # Replace with actual columns if needed
    
    # Merge all dataframes
    df_combined = pd.merge(df_combined, df_patient_data, on='MemberID', how='left')
    df_combined = pd.merge(df_combined, df_hcc_codes, on='MemberID', how='left')
    
    # Display the relevant data in the terminal
    print("\nComprehensive Risk Scores and Patient Data:")
    print(df_combined[['MemberID', 'Age', 'HCC Codes', 'Patient Category', 'Raw Risk Score_2020', 'Raw Risk Score_2024', 'Adjusted Risk Score_2020', 'Adjusted Risk Score_2024', 'Combined Adjusted Risk Score']])
    
    # Save the combined DataFrame to an Excel file
    df_combined.to_excel(output_file_path, index=False)
    
    print(f"Results have been saved to {output_file_path}")

def main():
    # Paths for code 1
    table_1_path_code_1 = 'C:/Users/Spencerdm/OneDrive/Documents/ADT Project/Rate Announcement 2020.xlsx'
    table_2_path_code_1 = 'C:/Users/Spencerdm/Downloads/For HCC (1).xlsx'
    output_path_code_1 = 'C:/Users/Spencerdm/Downloads/Patient_Data_Target_Values.xlsx'
    
    # Paths for code 2
    table_1_path_code_2 = 'C:/Users/Spencerdm/OneDrive/Documents/ADT Project/Rate Announcement 2024.xlsx'
    table_2_path_code_2 = 'C:/Users/Spencerdm/Downloads/For HCC (1).xlsx'
    icd_to_hcc_path = "C:/Users/Spencerdm/Downloads/2024 Initial ICD-10-CM Mappings/2024 Initial ICD-10-CM Mappings.csv"
    output_path_code_2 = 'C:/Users/Spencerdm/Downloads/hcc_code_target_values.xlsx'
    
    # Check if files exist
    if not os.path.isfile(table_1_path_code_1):
        print(f"File not found: {table_1_path_code_1}")
        return
    if not os.path.isfile(table_2_path_code_1):
        print(f"File not found: {table_2_path_code_1}")
        return
    if not os.path.isfile(table_1_path_code_2):
        print(f"File not found: {table_1_path_code_2}")
        return
    if not os.path.isfile(table_2_path_code_2):
        print(f"File not found: {table_2_path_code_2}")
        return
    if not os.path.isfile(icd_to_hcc_path):
        print(f"File not found: {icd_to_hcc_path}")
        return
    
    # Process the files
    process_code_1(table_1_path_code_1, table_2_path_code_1, output_path_code_1)
    process_code_2(table_1_path_code_2, table_2_path_code_2, icd_to_hcc_path, output_path_code_2)

    # Define output file path
    final_output_path = 'C:/Users/Spencerdm/Downloads/Comprehensive_Risk_Scores.xlsx'
    
    # Display and sum target values
    display_and_sum_values(output_path_code_1, output_path_code_2, final_output_path)

if __name__ == "__main__":
    main()
