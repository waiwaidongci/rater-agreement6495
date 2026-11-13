<script setup lang="ts">
import { computed } from 'vue';
import PageHeading from '../components/common/PageHeading.vue';
import Empty from '../components/common/Empty.vue';
import Status from '../components/common/Status.vue';
import AgreementSummary from '../components/AgreementSummary.vue';
import VoteMatrix from '../components/VoteMatrix.vue';
import CategoryMargins from '../components/CategoryMargins.vue';
import BootstrapStrip from '../components/BootstrapStrip.vue';
import MergeComparison from '../components/MergeComparison.vue';

const p = defineProps<{ runs: any[]; selectedId: number }>();
const emit = defineEmits(['open']);
const run = computed(() => p.runs.find((r) => r.id === p.selectedId) || p.runs[0]);
function select(e: Event) {
 emit('open', p.runs.find((r) => r.id === +(e.target as HTMLSelectElement).value));
}
</script>

<template>
 <PageHeading index="04" title="一致、机会与区间，各自有边界。" description="κ相对类别基率衡量一致性；经验区间只对固定面板下的iid试样解释。归并复核两侧同批试样、同次抽样。" />
 <label>结果运行
  <select :value="run?.id" @change="select">
   <option v-for="r in runs" :key="r.id" :value="r.id">#{{ r.id }} {{ r.name }}<template v-if="r.config?.category_merge">（含归并方案）</template></option>
  </select>
 </label>
 <p v-if="run"><Status :value="run.status" />　{{ run.error }}</p>
 <template v-if="run?.result">
  <p v-if="run.result.merged" class="merge-banner">本运行含类别归并方案；以下为原始口径，归并双侧对比见下方专节。</p>
  <AgreementSummary :result="run.result" />
  <div class="atlas-layout">
   <VoteMatrix :result="run.result" :limit="16" />
   <CategoryMargins :result="run.result" />
  </div>
  <BootstrapStrip :bootstrap="run.result.bootstrap" />
  <MergeComparison v-if="run.result.merged" :result="run.result" />
  <div class="boundary-note">
   <strong>固定同一三人面板；一致性不是准确率。</strong>
   <p>类别失衡会改变Pe。该经验区间不含抽取新标记者的不确定性，也不是岩相识别正确率或地质事实保证。归并不改写原始逐票，仅对计数行按方案聚合。</p>
  </div>
  <details class="provenance">
   <summary>冻结指纹与算法边界</summary>
   <p class="fingerprint">{{ run.result.fingerprint }}</p>
   <p>{{ run.result.interpretation }}</p>
   <p>类别顺序 {{ run.result.categories.join(' / ') }}，索引对应上方票格颜色。</p>
   <p v-if="run.result.category_merge">归并方案指纹敏感：任何映射、类别或面板顺序变化都会改变指纹；同方案同seed重算结果逐位一致。</p>
  </details>
  <a href="#memos" class="text-action">形成分类口径复核说明 →</a>
 </template>
 <Empty v-else :title="run?.status === 'failed' ? '本次κ未完成' : '等待真实worker核算'" :help="run?.error || '任务每3秒刷新，先在配置页排队。'" />
</template>
