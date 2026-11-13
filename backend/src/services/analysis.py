from .validation import validate_config
from .counts import panel_counts
from .fleiss import fleiss, UndefinedKappa
from .bootstrap import row_bootstrap
from .paired_bootstrap import paired_row_bootstrap, UNDEFINED_MERGED
from .merge import validate_merge_scheme, merge_groups, merged_counts, specimen_reconciliation
from .fingerprint import fingerprint

def analyze(study, specimens, votes, config):
 validate_config(config)
 rows=panel_counts(study, specimens, votes)
 matrix=[r['counts'] for r in rows]
 result=fleiss(matrix)
 for row, P in zip(rows, result['item_agreement']):
  row['agreement']=P
 result['bootstrap']=row_bootstrap(matrix, config['bootstrap_repeats'], config['seed'])
 result['source_study']=study
 result['categories']=study['categories']
 result['raters']=study['raters']
 result['items']=rows
 result['fingerprint']=fingerprint(study, specimens, votes, config)
 result['interpretation']='Agreement relative to empirical category marginals, not accuracy against a gold standard. Fixed complete three-person panel; bootstrap resamples whole iid specimens, not votes or new raters.'
 scheme=config.get('category_merge')
 if scheme:
  mapping, merged_categories=validate_merge_scheme(study['categories'], scheme)
  grouped=merge_groups(study['categories'], mapping, merged_categories)
  group_matrix=merged_counts(rows, study['categories'], mapping, merged_categories)
  reconciliation=specimen_reconciliation(rows, group_matrix)
  for row, merged in zip(rows, group_matrix):
   row['merged_counts']=merged
  try:
   merged_point=fleiss(group_matrix)
   merged_kappa=merged_point['kappa']
   merged_undefined_reason=None
  except UndefinedKappa:
   merged_point=None
   merged_kappa=None
   merged_undefined_reason=UNDEFINED_MERGED
  paired=paired_row_bootstrap(matrix, group_matrix, config['bootstrap_repeats'], config['seed'])
  result['category_merge']={'mapping': mapping, 'merged_categories': merged_categories, 'groups': grouped}
  result['merged']={'categories': merged_categories, 'kappa': merged_kappa, 'undefined_reason': merged_undefined_reason,
   'pbar': None if merged_point is None else merged_point['pbar'],
   'pe': None if merged_point is None else merged_point['pe'],
   'category_totals': None if merged_point is None else merged_point['category_totals'],
   'category_prevalence': None if merged_point is None else merged_point['category_prevalence'],
   'item_agreement': None if merged_point is None else merged_point['item_agreement'],
   'specimen_count': len(rows), 'total_votes': sum(sum(r) for r in group_matrix)}
  result['reconciliation']=reconciliation
  result['comparison']={'point_delta': None if merged_kappa is None else merged_kappa - result['kappa'],
   'bootstrap': paired,
   'interpretation': '同一批试样、同一次整行抽样下的两侧κ；原始逐票不变，差值为归并侧减原始侧。'}
 return result
