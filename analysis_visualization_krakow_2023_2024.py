import os
import re

import folium
import pandas as pd
import seaborn as sns
from folium.plugins import HeatMap
from matplotlib import pyplot as plt


def combines_sale_files(*paths, city_name):
    """Function to combine multiple sale files into a single DataFrame, filter by city, and adjust data types."""
    dataframes = []
    for path in paths:
        year_match = re.search(r'_(\d{4})', path)
        year = int(year_match.group(1)) if year_match else None

        for file_name in os.listdir(path):
            file_path = os.path.join(path, file_name)
            if os.path.isfile(file_path):
                df = pd.read_csv(file_path)
                df['rooms'] = df['rooms'].astype(int)
                df['floor'] = df['floor'].astype(int)
                df['year'] = year
                dataframes.append(df)

    combined_df = pd.concat(dataframes, ignore_index=True)

    filtered_df = combined_df[combined_df['city'].str.lower()
                              == city_name.lower()]

    return filtered_df


def visualize_avg_price_per_sqm_on_map(data):
    """Function to visualize the average price per square meter of apartments on a map of Krakow."""
    filtered_data = data.dropna(
        subset=[
            'latitude',
            'longitude',
            'squareMeters',
            'price'])

    filtered_data['pricePerSqM'] = filtered_data['price'] / \
        filtered_data['squareMeters']

    filtered_data = filtered_data[(filtered_data['pricePerSqM'] > 50) & (
        filtered_data['pricePerSqM'] < 100000)]

    krakow_map = folium.Map(location=[50.0614, 19.9366], zoom_start=12)

    heat_data = [[row['latitude'], row['longitude'], row['pricePerSqM']]
                 for _, row in filtered_data.iterrows()]
    HeatMap(
        heat_data,
        radius=15,
        max_zoom=13,
        gradient={
            0.0: 'blue',
            0.3: 'lime',
            0.6: 'yellow',
            1.0: 'red'},
        min_opacity=0.4).add_to(krakow_map)

    folium.Marker([50.0614, 19.9366], popup='Krakow City Centre',
                  icon=folium.Icon(color='red')).add_to(krakow_map)

    return krakow_map


def visualize_price_vs_amenities_correlation(df):
    """Function to plot the correlation between price per square meter and available amenities."""
    amenities_columns = [
        'hasParkingSpace',
        'hasBalcony',
        'hasElevator',
        'hasSecurity',
        'hasStorageRoom']

    available_columns = []
    for col in amenities_columns:
        if col in df.columns:
            available_columns.append(col)
        else:
            print(
                f"Warning: Column '{col}' is missing from the dataset, skipping it.")

    df['pricePerSqm'] = df['price'] / df['squareMeters']

    correlation_data = df[['pricePerSqm'] + available_columns]

    corr_matrix = correlation_data.corr()

    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', linewidths=0.5)
    plt.title('Correlation between Price per Square Meter and Amenities')
    plt.show()


def visualize_poi_influence_on_price(data):
    """Function to analyze and visualize the influence of distances to points of interest (e.g., kindergartens, clinics) on apartment prices."""
    poi_columns = [
        'kindergartenDistance',
        'clinicDistance',
        'postOfficeDistance',
        'schoolDistance',
        'restaurantDistance',
        'collegeDistance',
        'pharmacyDistance']

    filtered_data = data.dropna(subset=poi_columns + ['price'])

    plt.figure(figsize=(16, 20))

    for i, poi in enumerate(poi_columns, 1):
        plt.subplot(4, 2, i)
        sns.regplot(
            data=filtered_data, x=poi, y='price', scatter_kws={
                'alpha': 0.6}, line_kws={
                'color': 'green'})
        plt.title(f'Influence of {poi} on Price')
        plt.xlabel(f'Distance to {poi}')
        plt.ylabel('Price (PLN)')

    plt.tight_layout()
    plt.show()


