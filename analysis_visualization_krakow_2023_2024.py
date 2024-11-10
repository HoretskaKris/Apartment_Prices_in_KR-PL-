import os
import re
from typing import Dict, Optional, Tuple

import folium
import pandas as pd
import seaborn as sns
from folium.plugins import HeatMap
from matplotlib import pyplot as plt
from opencage.geocoder import OpenCageGeocode

from config import API_KEY

geocoder = OpenCageGeocode(API_KEY)
city_coordinates_cache: Dict[str, Tuple[float, float]] = {}


def combines_sale_files(*paths: str, city_name: str) -> pd.DataFrame:
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

                filtered_df = df[df['city'].str.lower() == city_name.lower()]
                dataframes.append(filtered_df)

    combined_df = pd.concat(dataframes, ignore_index=True)
    return combined_df


def get_city_coordinates(city_name: str) -> Optional[Tuple[float, float]]:
    """Get latitude and longitude for a specific city name using OpenCage."""
    normalized_city_name = city_name.strip().lower()

    if normalized_city_name in city_coordinates_cache:
        return city_coordinates_cache[normalized_city_name]

    try:
        result = geocoder.geocode(city_name)
        if result:
            coordinates = (result[0]['geometry']['lat'],
                           result[0]['geometry']['lng'])
            city_coordinates_cache[normalized_city_name] = coordinates
            return coordinates
        else:
            raise ValueError(
                "Coordinates for the specified city could not be found.")
    except Exception as e:
        print(f"Error: {e}")
        return None


def visualize_avg_price_per_sqm_on_map(data: pd.DataFrame, city_name: str = "Krakow") -> Optional[folium.Map]:
    """Function to visualize the average price per square meter of apartments on a map of a specified city."""
    city_coordinates = get_city_coordinates(city_name)
    if not city_coordinates:
        print("Could not retrieve city coordinates.")
        return None

    filtered_data = data.dropna(
        subset=['latitude', 'longitude', 'squareMeters', 'price'])
    filtered_data['pricePerSqM'] = filtered_data['price'] / \
        filtered_data['squareMeters']
    filtered_data = filtered_data[(filtered_data['pricePerSqM'] > 50) & (
        filtered_data['pricePerSqM'] < 100000)]

    city_map = folium.Map(location=city_coordinates, zoom_start=12)

    heat_data = [[row['latitude'], row['longitude'], row['pricePerSqM']]
                 for _, row in filtered_data.iterrows()]
    HeatMap(heat_data, radius=15, max_zoom=13, gradient={
            0.0: 'blue', 0.3: 'lime', 0.6: 'yellow', 1.0: 'red'}, min_opacity=0.4).add_to(city_map)

    folium.Marker(city_coordinates, popup=f'{city_name} City Centre', icon=folium.Icon(
        color='red')).add_to(city_map)

    return city_map


def visualize_price_vs_amenities_correlation(data: pd.DataFrame) -> None:
    """Function to plot the correlation between price per square meter and available amenities."""
    amenities_columns = [
        'hasParkingSpace',
        'hasBalcony',
        'hasElevator',
        'hasSecurity',
        'hasStorageRoom'
    ]

    available_columns = [
        col for col in amenities_columns if col in data.columns]
    if len(available_columns) < len(amenities_columns):
        missing = set(amenities_columns) - set(available_columns)
        print(f"Warning: Missing columns {missing}")

    data['pricePerSqm'] = data['price'] / data['squareMeters']
    correlation_data = data[['pricePerSqm'] + available_columns]
    corr_matrix = correlation_data.corr()

    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', linewidths=0.5)
    plt.title('Correlation between Price per Square Meter and Amenities')
    plt.show()


def visualize_poi_influence_on_price(data: pd.DataFrame) -> None:
    """Function to analyze and visualize the influence of distances to points of interest on apartment prices."""
    poi_columns = [
        'kindergartenDistance',
        'clinicDistance',
        'postOfficeDistance',
        'schoolDistance',
        'restaurantDistance',
        'collegeDistance',
        'pharmacyDistance'
    ]

    filtered_data = data.dropna(subset=poi_columns + ['price'])
    plt.figure(figsize=(16, 20))

    for i, poi in enumerate(poi_columns, 1):
        plt.subplot(4, 2, i)
        sns.regplot(data=filtered_data, x=poi, y='price', scatter_kws={
                    'alpha': 0.6}, line_kws={'color': 'green'})
        plt.title(f'Influence of {poi} on Price')
        plt.xlabel(f'Distance to {poi}')
        plt.ylabel('Price (PLN)')

    plt.tight_layout()
    plt.show()


