#!/usr/bin/env python
"""
A simple coin flipping example. The model is written in NumPy/SciPy.
Inspired by Stan's toy example.

Probability model
  Prior: Beta
  Likelihood: Bernoulli
Variational model
  Likelihood: Mean-field Beta
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import edward as ed
import numpy as np
import tensorflow as tf

from edward.models import PythonModel, Beta
from scipy.stats import beta, bernoulli


class BetaBernoulli(PythonModel):
  """p(x, p) = Bernoulli(x | p) * Beta(p | 1, 1)"""
  def _py_log_prob(self, xs, zs):
    # This example is written for pedagogy. We recommend
    # vectorizing operations in practice.
    xs = xs['x']
    ps = zs['p']
    n_samples = ps.shape[0]
    lp = np.zeros(n_samples, dtype=np.float32)
    for b in range(n_samples):
      lp[b] = beta.logpdf(ps[b, :], a=1.0, b=1.0)
      for n in range(xs.shape[0]):
        lp[b] += bernoulli.logpmf(xs[n], p=ps[b, :])

    return lp


ed.set_seed(42)
data = {'x': np.array([0, 1, 0, 0, 0, 0, 0, 0, 0, 1])}

model = BetaBernoulli()

qp_a = tf.nn.softplus(tf.Variable(tf.random_normal([1])))
qp_b = tf.nn.softplus(tf.Variable(tf.random_normal([1])))
qp = Beta(a=qp_a, b=qp_b)

inference = ed.MFVI({'p': qp}, data, model)
inference.run(n_iter=10000)
