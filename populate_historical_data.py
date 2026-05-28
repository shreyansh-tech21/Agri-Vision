"""
Populate database with sample historical disease occurrences and weather data
This provides training data for the Historical Pattern Analyzer
"""
from app import app, db
from models import DiseaseOccurrence, WeatherData, Disease
from datetime import datetime, timedelta
import random

def populate_historical_data():
    """Populate database with sample historical data for ML training"""
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Clear existing historical data
        DiseaseOccurrence.query.delete()
        WeatherData.query.delete()
        db.session.commit()
        
        # Get existing diseases
        diseases = Disease.query.all()
        if not diseases:
            print("No diseases found in database. Please run populate_disease_data.py first.")
            return
        
        print(f"Found {len(diseases)} diseases in database")
        
        # Locations to generate data for
        locations = [
            {'name': 'Punjab, India', 'lat': 30.3753, 'lon': 76.7821},
            {'name': 'Gujarat, India', 'lat': 22.2587, 'lon': 71.1924},
            {'name': 'Maharashtra, India', 'lat': 19.7515, 'lon': 75.7139},
            {'name': 'Haryana, India', 'lat': 29.0588, 'lon': 76.0856},
            {'name': 'Rajasthan, India', 'lat': 27.0238, 'lon': 74.2179}
        ]
        
        # Generate data for the past 2 years
        end_date = datetime.now()
        start_date = end_date - timedelta(days=730)
        
        disease_occurrences = []
        weather_records = []
        
        current_date = start_date
        while current_date <= end_date:
            for location in locations:
                # Generate weather data
                # Seasonal weather patterns for India
                month = current_date.month
                
                # Temperature (Celsius) - varies by season
                if month in [12, 1, 2]:  # Winter
                    temp_avg = random.uniform(10, 25)
                    temp_max = temp_avg + random.uniform(5, 10)
                    temp_min = temp_avg - random.uniform(5, 10)
                elif month in [3, 4, 5]:  # Spring
                    temp_avg = random.uniform(20, 35)
                    temp_max = temp_avg + random.uniform(5, 8)
                    temp_min = temp_avg - random.uniform(5, 8)
                elif month in [6, 7, 8, 9]:  # Monsoon/Summer
                    temp_avg = random.uniform(25, 40)
                    temp_max = temp_avg + random.uniform(3, 7)
                    temp_min = temp_avg - random.uniform(3, 7)
                else:  # Autumn
                    temp_avg = random.uniform(18, 32)
                    temp_max = temp_avg + random.uniform(4, 8)
                    temp_min = temp_avg - random.uniform(4, 8)
                
                # Humidity (%) - higher during monsoon
                if month in [6, 7, 8, 9]:
                    humidity = random.uniform(70, 95)
                else:
                    humidity = random.uniform(30, 70)
                
                # Rainfall (mm) - monsoon season
                if month in [6, 7, 8, 9]:
                    rainfall = random.uniform(0, 50)
                elif month in [3, 4, 5]:  # Pre-monsoon
                    rainfall = random.uniform(0, 15)
                else:
                    rainfall = random.uniform(0, 5)
                
                # Wind speed (km/h)
                wind_speed = random.uniform(5, 25)
                
                # Pressure (hPa)
                pressure = random.uniform(1000, 1020)
                
                weather = WeatherData(
                    location_name=location['name'],
                    latitude=location['lat'],
                    longitude=location['lon'],
                    date=current_date.date(),
                    temperature_avg=round(temp_avg, 1),
                    temperature_max=round(temp_max, 1),
                    temperature_min=round(temp_min, 1),
                    humidity=round(humidity, 1),
                    rainfall=round(rainfall, 1),
                    wind_speed=round(wind_speed, 1),
                    pressure=round(pressure, 1)
                )
                weather_records.append(weather)
                
                # Generate disease occurrences based on weather conditions
                # Higher probability during favorable conditions
                for disease in diseases:
                    disease_name = disease.name.lower().replace(' ', '_')
                    
                    # Simple logic to determine if disease should occur
                    # This is just for sample data generation
                    occurrence_probability = 0.02  # Base 2% chance per day
                    
                    # Adjust probability based on weather
                    if disease_name == 'bacterial_blight':
                        if humidity > 70 and rainfall > 5:
                            occurrence_probability += 0.15
                    elif disease_name == 'fusarium_wilt':
                        if temp_avg > 25 and temp_avg < 30:
                            occurrence_probability += 0.10
                    elif disease_name == 'verticillium_wilt':
                        if temp_avg > 20 and temp_avg < 25:
                            occurrence_probability += 0.10
                    elif disease_name == 'powdery_mildew':
                        if humidity > 60 and temp_avg > 20 and temp_avg < 28:
                            occurrence_probability += 0.12
                    elif disease_name == 'cotton_root_rot':
                        if temp_avg > 28 and rainfall > 10:
                            occurrence_probability += 0.15
                    elif disease_name == 'alternaria_leaf_spot':
                        if humidity > 70 and rainfall > 5:
                            occurrence_probability += 0.12
                    elif disease_name == 'cotton_boll_rot':
                        if humidity > 80 and rainfall > 10:
                            occurrence_probability += 0.15
                    elif disease_name == 'red_leaf_spot':
                        if humidity > 65 and rainfall > 5:
                            occurrence_probability += 0.10
                    
                    # Randomly decide if disease occurs
                    if random.random() < occurrence_probability:
                        severity = random.choice(['low', 'moderate', 'high', 'severe'])
                        affected_area = random.uniform(1, 50) if severity in ['high', 'severe'] else random.uniform(0.5, 10)
                        
                        occurrence = DiseaseOccurrence(
                            disease_id=disease.id,
                            location_name=location['name'],
                            latitude=location['lat'],
                            longitude=location['lon'],
                            occurrence_date=current_date.date(),
                            severity=severity,
                            affected_area=round(affected_area, 2),
                            notes=f"Sample occurrence generated for {disease.name}"
                        )
                        disease_occurrences.append(occurrence)
            
            current_date += timedelta(days=1)
        
        # Batch insert for performance
        print(f"Inserting {len(weather_records)} weather records...")
        db.session.add_all(weather_records)
        db.session.commit()
        
        print(f"Inserting {len(disease_occurrences)} disease occurrences...")
        db.session.add_all(disease_occurrences)
        db.session.commit()
        
        print("✓ Historical data populated successfully!")
        print(f"  - Weather records: {len(weather_records)}")
        print(f"  - Disease occurrences: {len(disease_occurrences)}")
        print(f"  - Time period: {start_date.date()} to {end_date.date()}")
        print(f"  - Locations: {len(locations)}")
        
        # Print some statistics
        print("\nDisease occurrence statistics:")
        disease_counts = {}
        for occ in disease_occurrences:
            disease_name = Disease.query.get(occ.disease_id).name
            disease_counts[disease_name] = disease_counts.get(disease_name, 0) + 1
        
        for disease_name, count in sorted(disease_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {disease_name}: {count} occurrences")

if __name__ == "__main__":
    populate_historical_data()
