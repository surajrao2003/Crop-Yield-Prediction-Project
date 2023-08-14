import numpy as np
from flask import Flask, request, jsonify, render_template
import pickle

# Create flask app
flask_app = Flask(__name__)
model = pickle.load(open("xgboost_yield_prediction_final.pkl", "rb"))

@flask_app.route("/")
def Home():
    return render_template("index.html")

@flask_app.route('/predict', methods=['POST'])
def predict():
    
    float_features = [float(x) for x in request.form.values()]
    features = [np.array(float_features)]
    final_prediction = model.predict(features)
    result_str = ''.join(str(e) for e in final_prediction)
    final_prediction=result_str
    return render_template('predict.html', prediction_text=final_prediction)



if __name__ == "__main__":
    flask_app.run(debug=True)