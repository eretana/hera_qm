# -*- coding: utf-8 -*-
# Copyright (c) 2019 the HERA Project
# Licensed under the MIT License
"""Tests for metrics_io module."""

import pytest
import numpy as np
import os
import h5py
import pyuvdata.tests as uvtest
from hera_qm.data import DATA_PATH
from hera_qm import metrics_io
import hera_qm.tests as qmtest
from hera_qm.version import hera_qm_version_str


class dummy_class(object):
    """A dummy class to break h5py object types."""

    def __init__(self):
        """Create blank object."""
        pass


def test_reds_list_to_dict_type():
    """Test type returned is dict."""
    test_list = [(1, 2), (3, 4)]
    test_dict = metrics_io._reds_list_to_dict(test_list)
    assert isinstance(test_dict, dict)


def test_reds_dict_to_list_type():
    """Test type returned is list."""
    test_dict = {'0': [[0, 1], [1, 2]], '1': [[0, 2], [1, 3]]}
    test_list = metrics_io._reds_dict_to_list(test_dict)
    assert isinstance(test_list, list)


def test_reds_list_to_dict_to_list_unchanged():
    """Test list to dict to list conversion does not change input."""
    test_list = [[(1, 2), (3, 4)]]
    test_dict = metrics_io._reds_list_to_dict(test_list)
    test_list2 = metrics_io._reds_dict_to_list(test_dict)
    assert np.allclose(test_list, test_list2)


def test_recursive_error_for_object_arrays():
    """Test a TypeError is raised if dictionary items are np.arrays of objects."""
    test_file = os.path.join(DATA_PATH, 'test_output', 'test.h5')
    path = '/'
    bad_dict = {'1': np.array(['123', 1, np.pi], dtype='object')}
    with h5py.File(test_file, 'w') as h5_test:
        pytest.raises(TypeError, metrics_io._recursively_save_dict_to_group,
                      h5_test, path, bad_dict)
    os.remove(test_file)


def test_recursive_error_for_dict_of_object():
    """Test a TypeError is raised if dictionary items are objects."""
    test_file = os.path.join(DATA_PATH, 'test_output', 'test.h5')
    path = '/'
    bad_dict = {'0': dummy_class()}
    with h5py.File(test_file, 'w') as h5_test:
        pytest.raises(TypeError, metrics_io._recursively_save_dict_to_group,
                      h5_test, path, bad_dict)
    os.remove(test_file)


def test_recursive_error_for_object_in_nested_dict():
    """Test TypeError is raised if object is nested in dict."""
    test_file = os.path.join(DATA_PATH, 'test_output', 'test.h5')
    path = '/'
    bad_dict = {'0': {'0.0': dummy_class()}}
    with h5py.File(test_file, 'w') as h5_test:
        pytest.raises(TypeError, metrics_io._recursively_save_dict_to_group,
                      h5_test, path, bad_dict)
    os.remove(test_file)


def test_recursive_adds_numpy_array_to_h5file():
    """Test that proper numpy arrays are added to h5file."""
    test_file = os.path.join(DATA_PATH, 'test_output', 'test.h5')
    test_array = np.arange(10)
    path = '/'
    good_dict = {'0': test_array}
    with h5py.File(test_file, 'w') as h5_test:
        metrics_io._recursively_save_dict_to_group(h5_test, path, good_dict)

        assert np.allclose(test_array, h5_test["0"][()])
    os.remove(test_file)


def test_recursive_adds_nested_numpy_array_to_h5file():
    """Test that a numpy array nested in a dict is added to h5file."""
    test_file = os.path.join(DATA_PATH, 'test_output', 'test.h5')
    test_array = np.arange(10)
    path = '/'
    good_dict = {'0': {1: test_array}}
    with h5py.File(test_file, 'w') as h5_test:
        metrics_io._recursively_save_dict_to_group(h5_test, path, good_dict)
        assert np.allclose(test_array, h5_test["0/1"][()])
    os.remove(test_file)