def visualize_poi_popularity_by_parameters(data: pd.DataFrame) -> None:
    """Function to analyze and visualize the popularity of apartments by parameters: number of rooms, floor, and number of floors in the building."""
    filtered_data = data.dropna(subset=['rooms', 'floor', 'floorCount'])

    plt.figure(figsize=(18, 15))

    plt.subplot(3, 1, 1)
    sns.countplot(data=filtered_data, x='rooms', hue='rooms',
                  palette='viridis', legend=False)
    plt.title('Popularity of Apartments by Number of Rooms')

    plt.subplot(3, 1, 2)
    sns.countplot(data=filtered_data, x='floor', hue='floor',
                  palette='viridis', legend=False)
    plt.title('Popularity of Apartments by Floor')

    plt.subplot(3, 1, 3)
    sns.countplot(data=filtered_data, x='floorCount',
                  hue='floorCount', palette='viridis', legend=False)
    plt.title('Popularity of Apartments by Number of Floors in Building')

    plt.tight_layout()
    plt.show()


def visualize_price_distribution_boxplot(data: pd.DataFrame) -> None:
    """Function to visualize the price distribution of apartments using a box plot for each room type."""
    filtered_data = data.dropna(subset=['price', 'rooms'])

    plt.figure(figsize=(12, 8))
    sns.boxplot(data=filtered_data, x='rooms', y='price')
    plt.title('Price Distribution of Apartments by Number of Rooms')
    plt.xlabel('Number of Rooms')
    plt.ylabel('Price (PLN)')
    plt.tight_layout()
    plt.show()


def visualize_build_year_and_condition(data: pd.DataFrame) -> None:
    """Function to visualize the distribution of apartment conditions by build year."""
    plt.figure(figsize=(14, 8))
    sns.boxplot(data=data.dropna(
        subset=['buildYear', 'condition']), x='buildYear', y='condition')
    plt.title('Distribution of Apartment Conditions by Build Year')
    plt.xlabel('Build Year')
    plt.ylabel('Condition')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def visualize_ownership_and_condition_vs_price(data: pd.DataFrame) -> None:
    """Function to visualize price distribution by ownership type and apartment condition."""
    plt.figure(figsize=(14, 8))
    sns.violinplot(data=data.dropna(subset=['ownership', 'condition', 'price']),
                   x='ownership', y='price', hue='condition', split=True, palette='muted')
    plt.title('Price Distribution by Ownership Type and Apartment Condition')
    plt.xlabel('Ownership Type')
    plt.ylabel('Price (PLN)')
    plt.tight_layout()
    plt.show()


def visualize_centre_distance_and_build_year_vs_price(data: pd.DataFrame) -> None:
    """Function to visualize the influence of distance to centre and build year on price."""
    plt.figure(figsize=(14, 8))
    sns.scatterplot(data=data.dropna(subset=['centreDistance', 'buildYear', 'price']),
                    x='centreDistance', y='price', hue='buildYear', palette='coolwarm', alpha=0.6)
    plt.title('Influence of Distance to Centre and Build Year on Price')
    plt.xlabel('Distance to City Centre (km)')
    plt.ylabel('Price (PLN)')
    plt.tight_layout()
    plt.show()


def visualize_build_year_and_floor_distribution(data: pd.DataFrame) -> None:
    """Function to visualize the distribution of apartments by build year and floor."""
    plt.figure(figsize=(14, 10))
    sns.heatmap(data=data.dropna(subset=['buildYear', 'floor']).pivot_table(index='buildYear', columns='floor', aggfunc='size', fill_value=0),
                cmap='viridis')
    plt.title('Distribution of Apartments by Build Year and Floor')
    plt.xlabel('Floor')
    plt.ylabel('Build Year')
    plt.tight_layout()
    plt.show()
