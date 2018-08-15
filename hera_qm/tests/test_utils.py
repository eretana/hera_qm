# -*- coding: utf-8 -*-
# Copyright (c) 2018 the HERA Project
# Licensed under the MIT License

import nose.tools as nt
import os
import pyuvdata.tests as uvtest
from pyuvdata import UVCal
from pyuvdata import UVData
from hera_qm import utils
from hera_qm.data import DATA_PATH
from hera_qm.ant_metrics import get_ant_metrics_dict
from hera_qm.firstcal_metrics import get_firstcal_metrics_dict
from hera_qm.omnical_metrics import get_omnical_metrics_dict
from hera_qm.utils import get_metrics_dict
import numpy as np


def test_get_pol():
    filename = 'zen.2457698.40355.xx.HH.uvcA'
    nt.assert_equal(utils.get_pol(filename), 'xx')


def test_generate_fullpol_file_list():
    pol_list = ['xx', 'xy', 'yx', 'yy']
    xx_file = os.path.join(DATA_PATH, 'zen.2457698.40355.xx.HH.uvcA')
    xy_file = os.path.join(DATA_PATH, 'zen.2457698.40355.xy.HH.uvcA')
    yx_file = os.path.join(DATA_PATH, 'zen.2457698.40355.yx.HH.uvcA')
    yy_file = os.path.join(DATA_PATH, 'zen.2457698.40355.yy.HH.uvcA')
    file_list = [xx_file, xy_file, yx_file, yy_file]

    # feed in one file at a time
    fullpol_file_list = utils.generate_fullpol_file_list([xx_file], pol_list)
    nt.assert_equal(sorted(fullpol_file_list[0]), sorted(file_list))
    fullpol_file_list = utils.generate_fullpol_file_list([xy_file], pol_list)
    nt.assert_equal(sorted(fullpol_file_list[0]), sorted(file_list))
    fullpol_file_list = utils.generate_fullpol_file_list([yx_file], pol_list)
    nt.assert_equal(sorted(fullpol_file_list[0]), sorted(file_list))
    fullpol_file_list = utils.generate_fullpol_file_list([yy_file], pol_list)
    nt.assert_equal(sorted(fullpol_file_list[0]), sorted(file_list))

    # feed in all four files
    fullpol_file_list = utils.generate_fullpol_file_list(file_list, pol_list)
    nt.assert_equal(sorted(fullpol_file_list[0]), sorted(file_list))

    # checks that we have a list of lists with outer length of 1, and inner length of 4
    nt.assert_equal(len(fullpol_file_list), 1)
    nt.assert_equal(len(fullpol_file_list[0]), 4)

    # try to pass in a file that doesn't have all pols present
    lone_file = os.path.join(DATA_PATH, 'zen.2457698.40355.xx.HH.uvcAA')
    fullpol_file_list = uvtest.checkWarnings(utils.generate_fullpol_file_list,
                                             [[lone_file], pol_list], nwarnings=1,
                                             message='Could not find')
    nt.assert_equal(fullpol_file_list, [])


def test_get_metrics_ArgumentParser():
    # raise error for requesting unknown type of parser
    nt.assert_raises(AssertionError, utils.get_metrics_ArgumentParser, 'fake_method')

    # Test the delay_xrfi_run method
    a = utils.get_metrics_ArgumentParser('delay_xrfi_run')
    # First try defaults - test a few of them
    args = a.parse_args('')
    nt.assert_equal(args.infile_format, 'miriad')
    nt.assert_equal(args.algorithm, 'xrfi_simple')
    nt.assert_equal(args.nsig_dt, 6.0)
    nt.assert_equal(args.px_threshold, 0.2)
    nt.assert_equal(args.filename, None)
    nt.assert_equal(args.tol, 1e-7)
    nt.assert_equal(args.waterfalls, None)
    # try to set something
    args = a.parse_args(['--waterfalls', 'a,g'])
    nt.assert_equal(args.waterfalls, 'a,g')


