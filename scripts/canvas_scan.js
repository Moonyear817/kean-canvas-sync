// Run in a Chrome tab on the Canvas site (logged in) via the claude-in-chrome
// javascript_tool. Replace __DATA__ with the output of local_index.py before sending. Result is kept in window.__todo / window.__big /
// window.__skipped; the returned string is a short summary (the tool truncates
// long outputs, so read the lists in slices afterwards).
const DATA = __DATA__;
const LOCAL = DATA.index;
const ENTRY = DATA.config.entry_year;              // year the student started (fall)
const MAX_BYTES = DATA.config.max_mb * 1024 * 1024;
const NUM = ['零', '一', '二', '三', '四', '五', '六'];
const SEASON = { FA: '秋季', SP: '春季', SU: '夏季', WI: '冬季' };

// "2026FAW*ACCT*2200*W05 (...)" -> term "2026FA" -> "大二秋季" (entry_year 2025):
// fall of year Y is study year Y-ENTRY+1, spring/summer of year Y is study year Y-ENTRY
function termFolder(courseName) {
  const m = /^(\d{4})(FA|SP|SU|WI)/.exec(courseName || '');
  if (!m) return null;
  const y = +m[1], s = m[2];
  const grade = s === 'FA' ? y - ENTRY + 1 : y - ENTRY;
  return '大' + (NUM[grade] || grade) + SEASON[s];
}
// "ACCT*2200*W05" -> "ACCT2200"
function courseFolder(code) {
  const p = (code || '').split('*');
  return p.length >= 2 ? p[0] + p[1] : null;
}
async function all(url) {
  let out = [];
  while (url) {
    const r = await fetch(url);
    if (!r.ok) return out;
    out = out.concat(await r.json());
    const next = (r.headers.get('Link') || '').split(',').find(s => s.includes('rel="next"'));
    url = next ? next.match(/<([^>]+)>/)[1] : null;
  }
  return out;
}

const me = await fetch('/api/v1/users/self');
let result = 'NOT_LOGGED_IN';
if (me.ok) {
  const todo = [], big = [], skipped = [], unknown = [];
  const courses = await all('/api/v1/courses?enrollment_state=active&per_page=100');
  for (const c of courses) {
    const term = termFolder(c.name), course = courseFolder(c.course_code);
    if (!term || !course) { unknown.push(c.name); continue; }
    const key = term + '/' + course;
    const have = new Set(LOCAL[key] || []);

    const files = {};
    (await all(`/api/v1/courses/${c.id}/files?per_page=100`)).forEach(f => files[f.id] = f);
    for (const m of await all(`/api/v1/courses/${c.id}/modules?include[]=items&per_page=100`)) {
      for (const it of (m.items || [])) {
        if (it.type === 'File' && !files[it.content_id]) {
          const r = await fetch(`/api/v1/courses/${c.id}/files/${it.content_id}`);
          if (r.ok) files[it.content_id] = await r.json();
        }
      }
    }
    const list = Object.values(files);
    const pptxStems = new Set(list.filter(f => /\.pptx?$/i.test(f.display_name))
      .map(f => f.display_name.replace(/\.[^.]+$/, '').toLowerCase()));

    for (const f of list) {
      const name = f.display_name, lower = name.normalize('NFC').toLowerCase();
      const stem = lower.replace(/\.[^.]+$/, '');
      const row = { key, term, course, id: f.id, size: f.size, name };
      if (lower.startsWith('~$') || have.has(lower)) continue;
      if (lower.endsWith('.zip') && have.has(stem)) continue;          // already extracted
      if (lower.endsWith('.pdf') && pptxStems.has(stem)) continue;     // same deck as pptx: keep pptx only
      if (f.locked_for_user) { skipped.push({ ...row, why: 'locked' }); continue; }
      if (f.size > MAX_BYTES) { big.push(row); continue; }
      todo.push(row);
    }
  }
  window.__todo = todo; window.__big = big; window.__skipped = skipped;
  result = JSON.stringify({ todo: todo.length, todoMB: +(todo.reduce((a, b) => a + b.size, 0) / 1048576).toFixed(1),
    big: big.length, skipped: skipped.length, unknownCourses: unknown });
}
result;
