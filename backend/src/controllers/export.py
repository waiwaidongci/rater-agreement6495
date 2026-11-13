from fastapi import HTTPException
from src.models import ReviewMemo
from src.services.audit import record
from src.utils.csv_export import csv_response

def export_memo(db, id, actor):
 memo=db.get(ReviewMemo, id)
 if not memo:
  raise HTTPException(404, '说明不存在')
 if memo.status != 'approved':
  raise HTTPException(409, '仅批准说明可导出')
 r=memo.result_snapshot
 b=r['bootstrap']
 ci=b['interval']
 merged=bool(r.get('merged'))
 if merged:
  scheme=r['category_merge']
  groups='；'.join(f"{g['merged_category']}←{'/'.join(g['original_categories'])}" for g in scheme['groups'])
  m=r['merged'];cmp=r['comparison'];pb=cmp['bootstrap'];pci=pb['comparison']['interval']
  merge_cols=[groups, m['kappa'] if m['kappa'] is not None else '未定义',
   m['pbar'] if m['pbar'] is not None else '', m['pe'] if m['pe'] is not None else '',
   cmp['point_delta'] if cmp['point_delta'] is not None else '',
   pb['comparison']['valid_pairs'], pci[0] if pci else '', pci[1] if pci else '']
  headers=['复核说明', '研究', '指纹', 'Fleissκ(原始)', 'Pbar(原始)', 'Pe(原始)', '有效重复(原始)', '退化重复(原始)',
   '经验区间下限(原始)', '经验区间上限(原始)', '归并方案', 'Fleissκ(归并)', 'Pbar(归并)', 'Pe(归并)', 'κ差值(归并-原始)',
   '有效配对', '差值区间下限', '差值区间上限', '试样', '逐项P', '原始类别计数', '归并类别计数', '人工解释', '下一步', '审核意见']
 else:
  merge_cols=[]
  headers=['复核说明', '研究', '指纹', 'Fleissκ', 'Pbar', 'Pe', '有效重复', '退化重复', '经验区间下限', '经验区间上限',
   '试样', '逐项P', '类别计数', '人工解释', '下一步', '审核意见']
 rows=[]
 for item in r['items']:
  base=[memo.name, r['source_study']['name'], r['fingerprint'], r['kappa'], r['pbar'], r['pe'],
   b['valid_repeats'], b['invalid_repeats'], ci[0] if ci else '', ci[1] if ci else '']
  if merged:
   base += merge_cols
   base += [item['reference'], item['agreement'], str(item['counts']), str(item.get('merged_counts', []))]
  else:
   base += [item['reference'], item['agreement'], str(item['counts'])]
  base += [memo.interpretation, memo.next_step, memo.review_note]
  rows.append(base)
 record(db, actor, 'memo.exported', {'memo_id': id, 'merged': merged})
 return csv_response(f'rater-review-{id}.csv', rows, headers)
