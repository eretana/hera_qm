#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2018 the HERA Project
# Licensed under the MIT License

import sys
from hera_qm import utils
from hera_qm import xrfi

a = utils.get_metrics_ArgumentParser('xrfi_apply')
args = a.parse_args()
filename = args.filename
history = ' '.join(sys.argv)

xrfi.xrfi_apply(filename, args, history)
