# Apartment_Prices_in_KR-PL-
Apartment Prices in Poland KRA.
---

# Apartment Price Analysis in Krakow

Цей проєкт спрямований на аналіз цін на квартири у Кракові, з можливістю адаптації для інших міст і типів нерухомості (оренда або продаж). Метою є виявлення різних факторів, що впливають на ринок нерухомості, шляхом обробки та візуалізації даних.

## Огляд проєкту

Проєкт складається з наступних кроків:

1. **Попередній аналіз якості даних**: Оцінка та візуалізація якості даних для виявлення пропущених значень, аномалій та інших можливих проблем у даних перед подальшою обробкою.
2. **Підготовка та нормалізація даних**: Попередня обробка даних, що включає очищення, заповнення відсутніх значень та корекцію форматів.
3. **Категоризація даних**: Розподіл даних за типами (оренда чи продаж) та роками для детальнішого аналізу.
4. **Аналіз та візуалізація**: Створення візуалізацій для виявлення закономірностей у даних.
5. **Фінальний аналіз та візуалізації**: Підсумкові візуалізації для представлення основних результатів.

## Структура файлів

### 1. `data_quality_analysis.ipynb`
- **Опис**: Jupyter Notebook, який проводить початковий аналіз якості даних.
- **Основні функції**:
  - **Завантаження даних**: Об'єднання кількох файлів у єдиний датасет.
  - **Візуалізація пропущених значень**: Використання бібліотеки `missingno` для графічного представлення відсутніх значень у даних.
  - **Статистичний огляд**: Оцінка розподілу даних та ідентифікація аномалій у значеннях.

### 2. `normalize_and_clean_data.py`
- **Опис**: Скрипт для нормалізації та очищення даних.
- **Основні функції**:
  - **Завантаження та збереження даних**: Завантажує CSV-файли, очищає дані та зберігає оновлену версію.
  - **Видалення дублікатів**: Видаляє неповторні ідентифікатори, щоб уникнути дублювання записів.
  - **Заповнення відсутніх значень**: Заповнює пропущені значення у колонках, таких як `condition`, `buildYear`, `floorCount`, `floor`, `type`, `buildingMaterial` тощо.
  - **Корекція значень**: Заміна "yes"/"no" на 1/0, стандартизація значень у колонках (наприклад, `ownership`).

### 3. `splitting_data_by_type_year.py`
- **Опис**: Цей файл розподіляє дані за типами (оренда чи продаж) та роками, зберігаючи кожну категорію у відповідній папці.
- **Основні функції**:
  - **Перевірка наявності папок**: Перевіряє, чи існують потрібні папки для зберігання даних.
  - **Завантаження файлів за роками**: Завантажує файли CSV та організовує дані за роками.
  - **Збереження за категоріями**: Зберігає розподілені дані за роками в окремих папках для подальшого аналізу.

### 4. `analysis_visualization_krakow_2023_2024.py`
- **Опис**: Містить функції для створення різноманітних візуалізацій на основі оброблених даних про нерухомість у Кракові.
- **Основні функції**:
  - **Географічна візуалізація**: Теплова карта з використанням Folium, яка показує середню ціну за квадратний метр на мапі Кракова.
  - **Кореляція з параметрами**: Дослідження зв'язку між ціною та доступними зручностями (паркінг, балкон, ліфт тощо).
  - **Вплив відстані до точок інтересу**: Аналіз впливу відстаней до закладів (школи, лікарні, ресторани) на ціну квартир.
  - **Популярність квартир**: Візуалізація розподілу квартир за кількістю кімнат, поверхом та кількістю поверхів у будівлі.
  - **Інші фактори**: Візуалізації, які показують розподіл цін, залежність ціни від відстані до центру міста та року будівництва.

### 5. `presentation_analysis_visualization_krakow_2023_2024.ipynb`
- **Опис**: Jupyter Notebook, який містить підсумковий аналіз та візуалізації для презентації.
- **Основні функції**:
  - **Інтеграція всіх візуалізацій**: Підсумковий огляд результатів аналізу, включаючи всі раніше створені візуалізації.
  - **Фінальні висновки**: Підбиття підсумків та інсайти, що були отримані на основі дослідження.

## Гнучкість використання

Проєкт розроблений таким чином, що всі операції з даними для Кракова можна виконати і для інших міст або для іншого типу нерухомості (оренда чи продаж), вказавши відповідні значення в змінних (назва міста, шлях до даних, тип нерухомості).

## Джерело даних

