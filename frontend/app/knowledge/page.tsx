'use client';

// Halaman Knowledge / Wiki.
// W1 (AKTIF): panel "Cari Wiki" — baca vault pengetahuan organisasi (read-only).
// W2/W3 (scaffold): promosi pattern + tulis-balik penugasan ke wiki — substansi menyusul.

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { api, clearToken, getSession, Session, SkillInfo } from '@/lib/api';

type SearchResult = {
  name: string;
  section: string;
  summary: string;
  path: string;
  score: number;
  snippet: string;
};

type PatternCandidate = {
  judul: string;
  id_proposed: string;
  count: number;
  rationales: string[];
  skills: Record<string, number>;
  suggested_skill: string;
  penugasan: { folder: string; obyek: string; skill: string }[];
  already_exists: boolean;
  existing_id: string | null;
};

const SECTIONS = [
  {
    title: 'Tulis-balik Penugasan (W3)',
    desc: 'Saat penugasan selesai, hasilkan draft catatan wiki (temuan + rekomendasi) untuk disetujui & di-apply ke vault.',
  },
];

export default function KnowledgePage() {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);
  const [session, setSession] = useState<Session | null>(null);

  // Cari Wiki (W1)
  const [q, setQ] = useState('');
  const [searching, setSearching] = useState(false);
  const [results, setResults] = useState<SearchResult[] | null>(null);
  const [notConfigured, setNotConfigured] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Preview catatan
  const [selected, setSelected] = useState<string | null>(null);
  const [pageContent, setPageContent] = useState<string>('');
  const [loadingPage, setLoadingPage] = useState(false);

  useEffect(() => {
    setMounted(true);
    const s = getSession();
    setSession(s);
    if (!s) router.push('/login');
  }, [router]);

  const handleLogout = () => {
    clearToken();
    router.push('/login');
  };

  const runSearch = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!q.trim()) return;
    setSearching(true);
    setError(null);
    setNotConfigured(null);
    setSelected(null);
    setPageContent('');
    try {
      const res = await api.searchWiki(q.trim(), 20);
      if (!res.configured) {
        setNotConfigured(res.message || 'Vault tidak dikonfigurasi (set APP_VAULT_PATH).');
        setResults([]);
      } else {
        setResults(res.results);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setSearching(false);
    }
  };

  const openPage = async (name: string) => {
    setSelected(name);
    setLoadingPage(true);
    setPageContent('');
    try {
      const res = await api.getWikiPage(name);
      setPageContent(res.found ? (res.content || '') : (res.message || 'Catatan tidak ditemukan.'));
    } catch (err: any) {
      setPageContent(`Gagal memuat: ${err.message}`);
    } finally {
      setLoadingPage(false);
    }
  };

  if (!mounted) return <main className="min-h-screen" />;
  if (!session) return null;

  return (
    <main className="min-h-screen">
      <header className="bg-primary text-white px-6 py-3 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <Link href="/penugasan" className="text-white/80 hover:text-white text-sm">
            ← Penugasan
          </Link>
          <span className="text-white/40">|</span>
          <span className="font-semibold text-sm">Knowledge — Wiki &amp; Pattern Temuan</span>
        </div>
        <div className="text-right text-xs">
          <div>{session.user.nama_lengkap}</div>
          <div className="opacity-80">
            <span className="px-2 py-0.5 rounded bg-white/15 ml-2">{session.role_aktif}</span>
            <button onClick={handleLogout} className="ml-3 underline">
              Keluar
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto p-6">
        <h1 className="text-2xl font-bold text-primary-dark mb-1">Knowledge / Wiki</h1>
        <p className="text-sm text-gray-500 mb-5">
          Cari di vault pengetahuan organisasi (dokumen resmi non-rahasia, hasil ingest). Agen juga
          memakai pencarian ini untuk menarik konteks auditi/vendor/BPK saat analisis.
        </p>

        {/* ===== W1: Cari Wiki ===== */}
        <div className="bg-white border border-gray-200 rounded-lg p-5 mb-6">
          <form onSubmit={runSearch} className="flex gap-2">
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="mis. temuan BPK PSTE, profil Ditjen Ekosdig, vendor …"
              className="flex-1 border border-gray-300 rounded px-3 py-2 text-sm"
            />
            <button
              type="submit"
              disabled={searching || !q.trim()}
              className="px-4 py-2 rounded bg-primary text-white text-sm font-semibold hover:bg-primary-dark disabled:opacity-40"
            >
              {searching ? 'Mencari…' : 'Cari'}
            </button>
          </form>

          {error && (
            <div className="mt-3 p-2 rounded bg-red-50 border border-red-200 text-red-700 text-sm">{error}</div>
          )}
          {notConfigured && (
            <div className="mt-3 p-2 rounded bg-amber-50 border border-amber-200 text-amber-800 text-sm">
              {notConfigured}
            </div>
          )}

          {results && (
            <div className="mt-4 grid md:grid-cols-2 gap-4">
              {/* Daftar hasil */}
              <div className="space-y-2 max-h-[460px] overflow-y-auto">
                {results.length === 0 && !notConfigured ? (
                  <p className="text-sm text-gray-400 italic">Tidak ada hasil untuk "{q}".</p>
                ) : (
                  results.map((r) => (
                    <button
                      key={r.path}
                      onClick={() => openPage(r.name)}
                      className={`w-full text-left border rounded p-3 hover:bg-gray-50 transition ${
                        selected === r.name ? 'border-primary bg-blue-50/40' : 'border-gray-200'
                      }`}
                    >
                      <div className="flex justify-between items-baseline gap-2">
                        <span className="font-medium text-sm text-primary-dark">{r.name}</span>
                        {r.section && (
                          <span className="text-[11px] text-gray-400 shrink-0">{r.section}</span>
                        )}
                      </div>
                      {r.summary && <div className="text-xs text-gray-600 mt-0.5">{r.summary}</div>}
                      {r.snippet && (
                        <div className="text-xs text-gray-400 mt-1 line-clamp-2">…{r.snippet}</div>
                      )}
                    </button>
                  ))
                )}
              </div>

              {/* Preview catatan */}
              <div className="border border-gray-200 rounded p-3 bg-gray-50 max-h-[460px] overflow-y-auto">
                {!selected ? (
                  <p className="text-sm text-gray-400 italic">Klik salah satu hasil untuk membaca isinya.</p>
                ) : loadingPage ? (
                  <p className="text-sm text-gray-400 italic">Memuat {selected}…</p>
                ) : (
                  <>
                    <div className="text-xs font-semibold text-gray-500 mb-2">{selected}.md</div>
                    <pre className="text-xs whitespace-pre-wrap font-sans text-gray-800">{pageContent}</pre>
                  </>
                )}
              </div>
            </div>
          )}
        </div>

        {/* ===== W2: Promosi Pattern (PT/PM) ===== */}
        {(session.role_aktif === 'PT' || session.role_aktif === 'PM') && <PatternMonitorPanel />}

        {/* ===== Graduasi (PT/PM) ===== */}
        {(session.role_aktif === 'PT' || session.role_aktif === 'PM') && <GraduasiPanel />}

        {/* ===== W3 scaffold ===== */}
        <div className="mb-3 text-sm text-gray-500">Berikutnya (substansi menyusul):</div>
        <div className="grid gap-4 md:grid-cols-2">
          {SECTIONS.map((s) => (
            <div key={s.title} className="bg-white border border-dashed border-gray-300 rounded-lg p-5">
              <h2 className="font-semibold text-primary-dark mb-2">{s.title}</h2>
              <p className="text-sm text-gray-500">{s.desc}</p>
              <div className="mt-3 text-xs text-gray-400 italic">Substansi menyusul.</div>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}

// Panel Promosi Pattern (PT/PM): pantau usulan pattern dari feedback agen lintas
// penugasan, lalu promote yang berulang jadi pattern wiki resmi. Human-in-the-loop.
type PromoteForm = {
  skill: string;
  pattern_id: string;
  judul: string;
  kategori: string;
  severity: string;
  kriteria_baku: string;
  kondisi: string;
  akibat: string;
  rekomendasi: string;
  bukti: string;
  tags: string;
  sumber_penugasan: string[];
};

const EMPTY_FORM: PromoteForm = {
  skill: '', pattern_id: '', judul: '', kategori: '', severity: 'MEDIUM',
  kriteria_baku: '', kondisi: '', akibat: '', rekomendasi: '', bukti: '', tags: '', sumber_penugasan: [],
};

function PatternMonitorPanel() {
  const [candidates, setCandidates] = useState<PatternCandidate[]>([]);
  const [skills, setSkills] = useState<SkillInfo[]>([]);
  const [totalSug, setTotalSug] = useState(0);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState<PromoteForm | null>(null);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  const refresh = () => {
    setLoading(true);
    api.getPatternMonitor(90)
      .then((r) => { setCandidates(r.candidates); setTotalSug(r.total_suggestions); })
      .catch(() => {})
      .finally(() => setLoading(false));
  };
  useEffect(() => {
    refresh();
    api.getSkills().then(setSkills).catch(() => {});
  }, []);

  const openFromCandidate = (c: PatternCandidate) => {
    setMsg(null);
    setForm({
      ...EMPTY_FORM,
      skill: c.suggested_skill || '',
      pattern_id: c.already_exists ? '' : c.id_proposed,
      judul: c.judul,
      kondisi: c.rationales.join('\n'),
      sumber_penugasan: c.penugasan.map((p) => p.obyek).filter(Boolean),
    });
  };

  const setField = (k: keyof PromoteForm, v: string) =>
    setForm((f) => (f ? { ...f, [k]: v } : f));

  const submit = async () => {
    if (!form) return;
    if (!form.skill || !form.pattern_id.trim() || !form.judul.trim()) {
      setMsg('Skill, ID pattern, dan judul wajib.');
      return;
    }
    setBusy(true); setMsg(null);
    try {
      const r = await api.promotePattern({
        skill: form.skill,
        pattern_id: form.pattern_id.trim(),
        judul: form.judul.trim(),
        kategori: form.kategori.trim(),
        severity: form.severity,
        kriteria_baku: form.kriteria_baku.trim(),
        kondisi: form.kondisi.trim(),
        akibat: form.akibat.trim(),
        rekomendasi: form.rekomendasi.trim(),
        bukti: form.bukti.trim(),
        tags: form.tags.split(',').map((t) => t.trim()).filter(Boolean),
        sumber_penugasan: form.sumber_penugasan,
      });
      setMsg(`Pattern ${r.id} ditulis ke ${r.file}${r.readme_updated ? ' (index README diperbarui)' : ''}.`);
      setForm(null);
      refresh();
    } catch (e: any) { setMsg(e.message); } finally { setBusy(false); }
  };

  return (
    <div className="mb-6 bg-white border border-emerald-200 rounded-lg p-5">
      <div className="flex items-center justify-between mb-1">
        <h2 className="font-semibold text-primary-dark">Promosi Pattern (PT/PM)</h2>
        <button
          onClick={() => { setMsg(null); setForm({ ...EMPTY_FORM }); }}
          className="text-[11px] px-2 py-0.5 rounded border border-emerald-300 text-emerald-700 hover:bg-emerald-50"
        >
          + Pattern manual
        </button>
      </div>
      <p className="text-xs text-gray-500 mb-3">
        Usulan pattern dari feedback agen lintas penugasan (90 hari). Yang <b>berulang</b> &amp;
        belum ada di wiki = kandidat kuat. Klik kandidat untuk menyunting lalu <b>Promote</b> jadi
        pattern resmi. {totalSug > 0 && <span className="text-gray-400">({totalSug} usulan mentah)</span>}
      </p>
      {msg && <div className="mb-3 p-2 rounded bg-emerald-50 text-emerald-800 text-xs">{msg}</div>}

      {form ? (
        <PromoteFormView
          form={form} skills={skills} busy={busy}
          onField={setField} onCancel={() => setForm(null)} onSubmit={submit}
        />
      ) : (
        <div className="border border-gray-200 rounded max-h-80 overflow-y-auto divide-y">
          {loading ? (
            <div className="p-3 text-xs text-gray-400 italic">Memuat kandidat…</div>
          ) : candidates.length === 0 ? (
            <div className="p-3 text-xs text-gray-400 italic">
              Belum ada usulan pattern dari feedback agen. Jalankan agen AT/KT — usulan muncul di sini.
            </div>
          ) : candidates.map((c) => (
            <button
              key={c.judul}
              onClick={() => openFromCandidate(c)}
              className="w-full text-left p-3 hover:bg-emerald-50/40 transition"
            >
              <div className="flex items-start justify-between gap-2">
                <span className="text-sm font-medium text-gray-800">{c.judul}</span>
                <span className="flex items-center gap-1 shrink-0">
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-gray-100 text-gray-600">×{c.count}</span>
                  {c.already_exists ? (
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-100 text-amber-700">sudah ada: {c.existing_id}</span>
                  ) : c.id_proposed ? (
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-700">{c.id_proposed}</span>
                  ) : null}
                </span>
              </div>
              <div className="text-[11px] text-gray-400 mt-0.5">
                {c.suggested_skill && <span className="uppercase">{c.suggested_skill}</span>}
                {c.penugasan.length > 0 && <span> · {c.penugasan.length} penugasan</span>}
              </div>
              {c.rationales[0] && <div className="text-xs text-gray-500 mt-1 line-clamp-2">{c.rationales[0]}</div>}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function PromoteFormView({
  form, skills, busy, onField, onCancel, onSubmit,
}: {
  form: PromoteForm;
  skills: SkillInfo[];
  busy: boolean;
  onField: (k: keyof PromoteForm, v: string) => void;
  onCancel: () => void;
  onSubmit: () => void;
}) {
  const inp = 'w-full border border-gray-300 rounded px-2 py-1.5 text-xs';
  const lbl = 'block text-[11px] font-semibold text-gray-600 mb-0.5';
  return (
    <div className="border border-gray-200 rounded p-3 space-y-2.5">
      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className={lbl}>Skill (folder target) *</label>
          <select value={form.skill} onChange={(e) => onField('skill', e.target.value)} className={inp}>
            <option value="">— pilih skill —</option>
            {skills.map((s) => <option key={s.slug} value={s.slug}>{s.slug}</option>)}
          </select>
        </div>
        <div>
          <label className={lbl}>ID Pattern * (mis. RP-17)</label>
          <input value={form.pattern_id} onChange={(e) => onField('pattern_id', e.target.value)} className={inp} placeholder="RP-17" />
        </div>
      </div>
      <div>
        <label className={lbl}>Judul *</label>
        <input value={form.judul} onChange={(e) => onField('judul', e.target.value)} className={inp} />
      </div>
      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className={lbl}>Kategori</label>
          <input value={form.kategori} onChange={(e) => onField('kategori', e.target.value)} className={inp} placeholder="mis. PBJ-KONTRAK" />
        </div>
        <div>
          <label className={lbl}>Severity</label>
          <select value={form.severity} onChange={(e) => onField('severity', e.target.value)} className={inp}>
            {['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO'].map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
      </div>
      <div>
        <label className={lbl}>Kriteria Baku (sebut pasal/ayat)</label>
        <input value={form.kriteria_baku} onChange={(e) => onField('kriteria_baku', e.target.value)} className={inp} placeholder="mis. Perpres 16/2018 Pasal 26 ayat (5)" />
      </div>
      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className={lbl}>Kondisi</label>
          <textarea value={form.kondisi} onChange={(e) => onField('kondisi', e.target.value)} className={inp} rows={3} />
        </div>
        <div>
          <label className={lbl}>Akibat</label>
          <textarea value={form.akibat} onChange={(e) => onField('akibat', e.target.value)} className={inp} rows={3} />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className={lbl}>Bukti yang dicari</label>
          <textarea value={form.bukti} onChange={(e) => onField('bukti', e.target.value)} className={inp} rows={2} />
        </div>
        <div>
          <label className={lbl}>Rekomendasi</label>
          <textarea value={form.rekomendasi} onChange={(e) => onField('rekomendasi', e.target.value)} className={inp} rows={2} />
        </div>
      </div>
      <div>
        <label className={lbl}>Tags (pisahkan koma)</label>
        <input value={form.tags} onChange={(e) => onField('tags', e.target.value)} className={inp} placeholder="kontrak, sla, denda" />
      </div>
      {form.sumber_penugasan.length > 0 && (
        <div className="text-[11px] text-gray-400">Sumber: {form.sumber_penugasan.join(', ')}</div>
      )}
      <div className="flex gap-2 pt-1">
        <button onClick={onSubmit} disabled={busy} className="text-xs px-3 py-1.5 rounded bg-emerald-600 text-white font-medium disabled:opacity-50">
          {busy ? 'Menyimpan…' : 'Promote ke Wiki'}
        </button>
        <button onClick={onCancel} disabled={busy} className="text-xs px-3 py-1.5 rounded border border-gray-300 text-gray-600 disabled:opacity-50">
          Batal
        </button>
      </div>
    </div>
  );
}

// Panel Graduasi (PT/PM): pilih penugasan sejenis → suling jadi DRAFT skill →
// reviu → promote ke registry. Human-in-the-loop.
function GraduasiPanel() {
  const [groups, setGroups] = useState<{ skill: string; penugasan: { kode: string; obyek: string; n_temuan: number }[] }[]>([]);
  const [drafts, setDrafts] = useState<{ nama: string; skill_induk?: string; n_temuan?: number }[]>([]);
  const [picked, setPicked] = useState<Record<string, boolean>>({});
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  const refresh = () => {
    api.getGraduasiCandidates().then((r) => setGroups(r.groups)).catch(() => {});
    api.getGraduasiDrafts().then((r) => setDrafts(r.drafts)).catch(() => {});
  };
  useEffect(() => { refresh(); }, []);

  const toggle = (kode: string) => setPicked((p) => ({ ...p, [kode]: !p[kode] }));
  const selected = Object.keys(picked).filter((k) => picked[k]);

  const run = async () => {
    if (selected.length === 0) { setMsg('Pilih ≥1 penugasan dulu.'); return; }
    setBusy(true); setMsg(null);
    try {
      const r = await api.runGraduasi(selected);
      setMsg(`Draft "${r.nama}" dibuat (${r.n_temuan} temuan, ${r.n_redflag} pola). Reviu lalu Promote.`);
      setPicked({}); refresh();
    } catch (e: any) { setMsg(e.message); } finally { setBusy(false); }
  };
  const act = async (nama: string, kind: 'promote' | 'reject') => {
    if (kind === 'reject' && !confirm(`Tolak & hapus draft "${nama}"?`)) return;
    if (kind === 'promote' && !confirm(`Promote draft "${nama}" jadi skill aktif di registry?`)) return;
    setBusy(true); setMsg(null);
    try {
      if (kind === 'promote') { await api.promoteGraduasi(nama); setMsg(`Skill "${nama}" dipromote & terdaftar.`); }
      else { await api.rejectGraduasi(nama); setMsg(`Draft "${nama}" ditolak.`); }
      refresh();
    } catch (e: any) { setMsg(e.message); } finally { setBusy(false); }
  };

  return (
    <div className="mb-6 bg-white border border-violet-200 rounded-lg p-5">
      <h2 className="font-semibold text-primary-dark mb-1">Graduasi Skill (PT/PM)</h2>
      <p className="text-xs text-gray-500 mb-3">
        Suling pola dari penugasan sejenis (skill sama) menjadi DRAFT skill spesifik. Generate = draft;
        Anda reviu lalu <b>Promote</b> agar terdaftar. Human-in-the-loop.
      </p>
      {msg && <div className="mb-3 p-2 rounded bg-violet-50 text-violet-800 text-xs">{msg}</div>}

      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <div className="text-xs font-semibold text-gray-600 mb-1">Kandidat penugasan (punya temuan)</div>
          <div className="border border-gray-200 rounded max-h-60 overflow-y-auto divide-y">
            {groups.length === 0 ? (
              <div className="p-3 text-xs text-gray-400 italic">Belum ada penugasan ber-temuan.</div>
            ) : groups.map((g) => (
              <div key={g.skill} className="p-2">
                <div className="text-[11px] uppercase text-gray-400 mb-1">{g.skill}</div>
                {g.penugasan.map((p) => (
                  <label key={p.kode} className="flex items-start gap-2 text-xs py-0.5 cursor-pointer">
                    <input type="checkbox" checked={!!picked[p.kode]} onChange={() => toggle(p.kode)} className="mt-0.5" />
                    <span className="text-gray-700">{p.obyek} <span className="text-gray-400">({p.n_temuan} temuan)</span></span>
                  </label>
                ))}
              </div>
            ))}
          </div>
          <button onClick={run} disabled={busy} className="mt-2 text-xs px-3 py-1.5 rounded bg-violet-600 text-white font-medium disabled:opacity-50">
            ⚗ Graduasikan {selected.length > 0 ? `(${selected.length})` : ''}
          </button>
        </div>

        <div>
          <div className="text-xs font-semibold text-gray-600 mb-1">Draft skill (perlu reviu)</div>
          <div className="border border-gray-200 rounded max-h-60 overflow-y-auto divide-y">
            {drafts.length === 0 ? (
              <div className="p-3 text-xs text-gray-400 italic">Belum ada draft.</div>
            ) : drafts.map((d) => (
              <div key={d.nama} className="p-2 flex items-center justify-between gap-2">
                <span className="text-xs text-gray-700">{d.nama} <span className="text-gray-400">← {d.skill_induk}</span></span>
                <span className="flex gap-1 shrink-0">
                  <button onClick={() => act(d.nama, 'promote')} disabled={busy} className="text-[11px] px-2 py-0.5 rounded bg-emerald-600 text-white disabled:opacity-50">Promote</button>
                  <button onClick={() => act(d.nama, 'reject')} disabled={busy} className="text-[11px] px-2 py-0.5 rounded bg-gray-400 text-white disabled:opacity-50">Tolak</button>
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
