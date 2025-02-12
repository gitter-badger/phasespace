#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# @file   bench_phasespace.py
# @author Albert Puig (albert.puig@cern.ch)
# @date   27.02.2019
# =============================================================================
"""Benchmark phasespace."""



import tensorflow as tf

from phasespace import phasespace

import os, sys

sys.path.append(os.path.dirname(__file__))

from .monitoring import Timer

# to play around with optimization, no big effect though
NUM_PARALLEL_EXEC_UNITS = 1
config = tf.ConfigProto(intra_op_parallelism_threads=NUM_PARALLEL_EXEC_UNITS, inter_op_parallelism_threads=1,
                        allow_soft_placement=True, device_count={'CPU': NUM_PARALLEL_EXEC_UNITS})

B_MASS = 5279.0
B_AT_REST = tf.stack((0.0, 0.0, 0.0, B_MASS), axis=-1)
PION_MASS = 139.6

N_EVENTS = 1000000
CHUNK_SIZE = N_EVENTS

N_EVENTS_VAR = tf.Variable(initial_value=N_EVENTS)
CHUNK_SIZE_VAR = tf.Variable(initial_value=CHUNK_SIZE)

samples = [phasespace.generate(B_AT_REST,
                               [PION_MASS, PION_MASS, PION_MASS],
                               CHUNK_SIZE_VAR)
           for _ in range(0, N_EVENTS, CHUNK_SIZE)
           ]

sess = tf.Session(
        config=config
        )

sess.run([N_EVENTS_VAR.initializer, CHUNK_SIZE_VAR.initializer])


def test_three_body():
    """Test B -> pi pi pi decay."""
    with Timer(verbose=True):
        print("Initial run (may takes more time than consequent runs)")
        do_run()  # to get rid of initial overhead
    print("starting benchmark")
    with Timer(verbose=True):
        CHUNK_SIZE_VAR.load(CHUNK_SIZE + 1, session=sess)  # +1 to make sure we're not using any trivial caching
        samples = do_run()
        print("Shape of one particle momentum", samples[0][1][0].shape)


def do_run():
    return sess.run(samples)


if __name__ == "__main__":
    test_three_body()

# EOF