def test_recursive_adds_scalar_to_h5file():
    """Test that a scalar type is added to h5file."""
    test_file = os.path.join(DATA_PATH, 'test_output', 'test.h5')
    test_scalar = 'hello world'
    path = '/'
    good_dict = {'filestem': test_scalar}
    with h5py.File(test_file, 'w') as h5_test:
        metrics_io._recursively_save_dict_to_group(h5_test, path, good_dict)
        # we convert to np.string_ types so use that to compare
        assert np.string_(test_scalar), h5_test["filestem"][()]
    os.remove(test_file)


def test_recursive_adds_nested_scalar_to_h5file():
    """Test that a scalar nested in a dict is added to h5file."""
    test_file = os.path.join(DATA_PATH, 'test_output', 'test.h5')
    test_scalar = 'hello world'
    good_dict = {'0': {'filestem': test_scalar}}
    path = '/'
    with h5py.File(test_file, 'w') as h5_test:
        metrics_io._recursively_save_dict_to_group(h5_test, path, good_dict)

        assert np.string_(test_scalar), h5_test["0/filestem"][()]
    os.remove(test_file)


def test_write_metric_error_for_existing_file():
    """Test an error is raised if an existing file is given and overwrite=False."""
    test_file = os.path.join(DATA_PATH, 'test_output', 'test.h5')
    with open(test_file, 'w') as f:
        pass
    pytest.raises(IOError, metrics_io.write_metric_file, test_file, {})
    os.remove(test_file)


def test_write_metric_error_for_existing_file_no_appellation():
    """Test an error is raised if an existing file is given with no appelation and overwrite=False."""
    test_file = os.path.join(DATA_PATH, 'test_output', 'test')
    with open(test_file + '.hdf5', 'w') as f:
        pass
    pytest.raises(IOError, metrics_io.write_metric_file, test_file, {})
    os.remove(test_file + '.hdf5')


def test_write_metric_succeeds_for_existing_file_no_appellation_overwrite():
    """Test an write is successful if an existing file is given and overwrite=True."""
    test_file = os.path.join(DATA_PATH, 'test_output', 'test')
    with open(test_file + '.hdf5', 'w') as f:
        pass
    metrics_io.write_metric_file(test_file, {}, True)
    assert os.path.exists(test_file + '.hdf5')
    os.remove(test_file + '.hdf5')


def test_write_metric_file_hdf5():
    """Test that correct hdf5 structure created from write_metric_file."""
    test_file = os.path.join(DATA_PATH, 'test_output', 'test.h5')
    test_scalar = 'hello world'
    test_array = np.arange(10)
    test_dict = {'filestem': test_scalar, 1: {'filestem': test_scalar, '1': test_array}}
    path = '/'
    metrics_io.write_metric_file(test_file, test_dict)

    with h5py.File(test_file, 'r') as test_h5:
        assert np.string_(test_scalar) == test_h5["/Metrics/filestem"][()]
        assert np.string_(test_scalar) == test_h5["/Metrics/1/filestem"][()]
        assert np.allclose(test_array, test_h5["Metrics/1/1"][()])
    os.remove(test_file)


def test_write_metric_file_hdf5_no_appellation_exists():
    """Test hdf5 file created from write_metric_file if no appellation given."""
    test_file = os.path.join(DATA_PATH, 'test_output', 'test')
    test_scalar = 'hello world'
    test_array = np.arange(10)
    test_dict = {'filestem': test_scalar, 1: {'filestem': test_scalar, '1': test_array}}
    path = '/'
    metrics_io.write_metric_file(test_file, test_dict)
    test_file += '.hdf5'
    assert os.path.exists(test_file)
    os.remove(test_file)


