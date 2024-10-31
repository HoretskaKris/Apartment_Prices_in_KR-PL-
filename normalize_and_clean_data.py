import pandas as pd
import os
import logging
from datetime import datetime
from typing import List, Dict
import numpy as np

pd.set_option('future.no_silent_downcasting', True)

# Налаштування логування
log_directory: str = r'.\logs'
os.makedirs(log_directory, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_directory, 'normalize_and_clean_data.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

def load_all_data(directory_path: str) -> pd.DataFrame:
    '''Завантаження даних з усіх файлів в вказаній папці та обдєднання їх в один дата сет'''
    logging.info('Завантаження даних з усіх файлів в папці %s', directory_path)
    # Створюємо пустий список для зберігання всіх датафреймів
    dataframes: List[pd.DataFrame] = []
    
    # Проходимо по всіх файлах у вказаніній папці
    for file in os.listdir(directory_path):
        if file.endswith('.csv'):
            file_path: str = os.path.join(directory_path, file)
            try:
                df: pd.DataFrame = pd.read_csv(file_path)
                dataframes.append(df)
                logging.info('Файл %s успішно завантажено', file)
            except Exception as e:
                logging.error('Не вдалося завантажити файл %s: %s', file, e)
    
    # Об'єднуємо всі датафрейми в один
    combined_df: pd.DataFrame = pd.concat(dataframes, ignore_index=True)
    logging.info('Всього завантажено %d рядків даних', len(combined_df))
    return combined_df

def remove_non_unique_ids(df: pd.DataFrame) -> pd.DataFrame:
    logging.info('Видалення неунікальних ID')
    if 'id' in df.columns:
        original_length: int = len(df)
        df = df.drop_duplicates(subset='id', keep='first')
        logging.info('Видалено %d дублікатів', original_length - len(df))
    return df

def get_price_stats_for_city(df: pd.DataFrame, city: str) -> Dict[str, Dict[str, float]]:
    '''Отримання мінімальних та максимальних цін для категорій 'premium' та 'low' для заданого міста'''
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
    '''Заповнення пропущених значень у стовпці condition на основі цін та міста'''
    logging.info('Заповнення пропущених значень у стовпці condition')
    if 'condition' in df.columns and 'city' in df.columns and 'price' in df.columns:
        city_price_stats = {}
        
        for index, row in df.iterrows():
            if pd.isna(row['condition']):
                city = row['city']
                # Якщо даних для цього міста ще немає, викликаємо функцію для їх отримання
                if city not in city_price_stats:
                    city_price_stats[city] = get_price_stats_for_city(df, city)
                
                premium_stats = city_price_stats[city].get('premium', {})
                low_stats = city_price_stats[city].get('low', {})
                
                # Визначаємо значення condition на основі ціни
                if 'min' in premium_stats and premium_stats['min'] <= row['price'] <= premium_stats['max']:
                    df.at[index, 'condition'] = 'premium'
                elif 'min' in low_stats and low_stats['min'] <= row['price'] <= low_stats['max']:
                    df.at[index, 'condition'] = 'low'
                else:
                    df.at[index, 'condition'] = 'medium'
        logging.info('Пропущені значення condition заповнено')
    return df

def fill_missing_building_material(df: pd.DataFrame) -> pd.DataFrame:
    logging.info('Заповнення пропусків у стовпці buildingMaterial')
    mode_value: str = df['buildingMaterial'].mode()[0]
    df['buildingMaterial'] = df['buildingMaterial'].fillna(mode_value)
    logging.info('Пропущені значення buildingMaterial заповнено модою (%s)', mode_value)
    return df

def fill_missing_type(df: pd.DataFrame) -> pd.DataFrame:
    logging.info('Заповнення пропусків у стовпці type')
    mode_value: str = df['type'].mode()[0]
    df['type'] = df['type'].fillna(mode_value)
    logging.info('Пропущені значення type заповнено модою (%s)', mode_value)
    return df

def fill_missing_build_year(df: pd.DataFrame) -> pd.DataFrame:
    logging.info('Заповнення пропусків у стовпці buildYear')
    df['buildYear'] = df.groupby('city')['buildYear'].transform(lambda x: x.fillna(x.median()))
    logging.info('Пропущені значення buildYear заповнено медіаною в межах міста')
    return df

def fill_missing_floor_count(df: pd.DataFrame) -> pd.DataFrame:
    logging.info('Заповнення пропусків у стовпці floorCount')
    df['floorCount'] = df['floorCount'].fillna(df['floorCount'].mean()).round().astype('Int64')
    logging.info('Пропущені значення floorCount заповнено середнім значенням')
    return df

def fill_missing_floor(df: pd.DataFrame) -> pd.DataFrame:
    logging.info('Заповнення пропусків у стовпці floor')
    # Зберігаємо середні значення поверхів для кожної кількості поверхів у змінну
    floor_means = df.groupby('floorCount')['floor'].mean()
    
    def fill_floor(row):
        if pd.notna(row['floor']):
            return row['floor']
        return round(floor_means.get(row['floorCount'], df['floor'].mean()))
    
    df['floor'] = df.apply(fill_floor, axis=1)
    logging.info('Пропущені значення floor заповнено на основі floorCount')
    return df

def fill_missing_distances(df: pd.DataFrame) -> pd.DataFrame:
    logging.info('Заповнення пропусків у стовпцях з відстанями до об\'єктів')
    distance_columns: List[str] = ['schoolDistance', 'clinicDistance', 'postOfficeDistance', 'kindergartenDistance', 'restaurantDistance', 'collegeDistance', 'pharmacyDistance']
    
    for column in distance_columns:
        correlated_columns: List[str] = [col for col in distance_columns if col != column and df[column].isnull().any() and df[col].notnull().any()]
        for correlated_column in correlated_columns:
            df[column] = df[column].fillna(df[correlated_column])
        # Якщо ще залишились пропуски, заповнюємо середнім значенням у межах міста
        df[column] = df.groupby('city')[column].transform(lambda x: x.fillna(x.mean()))
    logging.info('Пропущені значення відстаней заповнено')
    return df

def fill_missing_has_elevator(df: pd.DataFrame) -> pd.DataFrame:
    logging.info('Заповнення пропусків у стовпці hasElevator')
    df['hasElevator'] = df.apply(
        lambda row: 'yes' if pd.isna(row['hasElevator']) and row['floorCount'] > 5 else ('no' if pd.isna(row['hasElevator']) else row['hasElevator']),
        axis=1
    )
    logging.info('Пропущені значення hasElevator заповнено залежно від floorCount')
    return df

def replace_yes_no(df: pd.DataFrame) -> pd.DataFrame:
    '''Заміна значень "yes" на 1 та "no" на 0 у всіх стовпцях'''
    logging.info('Заміна значень yes/no на 1/0 у всіх стовпцях')
    df = df.replace({'yes': 1, 'no': 0})
    return df

def replace_ownership_value(df: pd.DataFrame) -> pd.DataFrame:
    logging.info('Заміна значення udział на part ownership у стовпці ownership')
    df['ownership'] = df['ownership'].replace('udział', 'part ownership')
    return df

def save_clean_data(df: pd.DataFrame, save_directory: str) -> None:
    logging.info('Збереження очищених даних')
    # Створюємо назву файлу з датою та часом
    current_datetime: str = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_name: str = f"cleaned_data_{current_datetime}.csv"
    save_path: str = os.path.join(save_directory, file_name)
    # Зберігаємо очищені дані у вказаній папці
    df.to_csv(save_path, index=False)
    logging.info('Очищені дані збережено за адресою: %s', save_path)

def check_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    logging.info('Перевірка залишкових пропусків у даних')
    # Перевірка, чи залишились пропуски після заповнення
    missing_summary: pd.DataFrame = df.isnull().sum().to_frame(name='Missing Values')
    missing_summary['Percentage'] = (missing_summary['Missing Values'] / len(df)) * 100
    logging.info('Остаточний звіт про пропуски: %s', missing_summary)
    print("Остаточний звіт про пропуски:")
    print(missing_summary)
    return df

def main() -> None:
    logging.info('-----Start-----')
    directory_path: str = r'.\raw_data'
    clean_folder: str = r'.\clean_data'

    # Завантаження даних
    df: pd.DataFrame = load_all_data(directory_path)
    df = remove_non_unique_ids(df)
    df = fill_condition(df)
    df = fill_missing_building_material(df)
    df = fill_missing_type(df)
    df = fill_missing_build_year(df)
    df = fill_missing_floor_count(df)
    df = fill_missing_floor(df)
    df = fill_missing_distances(df)
    df = fill_missing_has_elevator(df)
    df = replace_yes_no(df)
    df = replace_ownership_value(df)
    save_clean_data(df, clean_folder)
    logging.info('-----End-----')

if __name__ == "__main__":
    main()
