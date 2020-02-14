from flask import Flask, render_template, redirect, url_for,request
from flask import make_response, jsonify
from flask_cors import CORS
from data_manager import create_datasets
from flowline_data_manager import *
from flow_integrator import FlowIntegrator
import pandas as pd
import numpy as np
from pyproj import Proj
app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "hi"
@app.route("/index")

@app.route('/get_flowline', methods=['POST'])
def get_flowline():
    if request.method == 'POST':

        data = request.json
       
        xs = data['x']
        ys = data['y']

        return_data = {}
        for i in range(len(xs)):
            x = float(xs[i])
            y = float(ys[i])
            coords = flow_integrator.integrate_flowline(x, y, resolution = 2.5)
            return_data[i] = coords[:,::-1].tolist()
     
        return return_data


@app.route('/plot_flowline', methods=['POST'])
def plot_flowline():
    if request.method == 'POST':
        data = request.json
        avg_data = flowline_data_manager.get_flowline_data(data)['avg_data']
        L = avg_data['L']
        return_data = {}

        for field in ['smb', 't2m', 'surface','thickness', 'bed','bhat', 'width']:
            return_field = pd.DataFrame(np.c_[L, avg_data[field]], columns = ['x', 'y'])
            return_data[field] = return_field.to_dict(orient = 'records')
        
        return return_data


@app.route('/get_flowline_data', methods=['POST'])
def get_flowline_data():
    if request.method == 'POST':
        data = request.json
        return_data = flowline_data_manager.get_flowline_data(data)

        return return_data

if __name__ == "__main__":
    datasets = create_datasets()
    flowline_data_manager = FlowlineDataManager(datasets)
    flow_integrator = FlowIntegrator(datasets['VX'], datasets['VY'])
    app.run(debug = True)
