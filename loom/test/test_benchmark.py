# Copyright (c) 2014, Salesforce.com, Inc.  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# - Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# - Neither the name of Salesforce.com nor the names of its contributors
#   may be used to endorse or promote products derived from this
#   software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
# OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
# TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import loom.benchmark
import loom.datasets
from nose import SkipTest

DATASET = 'bb-10-10-0.5'


def test_generate():
    config = loom.datasets.CONFIGS[DATASET]
    loom.benchmark.generate(profile=None, **config)


def test_ingest():
    loom.benchmark.ingest(DATASET, profile=None)


def test_init():
    loom.benchmark.shuffle(DATASET, profile=None)


def test_tare():
    loom.benchmark.tare(DATASET, profile=None)


def test_sparsify():
    loom.benchmark.sparsify(DATASET, profile=None)


def test_shuffle():
    loom.benchmark.shuffle(DATASET, profile=None)


def test_infer():
    loom.benchmark.infer(DATASET, profile=None)


def test_checkpoint():
    loom.benchmark.load_checkpoint(DATASET, period_sec=0.2)
    loom.benchmark.infer_checkpoint(DATASET, profile=None)


def test_related():
    loom.benchmark.related(DATASET, sample_count=10, profile=None)


def test_test():
    raise SkipTest('FIXME(fobermeyer) test fails on travis')
    name = loom.benchmark.generate('bb', 4, 4, 1.0)
    loom.benchmark.test(name, debug=False)
