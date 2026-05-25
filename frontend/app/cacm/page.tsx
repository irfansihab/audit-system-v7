'use client';

// Halaman CACM — C1a: ingest hasil EWS SIRUP (dari agent tim) + usulan penugasan.
// Webhook/pull live (C1b) menyusul. Sumber data = sample fixture untuk demo.

import { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { api, clearToken, getSession, Session } from '@/lib/api';

type Run = Awaited<ReturnType<typeof api.getCacmRun>>;
type Finding = Run['findings'][number];

const STATUS_CLS: Record<string, string> = {
  MERAH: 'bg-red-100 text-red-800 border-red-300',
  KUNING: 'bg-amber-100 text-amber-800 border-amber-300',
  HIJAU: 'bg-emerald-100 text-emerald-800 border-emerald-300',
  INFO: 'bg-blue-100 text-blue-800 border-blue-300',
};

function rupiah(n: number): string {
  return 'Rp ' + (n || 0).toLocaleString('id-ID');
}

export default function CacmPage() {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);
  const [session, setSession] = useState<Session | null>(null);

  const [runsMeta, setRunsMeta] = useState<Awaited<ReturnType<typeof api.getCacmRuns>>['runs']>([]);
  const [run, setRun] = useState<Run | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<number | null>(null);

  const isPT = session?.role_aktif === 'PT';

  const loadRuns = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.getCacmRuns();
      setRunsMeta(res.runs);
      if (res.runs.length > 0) {
        const detail = await api.getCacmRun(res.runs[0].id);
        setRun(detail);
      } else {
        setRun(null);
      }
      setError(null);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    setMounted(true);
    const s = getSession();
    setSession(s);
    if (!s) {
      router.push('/login');
      return;
    }
    loadRuns();
  }, [router, loadRuns]);

  const handleLogout = () => {
    clearToken();
    router.push('/login');
  };

  const selectRun = async (id: number) => {
    setBusy('run');
    try {
      setRun(await api.getCacmRun(id));
      setExpanded(null);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setBusy(null);
    }
  };

  const ingestSample = async () => {
    setBusy('ingest');
    try {
      await api.ingestCacmSample();
      await loadRuns();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setBusy(null);
    }
  };

  const promote = async (f: Finding) => {
    if (!confirm(`Jadikan finding ${f.kode} (${f.satker}) sebagai usulan penugasan?`)) return;
    setBusy(`promote-${f.id}`);
    try {
      await api.promoteFinding(f.id);
      if (run) setRun(await api.getCacmRun(run.id));
    } catch (e: any) {
      setError(e.message);
    } finally {
      setBusy(null);
    }
  };

  const dismiss = async (f: Finding) => {
    setBusy(`dismiss-${f.id}`);
    try {
      await api.dismissFinding(f.id);
      if (run) setRun(await api.getCacmRun(run.id));
    } catch (e: any) {
      setError(e.message);
    } finally {
      setBusy(null);
    }
  };

  if (!mounted) return <main className="min-h-screen" />;
  if (!session) return null;

  const s = run?.summary || {};

  return (
    <main className="min-h-screen">
      <header className="bg-primary text-white px-6 py-3 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <Link href="/penugasan" className="text-white/80 hover:text-white text-sm">
            ← Penugasan
          </Link>
          <span className="text-white/40">|</span>
          <span className="font-semibold text-sm">CACM — EWS SIRUP</span>
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
        <div className="flex justify-between items-start mb-1">
          <h1 className="text-2xl font-bold text-primary-dark">CACM — Early Warning System SIRUP</h1>
          {isPT && (
            <button
              onClick={ingestSample}
              disabled={busy === 'ingest'}
              className="px-3 py-2 text-sm rounded bg-primary text-white font-semibold hover:bg-primary-dark disabled:opacity-50"
            >
              {busy === 'ingest' ? 'Memuat…' : '＋ Muat contoh EWS'}
            </button>
          )}
        </div>
        <p className="text-sm text-gray-500 mb-4">
          Hasil evaluasi 9 skenario EWS atas data SIRUP (RUP/perencanaan). Finding MERAH/KUNING dapat
          dijadikan usulan penugasan reviu pengadaan. <span className="text-gray-400">C1a: ingest dari
          file/sample; webhook &amp; pull otomatis (C1b) menyusul.</span>
        </p>

        {error && (
          <div className="mb-4 p-3 rounded bg-red-50 border border-red-200 text-red-700 text-sm">{error}</div>
        )}

        {loading ? (
          <div className="text-gray-500 text-sm">Memuat…</div>
        ) : !run ? (
          <div className="bg-white border border-dashed border-gray-300 rounded-lg p-10 text-center text-gray-500">
            Belum ada data EWS.{' '}
            {isPT ? 'Klik "Muat contoh EWS" untuk mengisi dengan data sample.' : 'Tunggu PT mengisi data EWS.'}
          </div>
        ) : (
          <>
            {/* Run selector + summary */}
            <div className="flex flex-wrap items-center gap-3 mb-4">
              {runsMeta.length > 1 && (
                <select
                  value={run.id}
                  onChange={(e) => selectRun(Number(e.target.value))}
                  className="border border-gray-300 rounded px-2 py-1.5 text-sm"
                >
                  {runsMeta.map((r) => (
                    <option key={r.id} value={r.id}>
                      {r.run_id} ({r.tanggal_evaluasi || r.received_at?.slice(0, 10)})
                    </option>
                  ))}
                </select>
              )}
              <span className="text-xs px-2 py-1 rounded bg-gray-100">Total {s.total ?? 0}</span>
              <span className="text-xs px-2 py-1 rounded bg-red-100 text-red-800">🔴 {s.merah ?? 0} Merah</span>
              <span className="text-xs px-2 py-1 rounded bg-amber-100 text-amber-800">🟡 {s.kuning ?? 0} Kuning</span>
              <span className="text-xs px-2 py-1 rounded bg-blue-100 text-blue-800">ℹ️ {s.info ?? 0} Info</span>
              <span className="text-[11px] text-gray-400">run: {run.run_id}</span>
            </div>

            {/* Rekap per satker */}
            {run.rekap.length > 0 && (
              <div className="bg-white border border-gray-200 rounded-lg overflow-hidden mb-5">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="text-left p-2.5 text-xs uppercase text-gray-600">Satker</th>
                      <th className="text-right p-2.5 text-xs uppercase text-gray-600">Paket Penyedia</th>
                      <th className="text-right p-2.5 text-xs uppercase text-gray-600">Pagu Penyedia (juta)</th>
                      <th className="text-right p-2.5 text-xs uppercase text-gray-600">Total Pagu (juta)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {run.rekap.map((rk, i) => (
                      <tr key={i} className="border-t border-gray-100">
                        <td className="p-2.5">{rk.satker}</td>
                        <td className="p-2.5 text-right">{rk.penyedia_paket}</td>
                        <td className="p-2.5 text-right">{(rk.penyedia_pagu_juta || 0).toLocaleString('id-ID')}</td>
                        <td className="p-2.5 text-right font-medium">{(rk.total_pagu_juta || 0).toLocaleString('id-ID')}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* Findings */}
            <h2 className="text-lg font-bold text-primary-dark mb-2">Temuan EWS ({run.findings.length})</h2>
            <div className="space-y-2">
              {run.findings.map((f) => (
                <div key={f.id} className="bg-white border border-gray-200 rounded-lg">
                  <div className="flex items-start gap-3 p-3">
                    <span className={`shrink-0 px-2 py-0.5 text-xs rounded border ${STATUS_CLS[f.status] || 'bg-gray-100'}`}>
                      {f.status}
                    </span>
                    <span className="shrink-0 text-xs font-mono text-gray-500 mt-0.5">{f.kode}</span>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-gray-800">
                        {f.judul || f.ringkasan || f.kode}
                      </div>
                      <div className="text-xs text-gray-500 mt-0.5">
                        {f.satker}
                        {f.nilai_aktual ? ` · ${f.nilai_aktual}` : ''}
                      </div>
                      {f.tindak_lanjut === 'DIPROMOSIKAN' && f.penugasan_id && (
                        <Link href={`/penugasan/${f.penugasan_id}`} className="text-xs text-emerald-700 hover:underline">
                          ✓ Jadi penugasan #{f.penugasan_id} →
                        </Link>
                      )}
                      {f.tindak_lanjut === 'DIABAIKAN' && (
                        <span className="text-xs text-gray-400">✕ Diabaikan</span>
                      )}
                    </div>
                    <div className="shrink-0 flex items-center gap-2">
                      <button
                        onClick={() => setExpanded(expanded === f.id ? null : f.id)}
                        className="text-xs text-gray-500 hover:text-gray-700"
                      >
                        {expanded === f.id ? 'Tutup' : 'Detail'}
                      </button>
                      {isPT && f.promotable && f.tindak_lanjut === 'BARU' && (
                        <>
                          <button
                            onClick={() => promote(f)}
                            disabled={busy === `promote-${f.id}`}
                            className="text-xs px-2 py-1 rounded bg-primary text-white hover:bg-primary-dark disabled:opacity-50"
                          >
                            {busy === `promote-${f.id}` ? '…' : 'Jadikan usulan'}
                          </button>
                          <button
                            onClick={() => dismiss(f)}
                            disabled={busy === `dismiss-${f.id}`}
                            className="text-xs px-2 py-1 rounded border border-gray-300 text-gray-600 hover:bg-gray-50 disabled:opacity-50"
                          >
                            Abaikan
                          </button>
                        </>
                      )}
                    </div>
                  </div>

                  {expanded === f.id && (
                    <div className="border-t border-gray-100 p-3 text-sm text-gray-700 space-y-2 bg-gray-50">
                      {f.penjelasan && <p className="whitespace-pre-wrap">{f.penjelasan}</p>}
                      <div className="grid sm:grid-cols-2 gap-x-6 gap-y-1 text-xs">
                        {f.threshold && <div><span className="text-gray-400">Threshold:</span> {f.threshold}</div>}
                        <div><span className="text-gray-400">Paket terdampak:</span> {f.jumlah_paket_terdampak} · {rupiah(f.total_nilai_terdampak)}</div>
                        {f.regulasi && <div className="sm:col-span-2"><span className="text-gray-400">Regulasi:</span> {f.regulasi}</div>}
                        {f.rekomendasi && <div className="sm:col-span-2"><span className="text-gray-400">Rekomendasi EWS:</span> {f.rekomendasi}</div>}
                      </div>
                      {f.paket_detail.length > 0 && (
                        <div className="mt-1">
                          <div className="text-xs text-gray-400 mb-1">Paket terdampak ({f.paket_detail.length}):</div>
                          <div className="space-y-0.5">
                            {f.paket_detail.slice(0, 15).map((p, i) => (
                              <div key={i} className="text-xs font-mono bg-white border border-gray-200 rounded px-2 py-1">
                                {p.nama || p.nama_paket} — {rupiah(p.pagu)} ({p.metode}, {p.jenis})
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </main>
  );
}
