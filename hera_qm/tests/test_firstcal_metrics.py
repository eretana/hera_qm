# -*- coding: utf-8 -*-
# Copyright (c) 2018 the HERA Project
# Licensed under the MIT License

"""
test_firstcal_metrics.py
"""
import numpy as np
from hera_qm import firstcal_metrics
from hera_qm.data import DATA_PATH
import unittest
import os
from hera_qm import utils
import hera_qm.tests as qmtest
from hera_qm import metrics_io
import sys


class Test_FirstCalMetrics(unittest.TestCase):

    def setUp(self):
        infile = os.path.join(DATA_PATH, 'zen.2457555.50099.yy.HH.uvcA.first.calfits')
        self.FC = firstcal_metrics.FirstCalMetrics(infile)
        self.out_dir = os.path.join(DATA_PATH, 'test_output')

    def test_init(self):
        self.assertEqual(self.FC.Nants, 17)
        self.assertEqual(len(self.FC.delays), 17)

    def test_run_metrics(self):
        self.FC.run_metrics(std_cut=1.0)
        self.assertEqual(self.FC.metrics['yy']['good_sol'], True)
        self.assertEqual(self.FC.metrics['yy']['bad_ants'], [])
        self.assertIn(9, self.FC.metrics['yy']['z_scores'])
        self.assertIn(9, self.FC.metrics['yy']['ant_std'])
        self.assertIn(9, self.FC.metrics['yy']['ant_avg'])
        self.assertIn(9, self.FC.metrics['yy']['ants'])
        self.assertIn(9, self.FC.metrics['yy']['z_scores'])
        self.assertIn(9, self.FC.metrics['yy']['ant_z_scores'])
        self.assertAlmostEqual(1.0, self.FC.metrics['yy']['std_cut'])
        self.assertAlmostEqual(self.FC.metrics['yy']['agg_std'], 0.044662349588061437)
        self.assertAlmostEqual(self.FC.metrics['yy']['max_std'], 0.089829821120782846)
        self.assertEqual('yy', self.FC.metrics['yy']['pol'])

        # Test bad ants detection
        self.FC.delay_fluctuations[0, :] *= 1000
        self.FC.run_metrics()
        self.assertEqual(self.FC.ants[0], self.FC.metrics['yy']['bad_ants'])
        # Test bad full solution
        self.FC.delay_fluctuations[1:, :] *= 1000
        self.FC.run_metrics()
        self.assertEqual(self.FC.metrics['yy']['good_sol'], False)

    def test_write_error_bad_type(self):
        """Test an error is raised if bad filetype is given to write."""
        self.FC.run_metrics()
        outfile = os.path.join(self.out_dir, 'firstcal_metrics.npz')
        self.assertRaises(ValueError, self.FC.write_metrics,
                          filename=outfile, filetype='npz')

    def test_write_load_metrics(self):
        # run metrics
        self.FC.run_metrics()
        num_keys = len(self.FC.metrics.keys())
        outfile = os.path.join(self.out_dir, 'firstcal_metrics.json')
        if os.path.isfile(outfile):
            os.remove(outfile)
        # write json
        self.FC.write_metrics(filename=outfile, filetype='json')
        self.assertTrue(os.path.isfile(outfile))
        # load json
        self.FC.load_metrics(filename=outfile)
        self.assertEqual(len(self.FC.metrics.keys()), num_keys)
        # erase
        os.remove(outfile)
        # write pickle
        outfile = os.path.join(self.out_dir, 'firstcal_metrics.pkl')
        if os.path.isfile(outfile):
            os.remove(outfile)

        self.FC.write_metrics(filename=outfile, filetype='pkl')
        self.assertTrue(os.path.isfile(outfile))
        # load pickle
        self.FC.load_metrics(filename=outfile)
        self.assertEqual(len(self.FC.metrics.keys()), num_keys)
        os.remove(outfile)

        outfile = os.path.join(self.out_dir, 'firstcal_metrics.hdf5')
        if os.path.isfile(outfile):
            os.remove(outfile)
        self.FC.write_metrics(filename=outfile, filetype='hdf5')
        self.assertTrue(os.path.isfile(outfile))
        # load pickle
        self.FC.load_metrics(filename=outfile)
        # These are added by default in hdf5 writes but not necessary here
        self.FC.metrics.pop('history', None)
        self.FC.metrics.pop('version', None)
        self.assertEqual(len(self.FC.metrics.keys()), num_keys)
        os.remove(outfile)

        # Check some exceptions
        outfile = os.path.join(self.out_dir, 'firstcal_metrics.txt')
        self.assertRaises(IOError, self.FC.load_metrics, filename=outfile)
        outfile = self.FC.fc_filestem + '.first_metrics.json'
        self.FC.write_metrics(filetype='json')  # No filename
        self.assertTrue(os.path.isfile(outfile))
        os.remove(outfile)

        outfile = self.FC.fc_filestem + '.first_metrics.pkl'
        self.FC.write_metrics(filetype='pkl')  # No filename
        self.assertTrue(os.path.isfile(outfile))
        os.remove(outfile)

        outfile = self.FC.fc_filestem + '.first_metrics.hdf5'
        self.FC.write_metrics(filetype='hdf5')  # No filename
        self.assertTrue(os.path.isfile(outfile))
        os.remove(outfile)

    @qmtest.skipIf_no_matplotlib
    def test_plot_delays(self):
        import matplotlib.pyplot as plt
        fname = os.path.join(self.out_dir, 'dlys.png')
        if os.path.isfile(fname):
            os.remove(fname)
        self.FC.plot_delays(fname=fname, save=True)
        self.assertTrue(os.path.isfile(fname))
        os.remove(fname)
        plt.close('all')
        self.FC.plot_delays(fname=fname, save=True, plot_type='solution')
        self.assertTrue(os.path.isfile(fname))
        os.remove(fname)
        plt.close('all')
        self.FC.plot_delays(fname=fname, save=True, plot_type='fluctuation')
        self.assertTrue(os.path.isfile(fname))
        os.remove(fname)
        plt.close('all')

        # Check cm defaults to spectral
        self.FC.plot_delays(fname=fname, save=True, cmap='foo')
        self.assertTrue(os.path.isfile(fname))
        os.remove(fname)
        plt.close('all')
        # check return figs
        fig = self.FC.plot_delays()
        self.assertTrue(fig is not None)
        plt.close('all')

    @qmtest.skipIf_no_matplotlib
    def test_plot_zscores(self):
        import matplotlib.pyplot as plt
        # check exception
        self.assertRaises(NameError, self.FC.plot_zscores)
        self.FC.run_metrics()
        self.assertRaises(NameError, self.FC.plot_zscores, plot_type='foo')
        # check output
        fname = os.path.join(self.out_dir, 'zscrs.png')
        if os.path.isfile(fname):
            os.remove(fname)
        self.FC.plot_zscores(fname=fname, save=True)
        self.assertTrue(os.path.isfile(fname))
        os.remove(fname)
        plt.close('all')
        self.FC.plot_zscores(fname=fname, plot_type='time_avg', save=True)
        self.assertTrue(os.path.isfile(fname))
        os.remove(fname)
        plt.close('all')
        # check return fig
        fig = self.FC.plot_zscores()
        self.assertTrue(fig is not None)
        plt.close('all')

    @qmtest.skipIf_no_matplotlib
    def test_plot_stds(self):
        import matplotlib.pyplot as plt
        # check exception
        self.assertRaises(NameError, self.FC.plot_stds)
        self.FC.run_metrics()
        self.assertRaises(NameError, self.FC.plot_stds, xaxis='foo')
        # check output
        fname = os.path.join(self.out_dir, 'stds.png')
        if os.path.isfile(fname):
            os.remove(fname)
        self.FC.plot_stds(fname=fname, save=True)
        self.assertTrue(os.path.isfile(fname))
        os.remove(fname)
        plt.close('all')
        self.FC.plot_stds(fname=fname, xaxis='time', save=True)
        self.assertTrue(os.path.isfile(fname))
        os.remove(fname)
        plt.close('all')
        # check return fig
        fig = self.FC.plot_stds()
        self.assertTrue(fig is not None)
        plt.close('all')

    def test_rotated_metrics(self):
        infile = os.path.join(DATA_PATH, 'zen.2457555.42443.xx.HH.uvcA.bad.first.calfits')
        FC = firstcal_metrics.FirstCalMetrics(infile)
        FC.run_metrics(std_cut=0.5)
        out_dir = os.path.join(DATA_PATH, 'test_output')
        # test pickup of rotant key
        self.assertIn('rot_ants', FC.metrics['xx'].keys())
        # test rotants is correct
        self.assertEqual([43], FC.metrics['xx']['rot_ants'])

    def test_delay_smoothing(self):
        infile = os.path.join(DATA_PATH, 'zen.2457555.50099.yy.HH.uvcA.first.calfits')
        np.random.seed(0)
        FC = firstcal_metrics.FirstCalMetrics(infile, use_gp=False)
        self.assertAlmostEqual(FC.delay_fluctuations[0, 0], 0.043740587980040324, delta=0.000001)
        np.random.seed(0)
        FC = firstcal_metrics.FirstCalMetrics(infile, use_gp=True)
        self.assertAlmostEqual(FC.delay_fluctuations[0, 0], 0.024669144881121961, delta=0.000001)


