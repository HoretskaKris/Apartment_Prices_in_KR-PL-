import pandas as pd
import os
from datetime import datetime

def load_all_data(directory_path):
    '''Завантаження даних з усіх файлів в вказаній папці та обєднання їх в один дата сет'''
    # Створюємо пустий список для зберігання всіх датафреймів
    dataframes = []
    
    # Проходимо по всіх файлах у вказаній папці
    for file in os.listdir(directory_path):
        if file.endswith('.csv'):
            file_path = os.path.join(directory_path, file)
            try:
                df = pd.read_csv(file_path)
                dataframes.append(df)
            except Exception as e:
                print(f"Не вдалося завантажити файл {file}: {e}")
    
    # Об'єднуємо всі датафрейми в один
    combined_df = pd.concat(dataframes, ignore_index=True)
    return combined_df

def remove_non_unique_ids(df):
    if 'id' in df.columns:
        df = df.drop_duplicates(subset='id', keep='first')
    return df

def fill_missing_condition(df):
    '''Заповнення пропущених значень у стовпці condition'''
    if 'condition' in df.columns:
        premium_min = df[df['condition'] == 'premium']['price'].min()
        premium_max = df[df['condition'] == 'premium']['price'].max()
        low_min = df[df['condition'] == 'low']['price'].min()
        low_max = df[df['condition'] == 'low']['price'].max()
        
        def fill_condition(row):
            if pd.isna(row['condition']):
                if premium_min <= row['price'] <= premium_max:
                    return 'premium'
                elif low_min <= row['price'] <= low_max:
                    return 'low'
                else:
                    return 'medium'
            return row['condition']
        
        df['condition'] = df.apply(fill_condition, axis=1)
    return df

def fill_missing_building_material(df):
    # Заповнюємо пропуски в buildingMaterial модою (найпоширеніше значення)
    mode_value = df['buildingMaterial'].mode()[0]
    df['buildingMaterial'] = df['buildingMaterial'].fillna(mode_value)
    return df

def fill_missing_type(df):
    # Заповнюємо пропуски в type модою (найпоширеніше значення)
    mode_value = df['type'].mode()[0]
    df['type'] = df['type'].fillna(mode_value)
    return df

def fill_missing_build_year(df):
    # Заповнюємо пропуски в buildYear середнім або медіанним значенням в залежності від міста
    df['buildYear'] = df.groupby('city')['buildYear'].transform(lambda x: x.fillna(x.median()))
    return df

def fill_missing_floor_count(df):
    # Заповнюємо пропуски в floorCount середнім значенням і заокруглюємо до цілого числа
    df['floorCount'] = df['floorCount'].fillna(df['floorCount'].mean()).round().astype('Int64')
    return df

def fill_missing_floor(df):
    # Заповнюємо пропуски в floor залежно від floorCount
    df['floor'] = df.apply(
        lambda row: row['floor'] if pd.notna(row['floor']) else round(df[df['floorCount'] == row['floorCount']]['floor'].mean()),
        axis=1
    )
    return df

def fill_missing_distances(df):
    # Заповнюємо пропуски у відстанях до об'єктів на основі високо корельованих змінних
    distance_columns = ['schoolDistance', 'clinicDistance', 'postOfficeDistance', 'kindergartenDistance', 'restaurantDistance', 'collegeDistance', 'pharmacyDistance']
    
    for column in distance_columns:
        correlated_columns = [col for col in distance_columns if col != column and df[column].isnull().any() and df[col].notnull().any()]
        for correlated_column in correlated_columns:
            df[column] = df[column].fillna(df[correlated_column])
        # Якщо ще залишились пропуски, заповнюємо середнім значенням у межах міста
        df[column] = df.groupby('city')[column].transform(lambda x: x.fillna(x.mean()))
    return df

def fill_missing_has_elevator(df):
    # Заповнюємо пропуски в hasElevator залежно від floorCount
    df['hasElevator'] = df.apply(
        lambda row: 'yes' if pd.isna(row['hasElevator']) and row['floorCount'] > 5 else ('no' if pd.isna(row['hasElevator']) else row['hasElevator']),
        axis=1
    )
    return df

def replace_yes_no(df):
    '''Заміна значень "yes" на 1 та "no" на 0'''
    df['hasElevator'] = df['hasElevator'].replace({'yes': 1, 'no': 0})
    return df

def replace_ownership_value(df):
    # Заміна значення 'udział' на 'part ownership' у стовпці ownership
    df['ownership'] = df['ownership'].replace('udział', 'part ownership')
    return df

def save_clean_data(df, save_directory):
    # Створюємо назву файлу з датою та часом
    current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_name = f"cleaned_data_{current_datetime}.csv"
    save_path = os.path.join(save_directory, file_name)
    # Зберігаємо очищені дані у вказаній папці
    df.to_csv(save_path, index=False)
    print(f"Очищені дані збережено за адресою: {save_path}")

def check_missing_values(df):
    # Перевіряємо, чи залишились пропуски після заповнення
    missing_summary = df.isnull().sum().to_frame(name='Missing Values')
    missing_summary['Percentage'] = (missing_summary['Missing Values'] / len(df)) * 100
    print("Остаточний звіт про пропуски:")
    print(missing_summary)
    return df 

def main():
  directory_path = r'C:\Users\KrisMur\Desktop\PetProjekt1\Apartment_Prices_in_KR-PL-\raw_data'
  clean_folder = r'C:\Users\KrisMur\Desktop\PetProjekt1\Apartment_Prices_in_KR-PL-\clean_data'

  # Завантаження даних
  df = load_all_data(directory_path)
  df = remove_non_unique_ids(df)
  df = fill_missing_condition(df)
  df = fill_missing_building_material(df)
  df = fill_missing_type(df)
  df = fill_missing_build_year(df)
  df = fill_missing_floor_count(df)
  #тут довго
  df = fill_missing_floor(df)
  df = fill_missing_distances(df)
  df = fill_missing_has_elevator(df)
  df = replace_yes_no(df)
  df = replace_ownership_value(df)
  save_clean_data(df, clean_folder)
  print("end")

if __name__ == "__main__":
  main()