def visualize_poi_popularity_by_parameters(data):
    """Function to analyze and visualize the popularity of apartments by parameters: number of rooms, floor, and number of floors in the building."""
    filtered_data = data.dropna(subset=['rooms', 'floor', 'floorCount'])

    plt.figure(figsize=(18, 15))

    plt.subplot(3, 1, 1)
    sns.countplot(
        data=filtered_data,
        x='rooms',
        hue='rooms',
        palette='viridis',
        legend=False)
    plt.title('Popularity of Apartments by Number of Rooms')
    plt.xlabel('Number of Rooms')
    plt.ylabel('Number of Apartments')

    plt.subplot(3, 1, 2)
    sns.countplot(
        data=filtered_data,
        x='floor',
        hue='floor',
        palette='viridis',
        legend=False)
    plt.title('Popularity of Apartments by Floor')
    plt.xlabel('Floor')
    plt.ylabel('Number of Apartments')

    plt.subplot(3, 1, 3)
    sns.countplot(
        data=filtered_data,
        x='floorCount',
        hue='floorCount',
        palette='viridis',
        legend=False)
    plt.title('Popularity of Apartments by Number of Floors in Building')
    plt.xlabel('Number of Floors in Building')
    plt.ylabel('Number of Apartments')

    plt.tight_layout()
    plt.show()


def visualize_price_distribution_boxplot(data):
    """Function to visualize the price distribution of apartments using a box plot for each room type."""
    filtered_data = data.dropna(subset=['price', 'rooms'])

    plt.figure(figsize=(12, 8))
    sns.boxplot(data=filtered_data, x='rooms', y='price')
    plt.title('Price Distribution of Apartments by Number of Rooms')
    plt.xlabel('Number of Rooms')
    plt.ylabel('Price (PLN)')
    plt.tight_layout()
    plt.show()


def visualize_build_year_and_condition(data):
    """Function to visualize the distribution of apartment conditions by build year."""
    plt.figure(figsize=(14, 8))
    sns.boxplot(
        data=data.dropna(
            subset=[
                'buildYear',
                'condition']),
        x='buildYear',
        y='condition')
    plt.title('Distribution of Apartment Conditions by Build Year')
    plt.xlabel('Build Year')
    plt.ylabel('Condition')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def visualize_ownership_and_condition_vs_price(data):
    """Function to visualize price distribution by ownership type and apartment condition."""
    plt.figure(figsize=(14, 8))
    sns.violinplot(
        data=data.dropna(
            subset=[
                'ownership',
                'condition',
                'price']),
        x='ownership',
        y='price',
        hue='condition',
        split=True,
        palette='muted')
    plt.title('Price Distribution by Ownership Type and Apartment Condition')
    plt.xlabel('Ownership Type')
    plt.ylabel('Price (PLN)')
    plt.tight_layout()
    plt.show()


def visualize_centre_distance_and_build_year_vs_price(data):
    """Function to visualize the influence of distance to centre and build year on price. """
    plt.figure(figsize=(14, 8))
    sns.scatterplot(
        data=data.dropna(
            subset=[
                'centreDistance',
                'buildYear',
                'price']),
        x='centreDistance',
        y='price',
        hue='buildYear',
        palette='coolwarm',
        alpha=0.6)
    plt.title('Influence of Distance to Centre and Build Year on Price')
    plt.xlabel('Distance to City Centre (km)')
    plt.ylabel('Price (PLN)')
    plt.tight_layout()
    plt.show()


def visualize_build_year_and_floor_distribution(data):
    """Function to visualize the distribution of apartments by build year and floor."""
    plt.figure(figsize=(14, 10))
    sns.heatmap(
        data.dropna(
            subset=[
                'buildYear',
                'floor']).pivot_table(
            index='buildYear',
            columns='floor',
            aggfunc='size',
            fill_value=0),
        cmap='viridis')
    plt.title('Distribution of Apartments by Build Year and Floor')
    plt.xlabel('Floor')
    plt.ylabel('Build Year')
    plt.tight_layout()
    plt.show()