def test_write_metric_warning_json():
    """Test the known warning is issued when writing to json."""
    json_file = os.path.join(DATA_PATH, 'test_output', 'test_save.json')
    test_scalar = 'hello world'
    test_array = np.arange(10)
    test_dict = {'filestem': test_scalar, 1: {'filestem': test_scalar, '1': test_array}}
    warn_message = ["JSON-type files can still be written but are no longer "
                    "written by default.\n"
                    "Write to HDF5 format for future compatibility."]
    json_dict = uvtest.checkWarnings(metrics_io.write_metric_file,
                                     [json_file, test_dict],
                                     {'overwrite': True},
                                     category=PendingDeprecationWarning,
                                     nwarnings=1,
                                     message=warn_message)
    assert os.path.exists(json_file)
    os.remove(json_file)


def test_write_metric_warning_pickle():
    """Test the known warning is issued when writing to pickles."""
    pickle_file = os.path.join(DATA_PATH, 'test_output', 'test_save.pkl')
    test_scalar = 'hello world'
    test_array = np.arange(10)
    test_dict = {'filestem': test_scalar, 1: {'filestem': test_scalar, '1': test_array}}
    warn_message = ["Pickle-type files can still be written but are no longer "
                    "written by default.\n"
                    "Write to HDF5 format for future compatibility."]
    pickle_dict = uvtest.checkWarnings(metrics_io.write_metric_file,
                                       [pickle_file, test_dict],
                                       {'overwrite': True},
                                       category=PendingDeprecationWarning,
                                       nwarnings=1,
                                       message=warn_message)
    assert os.path.exists(pickle_file)
    os.remove(pickle_file)


def test_write_then_recursive_load_dict_to_group_no_nested_dicts():
    """Test recursive load can gather dictionary from a group."""
    test_file = os.path.join(DATA_PATH, 'test_output', 'test.h5')
    test_scalar = 'hello world'
    path = '/'
    good_dict = {'filestem': test_scalar, 'history': "this is a test",
                 'version': hera_qm_version_str}
    metrics_io.write_metric_file(test_file, good_dict)
    with h5py.File(test_file, 'r') as h5file:
        read_dict = metrics_io._recursively_load_dict_to_group(h5file, '/Header/')
        read_dict.update(metrics_io._recursively_load_dict_to_group(h5file, '/Metrics/'))
    metrics_io._recursively_validate_dict(read_dict)
    assert qmtest.recursive_compare_dicts(good_dict, read_dict)
    os.remove(test_file)


def test_write_then_recursive_load_dict_to_group_with_nested_dicts():
    """Test recursive load can gather dictionary from a nested group."""
    test_file = os.path.join(DATA_PATH, 'test_output', 'test.h5')
    test_scalar = 'hello world'
    path = '/'
    good_dict = {'filestem': test_scalar, 'history': "this is a test",
                 'version': hera_qm_version_str, '1': {'filestem': test_scalar}}
    metrics_io.write_metric_file(test_file, good_dict)
    with h5py.File(test_file, 'r') as h5file:
        read_dict = metrics_io._recursively_load_dict_to_group(h5file, '/Header/')
        read_dict.update(metrics_io._recursively_load_dict_to_group(h5file, '/Metrics/'))
    metrics_io._recursively_validate_dict(read_dict)
    for key in good_dict:
        if isinstance(good_dict[key], dict):
            assert qmtest.recursive_compare_dicts(good_dict[key], read_dict[key])
        else:
            assert good_dict[key] == read_dict[key]
    os.remove(test_file)


def test_recursive_load_error_if_object_not_group_or_dataset():
    """Test the recursively loader errors if given HDF5 with non hdf5-object."""
    test_scalar = 'hello world'
    good_dict = {'0': {'1': {'filestem': test_scalar}}}
    pytest.raises(TypeError, metrics_io._recursively_load_dict_to_group,
                  good_dict, '0')