class Test_FirstCalMetrics_two_pols(unittest.TestCase):

    def setUp(self):
        infile = os.path.join(DATA_PATH, 'zen.2458098.49835.HH.first.calfits')
        self.FC = firstcal_metrics.FirstCalMetrics(infile)
        self.out_dir = os.path.join(DATA_PATH, 'test_output')

    def test_init(self):
        self.assertEqual(self.FC.Nants, 11)
        self.assertEqual(len(self.FC.delays), 11)

    def test_run_metrics_two_pols(self):
        # These results were run with a seed of 0, the seed shouldn't matter
        # but you never know.
        two_pol_known_results = os.path.join(DATA_PATH, 'example_two_polarization_firstcal_results.hdf5')
        np.random.seed(0)
        self.FC.run_metrics(std_cut=1.0)
        known_output = metrics_io.load_metric_file(two_pol_known_results)

        known_output.pop('history', None)
        known_output.pop('version', None)
        # There are some full paths of files saved in the files
        # Perhaps for record keeping, but that messes up the test comparison
        for key in known_output:
            known_output[key].pop('fc_filename', None)
            known_output[key].pop('fc_filestem', None)
            known_output[key].pop('version', None)
        for key in self.FC.metrics:
            self.FC.metrics[key].pop('fc_filename', None)
            self.FC.metrics[key].pop('fc_filestem', None)
            self.FC.metrics[key].pop('version', None)
        qmtest.recursive_compare_dicts(self.FC.metrics, known_output)


