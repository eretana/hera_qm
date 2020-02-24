#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2019 the HERA Project
# Licensed under the MIT License

import sys
from hera_qm import utils
from hera_qm import xrfi

ap = utils.get_metrics_ArgumentParser('xrfi_auto_run')
args = ap.parse_args()
history = ' '.join(sys.argv)

xrfi.auto_xrfi_run(data_file=args.data_file, ex_ants=args.ex_ants,
              kt_size=args.kt_size, kf_size=args.kf_size,
              sig_init=args.sig_init, sig_adj=args.sig_adj,
              filter_center=args.filter_centers,
              filter_half_widths=args.filter_half_widths,
              verbose=args.verbose, skip_wgts=args.skip_wgts,
              sig_inits=args.sig_inits, sig_adjs=args.sig_adjs,
              history=history, xrfi_path=args.xrfi_path, label=args.label,
              polarizations=args.polarizations, clobber=args.clobber)