def test_write_then_load_metric_file_hdf5():
    """Test loaded in map is same as written one from hdf5."""
    test_file = os.path.join(DATA_PATH, 'test_output', 'test.h5')
    test_scalar = 'hello world'
    path = '/'
    good_dict = {'filestem': test_scalar, 'history': "this is a test",
                 'version': hera_qm_version_str, 'all_metrics': {'filestem': test_scalar}}
    metrics_io.write_metric_file(test_file, good_dict)
    read_dict = metrics_io.load_metric_file(test_file)
    for key in good_dict:
        if isinstance(good_dict[key], dict):
            assert qmtest.recursive_compare_dicts(good_dict[key], read_dict[key])
        else:
            assert good_dict[key] == read_dict[key]
    os.remove(test_file)


def test_write_then_load_metric_warning_json():
    """Test the known warning is issued when writing then reading json."""
    json_file = os.path.join(DATA_PATH, 'test_output', 'test_save.json')
    test_dict = {'history': 'Test case', 'version': '0.0.0',
                 'dead_ant_z_cut': 5}
    warn_message = ["JSON-type files can still be written but are no longer "
                    "written by default.\n"
                    "Write to HDF5 format for future compatibility.", ]
    uvtest.checkWarnings(metrics_io.write_metric_file,
                         [json_file, test_dict],
                         {'overwrite': True},
                         category=PendingDeprecationWarning, nwarnings=1,
                         message=warn_message)
    assert os.path.exists(json_file)
    # output_json = metrics_io.write_metric_file(json_file, test_dict)
    warn_message = ["JSON-type files can still be read but are no longer "
                    "written by default.\n"]
    json_dict = uvtest.checkWarnings(metrics_io.load_metric_file,
                                     func_args=[json_file],
                                     category=[PendingDeprecationWarning],
                                     nwarnings=1,
                                     message=warn_message)
    # This function recursively walks dictionary and compares
    # data types together with assert or np.allclose
    qmtest.recursive_compare_dicts(test_dict, json_dict)
    os.remove(json_file)


def test_write_then_load_metric_warning_pickle():
    """Test the known warning is issued when writing then reading pickles."""
    pickle_file = os.path.join(DATA_PATH, 'test_output', 'test_save.pkl')
    test_dict = {'history': 'Test case', 'version': '0.0.0',
                 'dead_ant_z_cut': 5}
    warn_message = ["Pickle-type files can still be written but are no longer "
                    "written by default.\n"
                    "Write to HDF5 format for future compatibility.", ]
    uvtest.checkWarnings(metrics_io.write_metric_file,
                         [pickle_file, test_dict],
                         {'overwrite': True},
                         category=PendingDeprecationWarning, nwarnings=1,
                         message=warn_message)
    assert os.path.exists(pickle_file)
    # output_json = metrics_io.write_metric_file(json_file, test_dict)
    warn_message = ["Pickle-type files can still be read but are no longer "
                    "written by default.\n"]
    pickle_dict = uvtest.checkWarnings(metrics_io.load_metric_file,
                                       func_args=[pickle_file],
                                       category=[PendingDeprecationWarning],
                                       nwarnings=1,
                                       message=warn_message)
    # This function recursively walks dictionary and compares
    # data types together with assert or np.allclose
    assert qmtest.recursive_compare_dicts(test_dict, pickle_dict)
    os.remove(pickle_file)


def test_read_write_old_firstcal_json_files():
    """Test the old firstcal json storage can be read and written to hdf5."""
    json_infile = os.path.join(DATA_PATH, 'example_firstcal_metrics.json')
    test_file = os.path.join(DATA_PATH, 'test_output',
                             'test_firstcal_json_to_hdf5.h5')
    warn_message = ["JSON-type files can still be read but are no longer "
                    "written by default.\n"
                    "Write to HDF5 format for future compatibility.", ]
    test_metrics = uvtest.checkWarnings(metrics_io.load_metric_file,
                                        func_args=[json_infile],
                                        category=PendingDeprecationWarning,
                                        nwarnings=1,
                                        message=warn_message)
    metrics_io.write_metric_file(test_file, test_metrics, overwrite=True)
    test_metrics_in = metrics_io.load_metric_file(test_file)

    test_metrics.pop('history', None)
    test_metrics_in.pop('history', None)

    # This function recursively walks dictionary and compares
    # data types together with assert  or np.allclose
    assert qmtest.recursive_compare_dicts(test_metrics, test_metrics_in)
    assert os.path.exists(test_file)
    os.remove(test_file)