Дані для проєкту були взяті з [Kaggle](https://www.kaggle.com/datasets/krzysztofjamroz/apartment-prices-in-poland/data), де представлені ціни на квартири в Польщі.

## Запуск проекту

### Вимоги
- **Python 3.x**
- **Бібліотеки**:
  - pandas
  - numpy
  - seaborn
  - matplotlib
  - folium
  - opencage.geocoder
  - інші

### Інструкції з налаштування та запуску

1. **Клонування репозиторію**:
   ```bash
   git clone [repository_url]
   ```
2. **Встановлення залежностей**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Запуск скриптів**:
   - Для аналізу якості даних:
     Відкрийте `data_quality_analysis.ipynb` у Jupyter Notebook та виконайте кроки для аналізу якості даних.
   - Для підготовки даних:
     ```bash
     python normalize_and_clean_data.py
     ```
   - Для категоризації даних:
     ```bash
     python splitting_data_by_type_year.py
     ```
   - Для візуалізації:
     Використовуйте `analysis_visualization_krakow_2023_2024.py` у Jupyter Notebook або виконайте безпосередньо для отримання візуалізацій.
   - Для фінального аналізу:
     Відкрийте `presentation_analysis_visualization_krakow_2023_2024.ipynb` для перегляду підсумкових візуалізацій та висновків.

--- 
---

# Apartment Price Analysis in Krakow

This project aims to analyze apartment prices in Krakow, with the flexibility to adapt the analysis for other cities and types of real estate (rent or sale). The goal is to identify factors influencing the real estate market through data processing and visualization.

## Project Overview

The project consists of the following steps:

1. **Preliminary Data Quality Analysis**: Evaluation and visualization of data quality to identify missing values, anomalies, and other potential issues before further processing.
2. **Data Preparation and Normalization**: Initial data processing, including cleaning, filling missing values, and correcting formats.
3. **Data Categorization**: Splitting data by type (rent or sale) and year for a more detailed analysis.
4. **Analysis and Visualization**: Creating visualizations to uncover patterns in the data.
5. **Final Analysis and Visualization**: Summary visualizations to present key findings.

## File Structure

### 1. `data_quality_analysis.ipynb`
- **Description**: Jupyter Notebook for initial data quality analysis.
- **Main Functions**:
  - **Data Loading**: Combines multiple files into a single dataset.
  - **Missing Values Visualization**: Uses the `missingno` library for graphical representation of missing data.
  - **Statistical Overview**: Evaluates data distribution and identifies anomalies.

### 2. `normalize_and_clean_data.py`
- **Description**: Script for normalizing and cleaning data.
- **Main Functions**:
  - **Data Loading and Saving**: Loads CSV files, cleans the data, and saves an updated version.
  - **Duplicate Removal**: Eliminates duplicate entries to avoid redundancy.
  - **Filling Missing Values**: Fills missing values in columns like `condition`, `buildYear`, `floorCount`, `floor`, `type`, `buildingMaterial`, and more.
  - **Value Correction**: Replaces "yes"/"no" with 1/0, standardizes values in columns (e.g., `ownership`).

### 3. `splitting_data_by_type_year.py`
- **Description**: This file splits data by type (rent or sale) and year, saving each category into a corresponding folder.
- **Main Functions**:
  - **Folder Existence Check**: Verifies if required folders for data storage exist.
  - **Loading Files by Year**: Loads CSV files and organizes data by year.
  - **Saving by Category**: Saves split data by year in separate folders for further analysis.

### 4. `analysis_visualization_krakow_2023_2024.py`
- **Description**: Contains functions to create various visualizations based on processed real estate data in Krakow.
- **Main Functions**:
  - **Geographical Visualization**: Heat map using Folium to show average price per square meter on a map of Krakow.
  - **Parameter Correlation**: Studies the relationship between price and available amenities (parking, balcony, elevator, etc.).
  - **Influence of Distance to Points of Interest**: Analyzes the effect of distances to facilities (schools, hospitals, restaurants) on apartment prices.
  - **Apartment Popularity**: Visualization of apartment distribution by the number of rooms, floor, and total number of floors in the building.
  - **Other Factors**: Visualizations showing price distribution, price dependency on distance to the city center, and year of construction.

### 5. `presentation_analysis_visualization_krakow_2023_2024.ipynb`
- **Description**: Jupyter Notebook containing the final analysis and visualizations for presentation.
- **Main Functions**:
  - **Integrated Visualizations**: Summary of analysis results, including all previously created visualizations.
  - **Final Insights**: Conclusions and insights gained from the study.

## Usage Flexibility

The project is designed such that all data processing steps for Krakow can be performed for other cities and types of real estate (rent or sale) by specifying the appropriate variables (city name, data path, property type).

## Data Source

The data for the project was sourced from [Kaggle](https://www.kaggle.com/datasets/krzysztofjamroz/apartment-prices-in-poland/data), providing apartment prices across Poland.

## Running the Project

### Requirements
- **Python 3.x**
- **Libraries**:
  - pandas
  - numpy
  - seaborn
  - matplotlib
  - folium
  - opencage.geocoder
  - others

### Setup and Execution Instructions

1. **Clone the Repository**:
   ```bash
   git clone [repository_url]
   ```
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Scripts**:
   - For data quality analysis:
     Open `data_quality_analysis.ipynb` in Jupyter Notebook and execute the steps for data quality assessment.
   - For data preparation:
     ```bash
     python normalize_and_clean_data.py
     ```
   - For data categorization:
     ```bash
     python splitting_data_by_type_year.py
     ```
   - For visualizations:
     Use `analysis_visualization_krakow_2023_2024.py` in Jupyter Notebook or execute directly for generating visualizations.
   - For final analysis:
     Open `presentation_analysis_visualization_krakow_2023_2024.ipynb` to review final visualizations and conclusions.

--- 
