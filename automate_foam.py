#!/usr/bin/env python

# =============================================================================
# Import libraries 
# =============================================================================
import sys
sys.path.append('/home/simulation/PyCharm/PycharmProjects/AutomateFoam')
import os
import numpy as np
import random
from src import global_functions as gf, foam_setup as fs, result_data as rd
import matplotlib.pyplot as plt
import datetime
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile

np.set_printoptions(threshold=np.nan)

# Number of simulation runs
simulation_number = 1 

# Set directories
case_dir = '/media/Daten_Raid/OpenFOAM/simulation-2.3.0/UZB_61602/2D_thixoModel'
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

velocity_dict = {'inlet': {'value': 'uniform (%f 0 0) ' % velocity_in}}


input_dict = {
                'wallCoeffs':
                {
                    'alpha': 6e-2,
                    'beta': 1.0,
                    'exponent': 2.0
                },
                'RousselCoeffs':
                {
                    'tau0': 10e-4
                },
                'HerschelBulkleyExtendedCoeffs':
                {
                    'tau0': 0.0e-4,
                    'k': 5e-5,
                    'n': 0.6,
                    'nuInf': 5e-6
                },
                'FeierabendStructureCoeffs':
                {
                    'theta': 10.0,
                    'alpha': 5.0,
                    'a': 0.0,
                    'b': 1.0
                }
             }

# Set graph data for OpenFOAM post processing
fs.set_graphs(case_dir, bounds, x_pos_profiles)

# Parameter variation loop
for i in range(simulation_number):

    param_dict = {}

    for key in input_dict:
        sub_dict = input_dict[key]
        param_dict[key] = {}
        for skey in sub_dict:
            if isinstance(sub_dict[skey], (list, tuple)):
                param_dict[key][skey] = \
                    np.exp(random.uniform(np.log(sub_dict[skey][0]),
                                          np.log(sub_dict[skey][1])))
            else:
                param_dict[key][skey] = sub_dict[skey]

    boundary_dict = ParsedParameterFile(velocity_dict['name'])
    for key in boundary_dict['boundaryField']:
        if key == 'upperInletWall':
            velocity_dict[key] = boundary_dict['boundaryField'][key]
            velocity_dict[key]['alpha'] = param_dict['wallCoeffs']['alpha']*1.0
            velocity_dict[key]['beta'] = param_dict['wallCoeffs']['beta']
            velocity_dict[key]['exponent'] = \
                param_dict['wallCoeffs']['exponent']
        elif boundary_dict['boundaryField'][key]['type'] \
                == 'thixoShearStressSlipVelocity':
            velocity_dict[key] = boundary_dict['boundaryField'][key]
            velocity_dict[key]['alpha'] = param_dict['wallCoeffs']['alpha']
            velocity_dict[key]['beta'] = param_dict['wallCoeffs']['beta']
            velocity_dict[key]['exponent'] = \
                param_dict['wallCoeffs']['exponent']

    # Set up foam dictionary files
    fs.set_boundary(velocity_dict, os.path.join(case_dir, '0.org/U'))

    transport_dict = ParsedParameterFile('constant/transportProperties')
    dict_list = []
    for name in param_dict:
        sub_dict = dict()
        sub_dict.update(param_dict[name])
        sub_dict['name'] = name
        dict_list.append(sub_dict)
    transport_dict = fs.set_foam_subdicts(transport_dict, dict_list)
    transport_dict.writeFile()
    # fs.set_transport_props(param_dict)

    gf.run_sim(case_dir)

    sep = '\t'

    sim_data = rd.SimulationData(case_dir, meas_data)
    ts = str(datetime.datetime.now()).split('.')[0].split(' ')
    run_name = str(i) + sep + ts[0] + sep + ts[1]

    if sim_data.x_vel_prof:
        fig = gf.plot_profiles(meas_data, sim_data)
        error = gf.calculate_error(meas_data, sim_data)
        # info_dict = {}
        # info_dict.update(param_dict)
        # info_dict['error'] = error
        info = ''
        for key in param_dict:
            info += str(key) + ': ' + str(param_dict[key]) + '\n'
        info += 'error: %6.2f\n' % error
        fig.text(0.1, 0.001, info, horizontalalignment='left', fontsize='8.0')
        plt.savefig('results/' + run_name, bbox_inches='tight')
        run_name += sep + 'converged' + sep + 'error: %6.2f' % error
    else:
        run_name += sep + 'diverged'

    run_name += sep + str(param_dict)
    run_name += '\n'

    with open('results/runs.txt', 'a') as f:
        f.write(run_name)
