# =============================================================================
# Import libraries
# =============================================================================

import re

from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile


def set_inlet_velocity(inlet_name, velocity):
    velocity_dict = ParsedParameterFile('0.org/U')
    bf_dict = velocity_dict['boundaryField']
    inlet_dict = bf_dict[inlet_name]
    if inlet_dict['type'] == 'fixedValue':
        inlet_dict['value'] = 'uniform (%f 0 0)' % velocity


def set_slip_coeffs(factor, exponent):
    velocity_dict = ParsedParameterFile('0.org/U')
    bf_dict = velocity_dict['boundaryField']
    for key in bf_dict:
        if bf_dict[key]['type'] == 'shearStressSlipVelocity':
            bf_dict[key]['factor'] = factor
            bf_dict[key]['exponent'] = exponent


def set_boundary(in_dict):
    boundary_dict = ParsedParameterFile(in_dict['name'])
    bf_dict = boundary_dict['boundaryField']
    for bf_key in in_dict:
        if bf_key in bf_dict:
            patch_dict = bf_dict[bf_key]
            for val_key in patch_dict:
                if val_key in in_dict[bf_key]:
                    patch_dict[val_key] = in_dict[bf_key][val_key]
    boundary_dict.writeFile()


def set_transport_props(in_dict):
    transport_dict = ParsedParameterFile('constant/transportProperties')
    visco_model = transport_dict['transportModel']
    for key in in_dict:
        if key in transport_dict:
            transport_dict[key][-1] = in_dict[key]
    try:
        visco_dict = transport_dict[visco_model + 'Coeffs']
        for key in in_dict:
            if key in visco_dict:
                visco_dict[key][-1] = in_dict[key]
    except KeyError:
        if visco_model != 'Newtonian':
            print('No dictionary for transport model found')
    try:
        rheo_model = transport_dict['rheologyModel']
        rheo_dict = transport_dict[rheo_model + 'Coeffs']
        base_rheo_dict = transport_dict['rheologyCoeffs']
        for key in in_dict:
            if key in rheo_dict:
                rheo_dict[key][-1] = in_dict[key]
        for key in in_dict:
            if key in base_rheo_dict:
                base_rheo_dict[key][-1] = in_dict[key]
    except KeyError:
        print('No rheology model found')

    try:
        structure_model = transport_dict['structureModel']
        structure_dict = transport_dict[structure_model + 'Coeffs']
        for key in in_dict:
            if key in structure_dict:
                structure_dict[key][-1] = in_dict[key]
    except KeyError:
        print('No structure model found')
    transport_dict.writeFile()


def set_graphs(bounds, profile_positions):
    graph_names = []
    control_dict = ParsedParameterFile('system/controlDict')
    for key in control_dict['functions']:
        func_str = control_dict['functions'][key]
        if 'Graph' in func_str:
            graph_name = re.search('"(.*)"', func_str).group(1)
            graph_names.append(graph_name)

    for i in range(len(profile_positions)):
        graph_dict = ParsedParameterFile('system/' + str(graph_names[i]))
        for key in graph_dict:
            if 'start' in graph_dict[key]:
                graph_sub_dict = graph_dict[key]
                graph_sub_dict['start'] = '(%f %f 0)' % (bounds[1][0], profile_positions[i])
                graph_sub_dict['end'] = '(%f %f 0)' % (bounds[1][1], profile_positions[i])
        graph_dict.writeFile()