def test_metrics2mc():
    # test ant metrics
    filename = os.path.join(DATA_PATH, 'example_ant_metrics.json')
    d = utils.metrics2mc(filename, ftype='ant')
    nt.assert_equal(set(d.keys()), set(['ant_metrics', 'array_metrics']))
    nt.assert_equal(len(d['array_metrics']), 0)
    ant_metrics_list = get_ant_metrics_dict()
    nt.assert_equal(set(d['ant_metrics'].keys()), set(ant_metrics_list.keys()))

    # test firstcal metrics
    filename = os.path.join(DATA_PATH, 'example_firstcal_metrics.json')
    d = utils.metrics2mc(filename, ftype='firstcal')
    nt.assert_equal(set(d.keys()), set(['ant_metrics', 'array_metrics']))
    firstcal_array_metrics = set(['firstcal_metrics_agg_std_y',
                                  'firstcal_metrics_good_sol_y',
                                  'firstcal_metrics_max_std_y'])
    nt.assert_equal(set(d['array_metrics'].keys()), firstcal_array_metrics)
    firstcal_metrics_list = get_firstcal_metrics_dict()
    firstcal_ant_metrics = set(firstcal_metrics_list.keys()) - firstcal_array_metrics
    # remove others not in this data file
    firstcal_ant_metrics -= {'firstcal_metrics_good_sol_x', 'firstcal_metrics_good_sol',
                             'firstcal_metrics_agg_std_x', 'firstcal_metrics_agg_std',
                             'firstcal_metrics_max_std_x'}
    nt.assert_equal(set(d['ant_metrics']), firstcal_ant_metrics)

    # test omnical metrics
    filename = os.path.join(DATA_PATH, 'example_omnical_metrics.json')
    d = utils.metrics2mc(filename, ftype='omnical')
    nt.assert_equal(set(d.keys()), set(['ant_metrics', 'array_metrics']))
    om = 'omnical_metrics_'
    nt.assert_equal(set(d['array_metrics'].keys()),
                    set([om + 'chisq_tot_avg_XX', om + 'chisq_good_sol_XX',
                         om + 'chisq_tot_avg_YY', om + 'chisq_good_sol_YY',
                         om + 'ant_phs_std_max_XX', om + 'ant_phs_std_good_sol_XX',
                         om + 'ant_phs_std_max_YY', om + 'ant_phs_std_good_sol_YY']))
    nt.assert_equal(set(d['ant_metrics'].keys()),
                    set([om + 'chisq_ant_avg', om + 'chisq_ant_std', om + 'ant_phs_std']))
    nt.assert_equal(len(d['ant_metrics'][om + 'chisq_ant_avg']), 32)

    # Hit the exceptions
    nt.assert_raises(ValueError, utils.metrics2mc, filename, ftype='foo')


def test_get_metrics_dict():
    ant_metrics_dict = get_ant_metrics_dict()
    firstcal_metrics_dict = get_firstcal_metrics_dict()
    omnical_metrics_dict = get_omnical_metrics_dict()
    metrics_dict = get_metrics_dict()
    for key in ant_metrics_dict:
        nt.assert_equal(ant_metrics_dict[key], metrics_dict[key])
    for key in firstcal_metrics_dict:
        nt.assert_equal(firstcal_metrics_dict[key], metrics_dict[key])
    for key in omnical_metrics_dict:
        nt.assert_equal(omnical_metrics_dict[key], metrics_dict[key])


def test_mean_no_weights():
    # Fake data
    data = np.zeros((50, 25))
    for i in range(data.shape[1]):
        data[:, i] = i * np.ones_like(data[:, i])
    out, wo = utils.mean(data, axis=0, returned=True)
    nt.assert_true(np.array_equal(out, np.arange(data.shape[1])))
    nt.assert_true(np.array_equal(wo, data.shape[0] * np.ones(data.shape[1])))
    out, wo = utils.mean(data, axis=1, returned=True)
    nt.assert_true(np.all(out == np.mean(np.arange(data.shape[1]))))
    nt.assert_true(len(out) == data.shape[0])
    nt.assert_true(np.array_equal(wo, data.shape[1] * np.ones(data.shape[0])))
    out, wo = utils.mean(data, returned=True)
    nt.assert_true(out == np.mean(np.arange(data.shape[1])))
    nt.assert_true(wo == data.size)
    out = utils.mean(data)
    nt.assert_true(out == np.mean(np.arange(data.shape[1])))


def test_mean_weights():
    # Fake data
    data = np.zeros((50, 25))
    for i in range(data.shape[1]):
        data[:, i] = i * np.ones_like(data[:, i]) + 1
    w = 1. / data
    out, wo = utils.mean(data, weights=w, axis=0, returned=True)
    nt.assert_true(np.all(np.isclose(out * wo, data.shape[0])))
    nt.assert_true(np.all(np.isclose(wo, float(data.shape[0]) / (np.arange(data.shape[1]) + 1))))
    out, wo = utils.mean(data, weights=w, axis=1, returned=True)
    nt.assert_true(np.all(np.isclose(out * wo, data.shape[1])))
    nt.assert_true(np.all(np.isclose(wo, np.sum(1. / (np.arange(data.shape[1]) + 1)))))

    # Zero weights
    w = np.ones_like(w)
    w[0, :] = 0
    w[:, 0] = 0
    out, wo = utils.mean(data, weights=w, axis=0, returned=True)
    ans = np.arange(data.shape[1]).astype(np.float) + 1
    ans[0] = np.inf
    nt.assert_true(np.array_equal(out, ans))
    ans = (data.shape[0] - 1) * np.ones(data.shape[1])
    ans[0] = 0
    nt.assert_true(np.all(wo == ans))
    out, wo = utils.mean(data, weights=w, axis=1, returned=True)
    ans = np.mean(np.arange(data.shape[1])[1:] + 1) * np.ones(data.shape[0])
    ans[0] = np.inf
    nt.assert_true(np.all(out == ans))
    ans = (data.shape[1] - 1) * np.ones(data.shape[0])
    ans[0] = 0
    nt.assert_true(np.all(wo == ans))


