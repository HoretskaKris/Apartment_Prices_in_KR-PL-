import pandas as pd
import os
import logging
from datetime import datetime
from typing import List, Dict
import numpy as np

pd.set_option('future.no_silent_downcasting', True)

log_directory: str = r'.\logs'
os.makedirs(log_directory, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_directory, 'normalize_and_clean_data.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

def load_all_data(directory_path: str) -> pd.DataFrame:
    '''Loading data from all files in the specified folder and combining them into one dataset'''
    logging.info('Loading data from all files in folder %s', directory_path)
    dataframes: List[pd.DataFrame] = []

    for file in os.listdir(directory_path):
        if file.endswith('.csv'):
            file_path: str = os.path.join(directory_path, file)
            try:
                df: pd.DataFrame = pd.read_csv(file_path)
                dataframes.append(df)
                logging.info('File %s successfully loaded', file)
            except Exception as e:
                logging.error('Failed to load file %s: %s', file, e)

    combined_df: pd.DataFrame = pd.concat(dataframes, ignore_index=True)
    logging.info('Total of %d rows loaded', len(combined_df))
    return combined_df

def remove_non_unique_ids(df: pd.DataFrame) -> pd.DataFrame:
    '''Removing non-unique IDs'''
    logging.info('Removing non-unique IDs')
    if 'id' in df.columns:
        original_length: int = len(df)
        df = df.drop_duplicates(subset='id', keep='first')
        logging.info('%d duplicates removed', original_length - len(df))
    return df

def get_price_stats_for_city(df: pd.DataFrame, city: str) -> Dict[str, Dict[str, float]]:
    '''Getting minimum and maximum prices for 'premium' and 'low' categories for the specified city'''
    city_data = df[df['city'] == city]
    stats = {}
    for condition in ['premium', 'low']:
        condition_data = city_data[city_data['condition'] == condition]
        if not condition_data.empty:
            stats[condition] = {
                'min': condition_data['price'].min(),
                'max': condition_data['price'].max()
            }
    return stats

def fill_condition(df: pd.DataFrame) -> pd.DataFrame:
    '''Filling missing values in the 'condition' column based on prices and city'''
    logging.info('Filling missing values in the condition column')
    if 'condition' in df.columns and 'city' in df.columns and 'price' in df.columns:
        city_price_stats = {}
        
        for index, row in df.iterrows():
            if pd.isna(row['condition']):
                city = row['city']
                if city not in city_price_stats:
                    city_price_stats[city] = get_price_stats_for_city(df, city)

                premium_stats = city_price_stats[city].get('premium', {})
                low_stats = city_price_stats[city].get('low', {})

                if 'min' in premium_stats and premium_stats['min'] <= row['price'] <= premium_stats['max']:
                    df.at[index, 'condition'] = 'premium'
                elif 'min' in low_stats and low_stats['min'] <= row['price'] <= low_stats['max']:
                    df.at[index, 'condition'] = 'low'
                else:
                    df.at[index, 'condition'] = 'medium'
        logging.info('Missing condition values filled')
    return df

def fill_missing_building_material(df: pd.DataFrame) -> pd.DataFrame:
    '''Filling missing values in the buildingMaterial column'''
    logging.info('Filling missing values in the buildingMaterial column')
    mode_value: str = df['buildingMaterial'].mode()[0]
    df['buildingMaterial'] = df['buildingMaterial'].fillna(mode_value)
    logging.info('Missing buildingMaterial values filled with mode (%s)', mode_value)
    return df

def fill_missing_type(df: pd.DataFrame) -> pd.DataFrame:
    '''Filling missing values in the type column'''
    logging.info('Filling missing values in the type column')
    mode_value: str = df['type'].mode()[0]
    df['type'] = df['type'].fillna(mode_value)
    logging.info('Missing type values filled with mode (%s)', mode_value)
    return df

def fill_missing_build_year(df: pd.DataFrame) -> pd.DataFrame:
    '''Filling missing values in the buildYear column'''
    logging.info('Filling missing values in the buildYear column')
    df['buildYear'] = df.groupby('city')['buildYear'].transform(lambda x: x.fillna(x.median()))
    logging.info('Missing buildYear values filled with median within the city')
    return df

def fill_missing_floor_count(df: pd.DataFrame) -> pd.DataFrame:
    '''Filling missing values in the floorCount column'''
    logging.info('Filling missing values in the floorCount column')
    df['floorCount'] = df['floorCount'].fillna(df['floorCount'].mean()).round().astype('Int64')
    logging.info('Missing floorCount values filled with mean value')
    return df

def fill_missing_floor(df: pd.DataFrame) -> pd.DataFrame:
    '''Filling missing values in the floor column'''
    logging.info('Filling missing values in the floor column')
    floor_means = df.groupby('floorCount')['floor'].mean()
    
    def fill_floor(row):
        if pd.notna(row['floor']):
            return row['floor']
        return round(floor_means.get(row['floorCount'], df['floor'].mean()))
    
    df['floor'] = df.apply(fill_floor, axis=1)
    logging.info('Missing floor values filled based on floorCount')
    return df

def fill_missing_distances(df: pd.DataFrame) -> pd.DataFrame:
    '''Filling missing values in distance columns to various facilities'''
    logging.info('Filling missing values in distance columns to various facilities')
    distance_columns: List[str] = ['schoolDistance', 'clinicDistance', 'postOfficeDistance', 'kindergartenDistance', 'restaurantDistance', 'collegeDistance', 'pharmacyDistance']
    
    for column in distance_columns:
        correlated_columns: List[str] = [col for col in distance_columns if col != column and df[column].isnull().any() and df[col].notnull().any()]
        for correlated_column in correlated_columns:
            df[column] = df[column].fillna(df[correlated_column])
        df[column] = df.groupby('city')[column].transform(lambda x: x.fillna(x.mean()))
    logging.info('Missing distance values filled')
    return df

def fill_missing_has_elevator(df: pd.DataFrame) -> pd.DataFrame:
    '''Filling missing values in the hasElevator column'''
    logging.info('Filling missing values in the hasElevator column')
    df['hasElevator'] = df.apply(
        lambda row: 'yes' if pd.isna(row['hasElevator']) and row['floorCount'] > 5 else ('no' if pd.isna(row['hasElevator']) else row['hasElevator']),
        axis=1
    )
    logging.info('Missing hasElevator values filled based on floorCount')
    return df

def replace_yes_no(df: pd.DataFrame) -> pd.DataFrame:
    '''Replacing "yes" with 1 and "no" with 0 in all columns'''
    logging.info('Replacing "yes" with 1 and "no" with 0 in all columns')
    df = df.replace({'yes': 1, 'no': 0})
    return df

def replace_ownership_value(df: pd.DataFrame) -> pd.DataFrame:
    '''Replacing udział with part ownership in the ownership column'''
    logging.info('Replacing udział with part ownership in the ownership column')
    df['ownership'] = df['ownership'].replace('udział', 'part ownership')
    return df

def save_clean_data(df: pd.DataFrame, save_directory: str) -> None:
    '''Saving cleaned data'''
    logging.info('Saving cleaned data')
    current_datetime: str = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_name: str = f"cleaned_data_{current_datetime}.csv"
    save_path: str = os.path.join(save_directory, file_name)

    df.to_csv(save_path, index=False)
    logging.info('Cleaned data saved at: %s', save_path)

def check_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    '''Checking remaining missing values in the data'''
    logging.info('Checking remaining missing values in the data')
    missing_summary: pd.DataFrame = df.isnull().sum().to_frame(name='Missing Values')
    missing_summary['Percentage'] = (missing_summary['Missing Values'] / len(df)) * 100
    logging.info('Final report on missing values: %s', missing_summary)
    return df

def main() -> None:
    logging.info('-----Start-----')
    directory_path: str = r'.\raw_data'
    clean_folder: str = r'.\clean_data'

    df: pd.DataFrame = load_all_data(directory_path)
    remove_non_unique_ids(df)
    fill_condition(df)
    fill_missing_building_material(df)
    fill_missing_type(df)
    fill_missing_build_year(df)
    fill_missing_floor_count(df)
    fill_missing_floor(df)
    fill_missing_distances(df)
    fill_missing_has_elevator(df)
    df = replace_yes_no(df)
    df = replace_ownership_value(df)
    check_missing_values(df)
    save_clean_data(df, clean_folder)
    logging.info('-----End-----')

if __name__ == "__main__":
    main()