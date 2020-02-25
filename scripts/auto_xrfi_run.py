#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2019 the HERA Project
# Licensed under the MIT License

import sys
from hera_qm import utils
from hera_qm import xrfi

ap = utils.get_metrics_ArgumentParser('auto_xrfi_run')
args = ap.parse_args()
history = ' '.join(sys.argv)

filter_half_widths = args.filter_half_widths.split(',')
filter_half_widths = [float(fw) for fw in filter_half_widths]
filter_centers = args.filter_centers.split(',')
filter_centers = [float(fc) for fc in filter_centers]
skip_wgts = args.skip_wgts.split(',')
skip_wgts = [float(wgt) for wgt in skip_wgts]
sig_adjs = args.sig_adjs.split(',')
sig_adjs = [float(sa) for sa in sig_adjs]
sig_inits = args.sig_inits.split(',')
sig_inits = [float(si) for si in sig_inits]
polarizations = arg.polarizations.split(',')
polarizations = [str(pol)[:2] for pol in polarizations]
xrfi.auto_xrfi_run(data_file=args.data_file, ex_ants=args.ex_ants,
              kt_size=args.kt_size, kf_size=args.kf_size,
              sig_init=args.sig_init, sig_adj=args.sig_adj,
              filter_centers=filter_centers
              filter_half_widths=filter_half_widths,
              skip_wgts=skip_wgts,
              sig_inits=sig_inits,
              sig_adjs=sig_adjs,
              verbose=args.verbose, history=history,
              xrfi_path=args.xrfi_path, label=args.label,
              polarizations=polarizations, clobber=args.clobber)