class TestFirstcalMetricsRun(unittest.TestCase):
    def test_firstcal_metrics_run(self):
        # get argument object
        a = utils.get_metrics_ArgumentParser('firstcal_metrics')
        if DATA_PATH not in sys.path:
            sys.path.append(DATA_PATH)

        arg0 = "--std_cut=0.5"
        arg1 = "--extension=.firstcal_metrics.hdf5"
        arg2 = "--metrics_path={}".format(os.path.join(DATA_PATH, 'test_output'))
        arg3 = "--filetype=h5"
        arguments = ' '.join([arg0, arg1, arg2, arg3])

        # Test runing with no files
        cmd = ' '.join([arguments, ''])
        args = a.parse_args(cmd.split())
        history = cmd
        self.assertRaises(AssertionError, firstcal_metrics.firstcal_metrics_run,
                          args.files, args, history)

        # Test running with file
        filename = os.path.join(DATA_PATH, 'zen.2457555.50099.yy.HH.uvcA.first.calfits')
        dest_file = os.path.join(DATA_PATH, 'test_output',
                                 'zen.2457555.50099.yy.HH.uvcA.first.'
                                 + 'firstcal_metrics.hdf5')
        if os.path.exists(dest_file):
            os.remove(dest_file)
        cmd = ' '.join([arguments, filename])
        args = a.parse_args(cmd.split())
        history = cmd
        firstcal_metrics.firstcal_metrics_run(args.files, args, history)
        self.assertTrue(os.path.exists(dest_file))
        os.remove(dest_file)


if __name__ == "__main__":
    unittest.main()
