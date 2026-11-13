from collections import Counter
import numpy as np
from .fleiss import fleiss, UndefinedKappa

UNDEFINED_MERGED = '归并侧Pe=1：该次抽样全部票落同一归并类别，κ未定义'

def _histogram(values, edges):
 return {'edges': list(edges), 'counts': np.histogram(values, bins=edges)[0].tolist()}

def _side_block(seed, repeats, records, key, reason_key):
 values=[r[key] for r in records if r[key] is not None]
 valid=len(values)
 eligible=valid * 10 >= repeats * 9
 interval=np.quantile(values, [.025, .975], method='linear').tolist() if eligible else None
 edges=np.linspace(-1, 1, 21)
 reasons=Counter(r[reason_key] for r in records if r[key] is None)
 return {'seed': seed, 'requested_repeats': repeats, 'valid_repeats': valid, 'invalid_repeats': repeats - valid,
  'valid_fraction': valid / repeats, 'invalid_reasons': dict(reasons), 'interval': interval, 'confidence_level': .95,
  'interval_status': 'reported' if eligible else 'insufficient_valid',
  'interval_reason': ('有效比例≥90%，有效重复的2.5%/97.5%线性percentile经验区间' if eligible else '有效重复少于90%，沿用规则暂不报告经验区间'),
  'histogram': _histogram(values, edges)}

def paired_row_bootstrap(original_matrix, merged_matrix, repeats, seed):
 original_matrix=np.asarray(original_matrix, dtype=int)
 merged_matrix=np.asarray(merged_matrix, dtype=int)
 N=len(original_matrix)
 rng=np.random.default_rng(seed)
 records=[]
 deltas=[]
 delta_reasons=Counter()
 for i in range(repeats):
  indices=rng.integers(0, N, size=N)
  try:
   original_kappa=fleiss(original_matrix[indices])['kappa']
   original_reason=None
  except UndefinedKappa as error:
   original_kappa=None
   original_reason=str(error)
  try:
   merged_kappa=fleiss(merged_matrix[indices])['kappa']
   merged_reason=None
  except UndefinedKappa:
   merged_kappa=None
   merged_reason=UNDEFINED_MERGED
  if original_kappa is not None and merged_kappa is not None:
   delta=merged_kappa - original_kappa
   deltas.append(delta)
   delta_reason=None
  else:
   delta=None
   delta_reason='一侧κ未定义，该重复不参与差值与区间；原因保留，未补抽'
   delta_reasons[delta_reason] += 1
  records.append({'repeat': i, 'sample_indices': indices.tolist(), 'original_kappa': original_kappa,
   'original_reason': original_reason, 'merged_kappa': merged_kappa, 'merged_reason': merged_reason,
   'kappa_delta': delta, 'delta_reason': delta_reason, 'paired_valid': delta is not None})
 original=_side_block(seed, repeats, records, 'original_kappa', 'original_reason')
 merged=_side_block(seed, repeats, records, 'merged_kappa', 'merged_reason')
 valid_pairs=len(deltas)
 eligible=valid_pairs * 10 >= repeats * 9
 delta_interval=np.quantile(deltas, [.025, .975], method='linear').tolist() if eligible else None
 delta_edges=np.linspace(-2, 2, 41)
 comparison={'requested_repeats': repeats, 'valid_pairs': valid_pairs, 'invalid_pairs': repeats - valid_pairs,
  'valid_fraction': valid_pairs / repeats, 'invalid_reasons': dict(delta_reasons),
  'interval': delta_interval, 'confidence_level': .95,
  'interval_status': 'reported' if eligible else 'insufficient_valid',
  'interval_reason': ('有效配对≥90%，对差值（归并κ−原始κ）取2.5%/97.5%线性percentile经验区间' if eligible else '有效配对少于90%，沿用规则暂不报告差值经验区间'),
  'quantile_method': 'numpy.quantile(method=linear)', 'histogram': _histogram(deltas, delta_edges)}
 return {'seed': seed, 'requested_repeats': repeats, 'resampling_unit': 'entire specimen count row with replacement; fixed same three raters; identical draw for both sides',
  'original': original, 'merged': merged, 'comparison': comparison, 'replicates': records,
  'interpretation': '两侧共用同一批试样与同一次整行抽样；任一侧κ未定义的重复保留原因、不补抽，不参与差值区间。'}
