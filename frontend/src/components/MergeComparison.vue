<script setup lang="ts">
import { computed } from 'vue';
import { fmt, percent } from '../utils/format';

const p = defineProps<{ result: any }>();
const pb = computed(() => p.result.comparison.bootstrap);
const cmp = computed(() => pb.value.comparison);
const merged = computed(() => p.result.merged);
const rec = computed(() => p.result.reconciliation);

function intervalText(iv: [number, number] | null) {
 return iv ? `[${fmt(iv[0], 6)}, ${fmt(iv[1], 6)}]` : '暂不报告';
}
</script>

<template>
 <section class="merge-panel">
  <div class="section-head">
   <h2>岩相边界归并复核：同一批试样、同一次抽样。</h2>
   <span :class="['status', rec.all_balanced && rec.total_balanced ? 'completed' : 'rejected']">
    票数对账{{ rec.all_balanced && rec.total_balanced ? '平' : '不平' }}
   </span>
  </div>

  <div class="merge-scheme">
   <small>归并方案（原始逐票不变）</small>
   <div v-for="g in result.category_merge.groups" :key="g.merged_category" class="merge-chip">
    <strong>{{ g.merged_category }}</strong> ← {{ g.originals.join(' / ') }}
   </div>
  </div>

  <div class="side-table-scroll">
   <table class="side-table">
    <thead>
     <tr><th>口径</th><th>类别数</th><th>Fleiss κ</th><th>P̄</th><th>Pe</th><th>总票数</th><th>有效重复</th><th>退化重复</th><th>95%经验区间</th></tr>
    </thead>
    <tbody>
     <tr>
      <td><strong>原始类别</strong><small>{{ result.categories.join(' / ') }}</small></td>
      <td>{{ result.categories.length }}</td>
      <td>{{ fmt(result.kappa, 6) }}</td>
      <td>{{ fmt(result.pbar, 6) }}</td>
      <td>{{ fmt(result.pe, 6) }}</td>
      <td>{{ result.total_votes }}</td>
      <td>{{ pb.original.valid_repeats }}</td>
      <td>{{ pb.original.invalid_repeats }}</td>
      <td>{{ intervalText(pb.original.interval) }}</td>
     </tr>
     <tr>
      <td><strong>归并类别</strong><small>{{ merged.categories.join(' / ') }}</small></td>
      <td>{{ merged.categories.length }}</td>
      <td>{{ merged.kappa === null ? '未定义' : fmt(merged.kappa, 6) }}</td>
      <td>{{ fmt(merged.pbar, 6) }}</td>
      <td>{{ fmt(merged.pe, 6) }}</td>
      <td>{{ merged.total_votes }}</td>
      <td>{{ pb.merged.valid_repeats }}</td>
      <td>{{ pb.merged.invalid_repeats }}</td>
      <td>{{ intervalText(pb.merged.interval) }}</td>
     </tr>
     <tr class="delta-row">
      <td><strong>差值（归并 − 原始）</strong><small>点估计与配对bootstrap</small></td>
      <td>—</td>
      <td>{{ result.comparison.point_delta === null ? '未定义' : fmt(result.comparison.point_delta, 6) }}</td>
      <td colspan="3">有效配对 {{ cmp.valid_pairs }} / {{ pb.requested_repeats }} · {{ percent(cmp.valid_fraction) }}</td>
      <td>{{ cmp.valid_pairs }}</td>
      <td>{{ cmp.invalid_pairs }}</td>
      <td>{{ intervalText(cmp.interval) }}</td>
     </tr>
    </tbody>
   </table>
  </div>
  <p class="interval-rule">{{ cmp.interval_reason }}。{{ pb.resampling_unit }}</p>
  <p v-for="(count, reason) in pb.merged.invalid_reasons" :key="reason" class="invalid-reason">{{ reason }}：{{ count }} 次</p>
  <p v-for="(count, reason) in pb.original.invalid_reasons" :key="reason" class="invalid-reason">{{ reason }}：{{ count }} 次</p>

  <div class="reconcile">
   <small>逐试样票数对账（前16行）· 原始总票 {{ rec.original_total_votes }} / 归并总票 {{ rec.merged_total_votes }}</small>
   <table>
    <thead>
     <tr><th>试样</th><th>原始计数 {{ result.categories.join('/') }}</th><th>归并计数 {{ merged.categories.join('/') }}</th><th>原始票</th><th>归并票</th><th>对账</th></tr>
    </thead>
    <tbody>
     <tr v-for="row in rec.per_specimen.slice(0, 16)" :key="row.id">
      <td>{{ row.reference }}</td>
      <td>[{{ row.original_counts.join(', ') }}]</td>
      <td>[{{ row.merged_counts.join(', ') }}]</td>
      <td>{{ row.original_votes }}</td>
      <td>{{ row.merged_votes }}</td>
      <td><span :class="['status', row.balanced ? 'completed' : 'rejected']">{{ row.balanced ? '平' : '不平' }}</span></td>
     </tr>
    </tbody>
   </table>
  </div>

  <details>
   <summary>前16次配对重复：同次抽样行索引、两侧κ与退化原因（不补抽）</summary>
   <div class="replicate-line" v-for="r in pb.replicates.slice(0, 16)" :key="r.repeat">
    <strong>#{{ r.repeat }} 差值 {{ r.kappa_delta === null ? '未定义' : fmt(r.kappa_delta, 6) }}</strong>
    <span>原始 {{ r.original_kappa === null ? '未定义：' + r.original_reason : fmt(r.original_kappa, 6) }} ｜
     归并 {{ r.merged_kappa === null ? '未定义：' + r.merged_reason : fmt(r.merged_kappa, 6) }}</span>
    <span>抽取行 {{ r.sample_indices.slice(0, 10).join(', ') }}{{ r.sample_indices.length > 10 ? ' …' : '' }}</span>
   </div>
  </details>
 </section>
</template>
