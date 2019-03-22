# =============================================================================
# Import libraries
# =============================================================================

import re
import os

from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile


def set_boundary(in_dict, path):
    boundary_dict = ParsedParameterFile(path)
    bf_dict = boundary_dict['boundaryField']
    for bf_key in in_dict:
        if bf_key in bf_dict:
            patch_dict = bf_dict[bf_key]
            for val_key in patch_dict:
                if val_key in in_dict[bf_key]:
                    patch_dict[val_key] = in_dict[bf_key][val_key]
    boundary_dict.writeFile()


def set_transport_props(in_dict, path):
    transport_dict = ParsedParameterFile(path)
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


def set_foam_subdicts(main_dict, in_dicts):
    if isinstance(in_dicts, (list, tuple)):
        for sub_dict in in_dicts:
            main_dict = set_foam_subdict(main_dict, sub_dict)
    elif isinstance(in_dicts, dict):
        main_dict = set_foam_subdict(main_dict, in_dicts)
    else:
        raise TypeError('Input "in_dicts" must either be a list or tuple of '
                        'dicts or a single dict')
    return main_dict


def set_foam_subdict(main_dict, in_dict):
    if isinstance(in_dict, dict):
        try:
            this_dict = main_dict[in_dict['name']]
            for key in in_dict:
                if key in this_dict:
                    this_dict[key][-1] = in_dict[key]
        except KeyError:
            print('Foam sub-dict with name ' + in_dict['name']
                  + ' not found in ' + main_dict.name)
    else:
        raise TypeError('Input "in_dict" must be a dictionary')
    return main_dict


def set_graphs(case_dir, bounds, profile_positions):
    graph_names = []
    control_dict = \
        ParsedParameterFile(os.path.join(case_dir, 'system/controlDict'))
    for key in control_dict['functions']:
        func_str = control_dict['functions'][key]
        if 'Graph' in func_str:
            graph_name = re.search('"(.*)"', func_str).group(1)
            graph_names.append(graph_name)

    for i in range(len(profile_positions)):
        graph_dict = \
            ParsedParameterFile(os.path.join(case_dir,
                                             'system/' + str(graph_names[i])))
        for key in graph_dict:
            if 'start' in graph_dict[key]:
                graph_sub_dict = graph_dict[key]
                graph_sub_dict['start'] = \
                    '(%f %f 0)' % (bounds[1][0], profile_positions[i])
                graph_sub_dict['end'] = \
                    '(%f %f 0)' % (bounds[1][1], profile_positions[i])
        graph_dict.writeFile()
