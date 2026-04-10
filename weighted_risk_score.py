import pandas as pd

def load_weighted_risk_scores(file_path):
    """Load the weighted risk scores from an Excel file."""
    df = pd.read_excel(file_path)
    df['Weighted Risk Score'] = pd.to_numeric(df['Weighted Risk Score'], errors='coerce').fillna(0)
    return df

def combine_weighted_risk_scores(file_path_2020, file_path_2024, output_path):
    # Load the weighted risk scores for both years
    df_2020 = load_weighted_risk_scores(file_path_2020)
    df_2024 = load_weighted_risk_scores(file_path_2024)
    
    # Merge the dataframes on 'MemberID'
    df_combined = pd.merge(df_2020[['MemberID', 'Weighted Risk Score']], 
                           df_2024[['MemberID', 'Weighted Risk Score']], 
                           on='MemberID', how='outer', suffixes=('_2020', '_2024'))
    
    # Fill NaN values with 0
    df_combined['Weighted Risk Score_2020'] = df_combined['Weighted Risk Score_2020'].fillna(0)
    df_combined['Weighted Risk Score_2024'] = df_combined['Weighted Risk Score_2024'].fillna(0)
    
    # Calculate the total weighted risk score for each patient
    df_combined['Total Weighted Risk Score'] = df_combined['Weighted Risk Score_2020'] + df_combined['Weighted Risk Score_2024']
    
    # Display the combined data
    print("\nCombined Weighted Risk Scores:")
    print(df_combined[['MemberID', 'Weighted Risk Score_2020', 'Weighted Risk Score_2024', 'Total Weighted Risk Score']])
    
    # Save the combined data to an Excel file
    df_combined.to_excel(output_path, index=False)
    print(f"Combined weighted risk scores have been saved to {output_path}")

def main():
    # File paths for weighted risk scores
    file_path_2020 = 'C:/Users/Spencerdm/Downloads/Comprehensive_Risk_Scores_with_Patient_Data_2020.xlsx'
    file_path_2024 = 'C:/Users/Spencerdm/Downloads/Comprehensive_Risk_Scores_with_Patient_Data_2024.xlsx'
    output_path = 'C:/Users/Spencerdm/Downloads/Combined_Weighted_Risk_Scores_2020_2024.xlsx'
    
    # Combine the weighted risk scores and save to file
    combine_weighted_risk_scores(file_path_2020, file_path_2024, output_path)

if __name__ == "__main__":
    main()