def test_mean_infs():
    # Fake data
    data = np.zeros((50, 25))
    for i in range(data.shape[1]):
        data[:, i] = i * np.ones_like(data[:, i])
    data[:, 0] = np.inf
    data[0, :] = np.inf
    out, wo = utils.mean(data, axis=0, returned=True)
    ans = np.arange(data.shape[1]).astype(np.float)
    ans[0] = np.inf
    nt.assert_true(np.array_equal(out, ans))
    ans = (data.shape[0] - 1) * np.ones(data.shape[1])
    ans[0] = 0
    nt.assert_true(np.all(wo == ans))
    print(data)
    out, wo = utils.mean(data, axis=1, returned=True)
    ans = np.mean(np.arange(data.shape[1])[1:]) * np.ones(data.shape[0])
    ans[0] = np.inf
    print(out)
    print(ans)
    nt.assert_true(np.all(out == ans))
    ans = (data.shape[1] - 1) * np.ones(data.shape[0])
    ans[0] = 0
    nt.assert_true(np.all(wo == ans))


def test_absmean():
    # Fake data
    data1 = np.zeros((50, 25))
    for i in range(data1.shape[1]):
        data1[:, i] = (-1)**i * np.ones_like(data1[:, i])
    data2 = np.ones_like(data1)
    out1 = utils.absmean(data1)
    out2 = utils.absmean(data2)
    nt.assert_equal(out1, out2)


def test_quadmean():
    # Fake data
    data = np.zeros((50, 25))
    for i in range(data.shape[1]):
        data[:, i] = i * np.ones_like(data[:, i])
    o1, w1 = utils.quadmean(data, returned=True)
    o2, w2 = utils.mean(np.abs(data)**2, returned=True)
    o3 = utils.quadmean(data)  # without returned
    o2 = np.sqrt(o2)
    nt.assert_equal(o1, o2)
    nt.assert_equal(w1, w2)
    nt.assert_equal(o1, o3)


def test_flags2waterfall():
    uv = UVData()
    uv.read_uvfits(os.path.join(DATA_PATH, 'zen.2457698.40355.xx.HH.uvc.vis.uvfits'))

    np.random.seed(0)
    uv.flag_array = np.random.randint(0, 2, size=uv.flag_array.shape, dtype=bool)
    wf = utils.flags2waterfall(uv)
    nt.assert_almost_equal(np.mean(wf), np.mean(uv.flag_array))
    nt.assert_equal(wf.shape, (uv.Ntimes, uv.Nfreqs))

    wf = utils.flags2waterfall(uv, keep_pol=True)
    nt.assert_equal(wf.shape, (uv.Ntimes, uv.Nfreqs, uv.Npols))

    # Test external flag_array
    uv.flag_array = np.zeros_like(uv.flag_array)
    f = np.random.randint(0, 2, size=uv.flag_array.shape, dtype=bool)
    wf = utils.flags2waterfall(uv, flag_array=f)
    nt.assert_almost_equal(np.mean(wf), np.mean(f))
    nt.assert_equal(wf.shape, (uv.Ntimes, uv.Nfreqs))

    # UVCal version
    uvc = UVCal()
    uvc.read_calfits(os.path.join(DATA_PATH, 'zen.2457698.40355.xx.HH.uvcAA.omni.calfits'))

    uvc.flag_array = np.random.randint(0, 2, size=uvc.flag_array.shape, dtype=bool)
    wf = utils.flags2waterfall(uvc)
    nt.assert_almost_equal(np.mean(wf), np.mean(uvc.flag_array))
    nt.assert_equal(wf.shape, (uvc.Ntimes, uvc.Nfreqs))

    wf = utils.flags2waterfall(uvc, keep_pol=True)
    nt.assert_equal(wf.shape, (uvc.Ntimes, uvc.Nfreqs, uvc.Njones))


def test_flags2waterfall_errors():

    # First argument must be UVData or UVCal object
    nt.assert_raises(ValueError, utils.flags2waterfall, 5)

    uv = UVData()
    uv.read_uvfits(os.path.join(DATA_PATH, 'zen.2457698.40355.xx.HH.uvc.vis.uvfits'))
    # Flag array must have same shape as uv.flag_array
    nt.assert_raises(ValueError, utils.flags2waterfall, uv, np.array([4, 5]))


def test_lst_from_uv():
    uv = UVData()
    uv.read_uvfits(os.path.join(DATA_PATH, 'zen.2457698.40355.xx.HH.uvc.vis.uvfits'))
    lst = utils.lst_from_uv(uv)
    nt.assert_true(np.array_equal(uv.lst_array, lst))


def test_lst_from_uv_errors():
    # Argument must be UVData or UVCal
    nt.assert_raises(ValueError, utils.lst_from_uv, 5)
