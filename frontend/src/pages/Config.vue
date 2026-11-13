<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import PageHeading from '../components/common/PageHeading.vue';
import RunList from '../components/RunList.vue';
import Notice from '../components/common/Notice.vue';
import { useTask } from '../hooks/useTask';
import { researchApi } from '../api/research';

const p = defineProps<{ studies: any[]; specimens: any[]; runs: any[]; user: any; reloadResearch: () => Promise<void> }>();
const emit = defineEmits(['open']);
const id = ref(0);
const name = ref('固定面板一致性 ' + new Date().toLocaleTimeString());
const B = ref(400);
const seed = ref(231);
const mergeEnabled = ref(false);
const mergeTargets = ref<Record<string, string>>({});
const task = useTask();
const study = computed(() => p.studies.find((s) => s.id === (id.value || p.studies[0]?.id)));
const N = computed(() => p.specimens.filter((s) => s.study_id === study.value?.id).length);

watch(study, (s) => {
 mergeTargets.value = {};
 if (s) for (const c of s.categories) mergeTargets.value[c] = c;
}, { immediate: true });

const mergeError = computed(() => {
 if (!mergeEnabled.value || !study.value) return '';
 const values = study.value.categories.map((c: string) => (mergeTargets.value[c] || '').trim());
 if (values.some((v) => !v)) return '每个原类别都必须填写归并目标，漏映射会被后端拒绝（422）。';
 const groups = [...new Set(values)];
 if (groups.length < 2) return '全部归为一类时 Pe 恒为 1、κ 未定义；至少保留 2 个归并类别。';
 return '';
});
const mergedGroups = computed(() => {
 if (!study.value || !mergeEnabled.value || mergeError.value) return [];
 const groups: { target: string; originals: string[] }[] = [];
 for (const c of study.value.categories) {
  const target = (mergeTargets.value[c] || '').trim();
  const g = groups.find((x) => x.target === target);
  if (g) g.originals.push(c);
  else groups.push({ target, originals: [c] });
 }
 return groups;
});

async function run() {
 if (mergeError.value) return;
 await task.act(async () => {
  const payload: any = {
   study_id: study.value.id,
   name: name.value,
   bootstrap_repeats: B.value,
   seed: seed.value,
   panel_scope: 'fixed_three_raters',
  };
  if (mergeEnabled.value) {
   payload.category_merge = Object.fromEntries(
    study.value.categories.map((c: string) => [c, (mergeTargets.value[c] || '').trim()]),
   );
  }
  const r = await researchApi.createRun(payload);
  await p.reloadResearch();
  emit('open', r);
 }, mergeEnabled.value ? '双侧κ与配对bootstrap已排队' : 'κ与整样本bootstrap已排队');
}
</script>

<template>
 <PageHeading index="03" title="固定面板，整试样重采样。" description="参数在运行前确定；不按单票重采样，不把新标记者抽样误差混入。归并方案与原始口径同批试样、同次抽样对比。" />
 <div class="config-layout">
  <form class="input-sheet" @submit.prevent="run">
   <label>拟合研究
    <select :value="study?.id || 0" @change="id = Number(($event.target as HTMLSelectElement).value)">
     <option v-for="s in studies" :key="s.id" :value="s.id">{{ s.name }}</option>
    </select>
   </label>
   <label>运行名称<input v-model="name" required /></label>
   <div class="field-pair">
    <label>bootstrap重复 B<input v-model.number="B" type="number" min="400" max="1000" required /></label>
    <label>随机种子 seed<input v-model.number="seed" type="number" min="0" max="1000000000" required /></label>
   </div>
   <p>本研究{{ N }}个独立试样，{{ study?.raters.join(' / ') }}固定面板。经验区间95%，线性percentile；有效比例≥90%才报告。</p>

   <section class="merge-editor">
    <label class="merge-switch"><input type="checkbox" v-model="mergeEnabled" />启用岩相类别归并复核（原始逐票不变，双侧同次抽样）</label>
    <template v-if="mergeEnabled && study">
     <p class="merge-hint">为每个原类别指定归并目标；目标相同即并为一类，留空属漏映射，全部同名会被拒绝。</p>
     <div class="merge-grid">
      <label v-for="c in study.categories" :key="c">
       <span :class="['merge-origin', 'category-' + study.categories.indexOf(c)]">{{ c }}</span>
       <span class="merge-arrow">→</span>
       <input v-model="mergeTargets[c]" :placeholder="`归并目标（默认${c}）`" />
      </label>
     </div>
     <p v-if="mergeError" class="merge-error">{{ mergeError }}</p>
     <div v-else class="merge-preview">
      <small>归并后 {{ mergedGroups.length }} 类：</small>
      <span v-for="g in mergedGroups" :key="g.target" class="merge-chip">{{ g.target }} ← {{ g.originals.join(' / ') }}</span>
     </div>
    </template>
   </section>

   <button v-if="user.role !== 'viewer'" class="primary" :disabled="task.state.busy || !study || !!mergeError">
    送入{{ mergeEnabled ? '双侧' : '' }}κ与bootstrap队列 →
   </button>
   <p v-else>观察员只读已有研究。</p>
   <Notice v-bind="task.state" />
  </form>
  <aside class="method-note">
   <small>AGREEMENT / NOT ACCURACY</small>
   <h2>κ = (P̄ − Pe)<br />÷ (1 − Pe)</h2>
   <p>Pᵢ按同一试样的成对一致计算，Pe来自全部票的类别基率。</p>
   <p>Pe=1时κ未定义。全同类不能标κ1；全一致且多类别时κ可以κ1。</p>
   <p>Bootstrap每次抽完整计数行，退化重复保留原因及数量，未补抽。归并运行两侧共用同一次抽样，任一侧未定义的重复不参与差值区间。</p>
  </aside>
 </div>
 <section class="section">
  <h2>核算队列与归档</h2>
  <RunList :runs="runs" @open="emit('open', $event)" />
 </section>
</template>
