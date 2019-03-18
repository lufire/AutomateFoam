#!/usr/bin/env python

# =============================================================================
# Import libraries 
# =============================================================================
import os
import result_data as rd
import numpy as np
import random
import global_functions as gf
import foam_setup as fs
import matplotlib.pyplot as plt
import datetime
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile

np.set_printoptions(threshold=np.nan)

# Number of simulation runs
simulation_number = 1 

# Set directories
case_dir = '/media/Daten_Raid/OpenFOAM/Feierabend/UZB_61602/2D_thixoModel'
meas_path = os.path.join(case_dir, '../measurement_data/slurry/meas_data.pk')

os.chdir(case_dir)

# Specify flow geometry
y_width = 15e-3
z_depth = 47e-3
x_width_in = 2e-3
x_pos_profiles = (2.5e-3, 5.0e-3, 7.5e-3, 10.0e-3, 15.0e-3)

bounds = ((0.0, 20e-3),
          (0.0, 15e-3))

vel_factor = 1.2
meas_data = rd.MeasurementData(meas_path, x_pos_profiles, bounds)

velocity = np.nansum(meas_data.x_vel_prof[-1], axis=-1) / len(meas_data.x_grid)
flow_rate = velocity * y_width * z_depth
velocity_in = velocity * y_width / x_width_in * vel_factor

velocity_dict = {'name': '0.org/U',
                 'inlet': {'value': 'uniform (%f 0 0) ' % velocity_in}}

# Set variable input parameters
slip_dict = {'factor': 1e-3,
             'exponent': 1.3}

# deSouzaMendesThompson_dict = {'a': 1e-3,
#                               'b': 10,
#                               'teq': 0.5,
#                               'G0': 1.3,
#                               'm': 1.0,
#                               'nuInf': 1e-5,
#                               'tauY': 1e-3,
#                               'tauYD': 1e-3,
#                               'K': 1e-4,
#                               'gammaYD': 1e-4}

# bounds_dict = {
#                'factor': (5e-6, 5e-3),
#                'exponent': (1.0, 4.2),
#                'tau0': (5e-5, 5e-3),
#                'nuInf': (1e-6, 1e-3),
#                'k': (1e-6, 1e-3),
#                'theta': (0.1, 1000.0),
#                'alpha': (0.01, 100.0)
#               }

bounds_dict = {
               'factor':  1.0e-1,
               'exponent': 3.0,
               'tau0': 5.0e-4,
               'nuInf': 2e-6,
               'k': 3e-5,
               'theta': 10.0,
               'alpha': 5.0,
               'a': 0.2,
               'b': 0.2,
              }

# bounds_dict = {'factor': (1e-4, 1e7),
#                'exponent': (0.5, 5.0),
#                'a': (0.2, 2.0),
#                'b': (0.2, 2.0),
#                'teq': (0.1, 1000.0),
#                'G0': (1.0, 1000.0),
#                'm': (0.5, 1.5),
#                'nuInf': (1e-6, 1e-3),
#                'tauY': (5e-4, 5e-2),
#                'tauYD': (5e-4, 5e-2),
#                'K': (1e-6, 1e-3),
#                'gammaYD': (1e-5, 1e-2)}

Coussot_dict = {'nu': 1e-3,
                'theta': 10,
                'alpha': 0.5,
                'n': 1.3}

# transport_dict = deSouzaMendesThompson_dict
# 
# param_dict = {}
# param_dict.update(slip_dict)
# param_dict.update(transport_dict)

# bounds_dict = {'factor': [1e-4, 1e7],
#                'exponent': [0.5, 5.0],
#                'nu': [1e-6, 1e-2],
#                'theta': [0.1, 1000.0],
#                'alpha': [0.01, 100.0],
#                'n': [0.5, 5.0]}

# Set graph data for OpenFOAM post processing
fs.set_graphs(bounds, x_pos_profiles)

# Parameter variation loop
for i in range(simulation_number):

    param_dict = {}
    # Random parameter generation
    for key in bounds_dict:
        if isinstance(bounds_dict[key], (list, tuple)):
            param_dict[key] = np.exp(random.uniform(np.log(bounds_dict[key][0]), np.log(bounds_dict[key][1])))
        else:
            param_dict[key] = bounds_dict[key]

    boundary_dict = ParsedParameterFile(velocity_dict['name'])
    for key in boundary_dict['boundaryField']:
        if key == 'upperInletWall':
            velocity_dict[key] = {'factor': param_dict['factor']*1.0}
            velocity_dict[key] = {'exponent': param_dict['exponent']}
        elif boundary_dict['boundaryField'][key]['type'] == 'shearStressSlipVelocity':
            velocity_dict[key] = boundary_dict['boundaryField'][key]
            velocity_dict[key]['factor'] = param_dict['factor']
            velocity_dict[key]['exponent'] = param_dict['exponent']

    # Set up foam dictionary files
    fs.set_boundary(velocity_dict)
    fs.set_transport_props(param_dict)

    gf.run_sim()

    sim_data = rd.SimulationData(case_dir, meas_data)
    ts = str(datetime.datetime.now()).split('.')[0].split(' ')
    run_name = str(i) + ', ' + ts[0] + ', ' + ts[1]

    if sim_data.x_vel_prof:
        fig = gf.plot_profiles(meas_data, sim_data)
        error = gf.calculate_error(meas_data, sim_data)
        info_dict = {}
        info_dict.update(param_dict)
        info_dict['error'] = error
        fig = gf.add_info(fig, info_dict)
        plt.savefig('results/' + run_name, bbox_inches='tight')
        run_name += ', converged, error: %6.2f' % error
    else:
        run_name += ',  diverged'

    for key in param_dict:
        run_name += ', ' + str(key) + ': ' + '%.2E' % param_dict[key]
    run_name += '\n'
    with open('results/runs.txt', 'a') as f:
        f.write(run_name)
