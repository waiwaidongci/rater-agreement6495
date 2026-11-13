def validate_merge_scheme(categories, mapping):
 if not isinstance(mapping, dict) or not mapping:
  raise ValueError('归并方案须为非空的“原类别→归并类别”映射')
 keys=set(mapping.keys())
 if keys != set(categories):
  parts=[]
  missing=[c for c in categories if c not in keys]
  extra=sorted(keys-set(categories))
  if missing:parts.append('漏映射类别：'+'、'.join(missing))
  if extra:parts.append('含声明外未知类别：'+'、'.join(extra))
  raise ValueError('；'.join(parts))
 if any(not isinstance(v, str) or not v.strip() or len(v.strip()) > 80 for v in mapping.values()):
  raise ValueError('归并目标类别须为1..80字非空字符串')
 normalized={c:mapping[c].strip() for c in categories}
 targets=[]
 for c in categories:
  if normalized[c] not in targets:targets.append(normalized[c])
 if len(targets) < 2:
  raise ValueError('归并后至少保留2个类别；全部归为一类时Pe恒为1、κ未定义，方案拒绝')
 return normalized, targets

def merge_groups(categories, mapping, merged_categories):
 return [{'merged_category':t,'original_categories':[c for c in categories if mapping[c] == t]} for t in merged_categories]

def merged_counts(rows, categories, mapping, merged_categories):
 index={t:j for j, t in enumerate(merged_categories)}
 width=len(merged_categories)
 matrix=[]
 for row in rows:
  merged=[0] * width
  for original, count in zip(categories, row['counts']):
   merged[index[mapping[original]]] += count
  if sum(merged) != sum(row['counts']):
   raise ValueError('归并后票数与原始逐票对账不平，拒绝该方案')
  matrix.append(merged)
 return matrix

def specimen_reconciliation(rows, merged_matrix):
 per_specimen=[]
 for row, merged in zip(rows, merged_matrix):
  original_total=sum(row['counts']);merged_total=sum(merged)
  per_specimen.append({'id':row['id'],'reference':row['reference'],'original_counts':list(row['counts']),'merged_counts':list(merged),'original_votes':original_total,'merged_votes':merged_total,'balanced':original_total == merged_total == 3})
 original_total=sum(item['original_votes'] for item in per_specimen)
 merged_total=sum(item['merged_votes'] for item in per_specimen)
 return {'per_specimen':per_specimen,'all_balanced':all(item['balanced'] for item in per_specimen),'original_total_votes':original_total,'merged_total_votes':merged_total,'total_balanced':original_total == merged_total}
