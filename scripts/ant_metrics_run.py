#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2019 the HERA Project
# Licensed under the MIT License

from hera_qm import utils
from hera_qm import ant_metrics
import sys

ap = utils.get_metrics_ArgumentParser('ant_metrics')
args = ap.parse_args()
history = ' '.join(sys.argv)
if args.pol == '':
    args.pol = ['xx', 'yy', 'xy', 'yx']
else:
    args.pol = list(args.pol.split(','))
ant_metrics.ant_metrics_run(args.files, pols=args.pol, crossCut=args.crossCut,
                            deadCut=args.deadCut,
                            alwaysDeadCut=args.alwaysDeadCut,
                            metrics_path=args.metrics_path,
                            extension=args.extension,
                            vis_format=args.vis_format,
                            verbose=args.verbose, history=history,
                            run_mean_vij=args.run_mean_vij,
                            run_red_corr=args.run_red_corr,
                            run_cross_pols=args.run_cross_pols)