def test_read_write_old_omnical_json_files():
    """Test the old omnical json storage can be read and written to hdf5."""
    json_infile = os.path.join(DATA_PATH, 'example_omnical_metrics.json')
    test_file = os.path.join(DATA_PATH, 'test_output',
                             'test_omnical_json_to_hdf5.h5')
    warn_message = ["JSON-type files can still be read but are no longer "
                    "written by default.\n"
                    "Write to HDF5 format for future compatibility.", ]
    test_metrics = uvtest.checkWarnings(metrics_io.load_metric_file,
                                        func_args=[json_infile],
                                        category=PendingDeprecationWarning,
                                        nwarnings=1,
                                        message=warn_message)
    metrics_io.write_metric_file(test_file, test_metrics, overwrite=True)
    test_metrics_in = metrics_io.load_metric_file(test_file)

    # The written hdf5 may have these keys that differ by design
    # so ignore them.
    test_metrics.pop('history', None)
    test_metrics.pop('version', None)
    test_metrics_in.pop('history', None)
    test_metrics_in.pop('version', None)

    # This function recursively walks dictionary and compares
    # data types together with nt.assert_type_equal or np.allclose
    assert qmtest.recursive_compare_dicts(test_metrics, test_metrics_in)
    assert os.path.exists(test_file)
    os.remove(test_file)


def test_read_write_new_ant_json_files():
    """Test the new ant_metric json storage can be read and written to hdf5."""
    json_infile = os.path.join(DATA_PATH, 'example_ant_metrics.json')
    test_file = os.path.join(DATA_PATH, 'test_output',
                             'test_ant_json_to_hdf5.h5')
    warn_message = ["JSON-type files can still be read but are no longer "
                    "written by default.\n"
                    "Write to HDF5 format for future compatibility.", ]
    test_metrics = uvtest.checkWarnings(metrics_io.load_metric_file,
                                        func_args=[json_infile],
                                        category=PendingDeprecationWarning,
                                        nwarnings=1,
                                        message=warn_message)
    metrics_io.write_metric_file(test_file, test_metrics, overwrite=True)
    test_metrics_in = metrics_io.load_metric_file(test_file)

    # The written hdf5 may have these keys that differ by design
    # so ignore them.
    test_metrics.pop('history', None)
    test_metrics.pop('version', None)
    test_metrics_in.pop('history', None)
    test_metrics_in.pop('version', None)

    # This function recursively walks dictionary and compares
    # data types together with nt.assert_type_equal or np.allclose
    assert qmtest.recursive_compare_dicts(test_metrics, test_metrics_in)
    assert os.path.exists(test_file)
    os.remove(test_file)


def test_read_old_all_string_ant_json_files():
    """Test the new ant_metric json storage can be read and written to hdf5."""
    old_json_infile = os.path.join(DATA_PATH, 'example_ant_metrics_all_string.json')
    new_json_infile = os.path.join(DATA_PATH, 'example_ant_metrics.json')
    warn_message = ["JSON-type files can still be read but are no longer "
                    "written by default.\n"
                    "Write to HDF5 format for future compatibility.", ]
    test_metrics_old = uvtest.checkWarnings(metrics_io.load_metric_file,
                                            func_args=[old_json_infile],
                                            category=PendingDeprecationWarning,
                                            nwarnings=1,
                                            message=warn_message)
    test_metrics_new = uvtest.checkWarnings(metrics_io.load_metric_file,
                                            func_args=[new_json_infile],
                                            category=PendingDeprecationWarning,
                                            nwarnings=1,
                                            message=warn_message)
    # The written hdf5 may have these keys that differ by design
    # so ignore them.
    test_metrics_old.pop('history', None)
    test_metrics_old.pop('version', None)
    test_metrics_new.pop('history', None)
    test_metrics_new.pop('version', None)

    # This function recursively walks dictionary and compares
    # data types together with nt.assert_type_equal or np.allclose
    assert qmtest.recursive_compare_dicts(test_metrics_new, test_metrics_old)


