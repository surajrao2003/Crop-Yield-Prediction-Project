import numpy as np
from flask import Flask, request, render_template, flash, redirect, url_for
import pickle
import os

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Load the model
try:
    model = pickle.load(open("xgboost_yield_prediction_final.pkl", "rb"))
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# Required form fields and their validation ranges
FORM_FIELDS = {
    'state_names': {'type': int, 'min': 0, 'max': 32},
    'season_names': {'type': int, 'min': 1, 'max': 6},
    'crop_names': {'type': int, 'min': 1, 'max': 99},
    'temperature': {'type': float, 'min': -20, 'max': 50},  # in Celsius
    'wind_speed': {'type': float, 'min': 0, 'max': 200},    # in km/h
    'precipitation': {'type': float, 'min': 0, 'max': 1000}, # in mm
    'humidity': {'type': float, 'min': 0, 'max': 100},      # in percentage
    'soil_type': {'type': int, 'min': 1, 'max': 7},
    'N': {'type': float, 'min': 0, 'max': 1000},            # Nitrogen content
    'P': {'type': float, 'min': 0, 'max': 1000},            # Phosphorus content
    'K': {'type': float, 'min': 0, 'max': 1000}             # Potassium content
}

def validate_input(form_data):
    """Validate form inputs against expected types and ranges."""
    errors = []
    validated_data = {}
    
    for field, config in FORM_FIELDS.items():
        value = form_data.get(field, '').strip()
        
        # Check if field is empty
        if not value:
            errors.append(f"{field.replace('_', ' ').title()} is required")
            continue
            
        try:
            # Convert to appropriate type
            if config['type'] == int:
                value = int(value)
            elif config['type'] == float:
                value = float(value)
                
            # Check value range
            if 'min' in config and value < config['min']:
                errors.append(f"{field.replace('_', ' ').title()} must be at least {config['min']}")
            elif 'max' in config and value > config['max']:
                errors.append(f"{field.replace('_', ' ').title()} must be at most {config['max']}")
                
            validated_data[field] = value
                
        except ValueError:
            errors.append(f"Invalid value for {field.replace('_', ' ').title()}: must be a {config['type'].__name__}")
    
    return validated_data, errors

@app.route("/")
def home():
    """Render the home page with the prediction form."""
    from flask import request
    return render_template("index.html", request=request)

@app.route('/predict', methods=['POST'])
def predict():
    """Handle prediction requests with input validation."""
    if not model:
        flash('Error: Prediction model is not available', 'error')
        return redirect(url_for('home'))
    
    # Validate form inputs
    validated_data, errors = validate_input(request.form)
    
    if errors:
        for error in errors:
            flash(error, 'error')
        # Instead of redirect, re-render index.html with current form values
        return render_template("index.html", request=request)
    
    try:
        # Prepare features in the correct order
        feature_order = [
            'state_names', 'season_names', 'crop_names', 'temperature',
            'wind_speed', 'precipitation', 'humidity', 'soil_type', 'N', 'P', 'K'
        ]
        features = [validated_data[field] for field in feature_order]
        
        # Make prediction
        prediction = model.predict([features])
        prediction_text = f"{prediction[0]:.2f}"  # Format to 2 decimal places
        
        return render_template('predict.html', 
                               prediction_text=prediction_text,
                               input_data=validated_data)
                               
    except Exception as e:
        app.logger.error(f"Prediction error: {str(e)}")
        flash('An error occurred while making the prediction. Please try again.', 'error')
        return redirect(url_for('home'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error='Page not found'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error='Internal server error'), 500

if __name__ == "__main__":
    app.run(debug=True)