def test_process_ex_ants_empty():
    ex_ants = ''
    xants = metrics_io.process_ex_ants(ex_ants=ex_ants)
    assert xants == []


def test_process_ex_ants_string():
    ex_ants = '0,1,2'
    xants = metrics_io.process_ex_ants(ex_ants=ex_ants)
    assert xants == [0, 1, 2]


def test_process_ex_ants_bad_string():
    ex_ants = '0,obvious_error'
    pytest.raises(AssertionError, metrics_io.process_ex_ants, ex_ants=ex_ants)


def test_process_ex_ants_string_and_file():
    ex_ants = '0,1'
    met_file = os.path.join(DATA_PATH, 'example_ant_metrics.hdf5')
    xants = metrics_io.process_ex_ants(ex_ants=ex_ants, metrics_file=met_file)
    assert xants == [0, 1, 81]


def test_boolean_read_write_json():
    """Test a Boolean type is preserved in read write loop: json."""
    test_file = os.path.join(DATA_PATH, 'test_output', 'test_bool.json')
    test_bool = True
    test_dict = {'good_sol': test_bool}
    warn_message = ["JSON-type files can still be written but are no longer "
                    "written by default.\n"
                    "Write to HDF5 format for future compatibility.", ]
    uvtest.checkWarnings(metrics_io.write_metric_file,
                         [test_file, test_dict],
                         {"overwrite": True},
                         category=PendingDeprecationWarning, nwarnings=1,
                         message=warn_message)
    warn_message = ["JSON-type files can still be read but are no longer "
                    "written by default.\n"]
    json_dict = uvtest.checkWarnings(metrics_io.load_metric_file,
                                     func_args=[test_file],
                                     category=[PendingDeprecationWarning],
                                     nwarnings=1,
                                     message=warn_message)
    assert test_dict['good_sol'] == json_dict['good_sol']
    assert isinstance(json_dict['good_sol'], (np.bool_, bool))
    os.remove(test_file)


def test_boolean_read_write_pickle():
    """Test a Boolean type is preserved in read write loop: pickle."""
    test_file = os.path.join(DATA_PATH, 'test_output', 'test_bool.pkl')
    test_bool = True
    test_dict = {'good_sol': test_bool}
    warn_message = ["Pickle-type files can still be written but are no longer "
                    "written by default.\n"
                    "Write to HDF5 format for future compatibility.", ]
    uvtest.checkWarnings(metrics_io.write_metric_file,
                         [test_file, test_dict],
                         category=PendingDeprecationWarning, nwarnings=1,
                         message=warn_message)
    warn_message = ["Pickle-type files can still be read but are no longer "
                    "written by default.\n"]
    input_dict = uvtest.checkWarnings(metrics_io.load_metric_file,
                                      func_args=[test_file],
                                      category=[PendingDeprecationWarning],
                                      nwarnings=1,
                                      message=warn_message)
    assert test_dict['good_sol'] == input_dict['good_sol']
    assert isinstance(input_dict['good_sol'], (np.bool_, bool))
    os.remove(test_file)


def test_boolean_read_write_hdf5():
    """Test a Boolean type is preserved in read write loop: hdf5."""
    test_file = os.path.join(DATA_PATH, 'test_output', 'test_bool.h5')
    test_bool = True
    test_dict = {'good_sol': test_bool}

    metrics_io.write_metric_file(test_file, test_dict, overwrite=True)
    input_dict = metrics_io.load_metric_file(test_file)

    assert test_dict['good_sol'], input_dict['good_sol']
    assert isinstance(input_dict['good_sol'], (np.bool_, bool))
    os.remove(test_file)
