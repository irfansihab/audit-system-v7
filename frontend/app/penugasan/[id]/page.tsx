'use client';

import { useEffect, useState, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { api, getSession, Dokumen, Penugasan } from '@/lib/api';

type Tab = 'dokumen' | 'chat' | 'output';

export default function DetailPenugasanPage() {
  const params = useParams();
  const router = useRouter();
  const id = Number(params.id);
  const session = getSession();

  const [penugasan, setPenugasan] = useState<Penugasan | null>(null);
  const [dokumen, setDokumen] = useState<Dokumen[]>([]);
  const [tab, setTab] = useState<Tab>('dokumen');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!session) {
      router.push('/login');
      return;
    }
    Promise.all([api.getPenugasan(id), api.listDokumen(id)])
      .then(([p, d]) => {
        setPenugasan(p);
        setDokumen(d);
      })
      .catch((e) => setError(e.message));
  }, [id, router]);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;
    for (const f of Array.from(files)) {
      try {
        const d = await api.uploadDokumen(id, f);
        setDokumen((prev) => [...prev, d]);
      } catch (err: any) {
        setError(err.message);
      }
    }
    e.target.value = '';
  };

  const triggerIngest = async () => {
    try {
      await api.triggerIngestion(id);
      // refresh list
      const d = await api.listDokumen(id);
      setDokumen(d);
    } catch (e: any) {
      setError(e.message);
    }
  };

  if (!session || !penugasan) return null;

  const allReady = dokumen.length > 0 && dokumen.every((d) => d.status === 'READY');

  return (
    <main className="min-h-screen">
      <header className="bg-primary text-white px-6 py-3 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <Link href="/penugasan" className="text-white/80 hover:text-white text-sm">
            ← Penugasan
          </Link>
          <span className="text-white/40">|</span>
          <span className="font-semibold text-sm">{penugasan.obyek}</span>
        </div>
        <div className="text-xs">
          {session.user.nama_lengkap}{' '}
          <span className="px-2 py-0.5 rounded bg-white/15 ml-2">{session.role_aktif}</span>
        </div>
      </header>

      <div className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-6 flex gap-1">
          {(['dokumen', 'chat', 'output'] as Tab[]).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`px-4 py-3 text-sm border-b-2 transition ${
                tab === t
                  ? 'border-primary text-primary-dark font-semibold'
                  : 'border-transparent text-gray-500 hover:text-primary-dark'
              }`}
            >
              {t === 'dokumen' && 'Dokumen'}
              {t === 'chat' && (session.role_aktif === 'AT' ? 'Chat AT' : 'Chat KT')}
              {t === 'output' && 'Output & QC'}
            </button>
          ))}
        </div>
      </div>

      <div className="max-w-6xl mx-auto p-6">
        {error && (
          <div className="mb-4 p-3 rounded bg-red-50 border border-red-200 text-red-700 text-sm">
            {error}
          </div>
        )}

        {tab === 'dokumen' && (
          <DokumenTab
            dokumen={dokumen}
            onUpload={handleUpload}
            onIngest={triggerIngest}
            allReady={allReady}
          />
        )}

        {tab === 'chat' && <ChatTab penugasanId={id} role={session.role_aktif} skill={penugasan.skill} />}

        {tab === 'output' && <OutputTab penugasan={penugasan} />}
      </div>
    </main>
  );
}

function DokumenTab({
  dokumen,
  onUpload,
  onIngest,
  allReady,
}: {
  dokumen: Dokumen[];
  onUpload: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onIngest: () => void;
  allReady: boolean;
}) {
  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold text-primary-dark">Dokumen Penugasan</h2>
        <div className="flex gap-2">
          <label className="px-4 py-2 rounded bg-primary text-white text-sm font-semibold cursor-pointer hover:bg-primary-dark">
            + Upload
            <input type="file" multiple onChange={onUpload} className="hidden" />
          </label>
          <button
            onClick={onIngest}
            disabled={dokumen.length === 0}
            className="px-4 py-2 rounded bg-ing text-white text-sm font-semibold hover:opacity-90 disabled:opacity-40"
          >
            Mulai Ingestion
          </button>
        </div>
      </div>

      {dokumen.length === 0 ? (
        <div className="bg-white border border-dashed border-gray-300 rounded-lg p-10 text-center text-gray-500">
          Belum ada dokumen. Upload TOR/RAB (Reviu RKA-K/L) atau KAK/HPS/RFI/Kontrak (Reviu Pengadaan).
        </div>
      ) : (
        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left p-3 text-xs uppercase text-gray-600">Nama File</th>
                <th className="text-left p-3 text-xs uppercase text-gray-600">Jenis</th>
                <th className="text-left p-3 text-xs uppercase text-gray-600">Status</th>
                <th className="text-left p-3 text-xs uppercase text-gray-600">Output</th>
              </tr>
            </thead>
            <tbody>
              {dokumen.map((d) => (
                <tr key={d.id} className="border-t border-gray-100">
                  <td className="p-3">{d.nama_file}</td>
                  <td className="p-3">
                    <span className="px-2 py-0.5 text-xs rounded bg-gray-100">{d.jenis}</span>
                  </td>
                  <td className="p-3">
                    <StatusBadge status={d.status} />
                  </td>
                  <td className="p-3 text-xs text-gray-500">
                    {d.ingested_json_path ? d.ingested_json_path.split('/').pop() : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {allReady && (
        <div className="mt-4 p-3 rounded bg-green-50 border border-green-200 text-green-700 text-sm">
          ✓ Semua dokumen siap dianalisis. Buka tab <strong>Chat AT</strong> untuk memulai analisis.
        </div>
      )}
    </div>
  );
}

function StatusBadge({ status }: { status: Dokumen['status'] }) {
  const map = {
    UPLOADED: 'bg-gray-100 text-gray-700',
    INGESTING: 'bg-yellow-50 text-yellow-700',
    READY: 'bg-green-50 text-green-700',
    FAILED: 'bg-red-50 text-red-700',
  } as const;
  return (
    <span className={`px-2 py-0.5 text-xs rounded ${map[status]}`}>
      {status === 'UPLOADED' && 'Antri'}
      {status === 'INGESTING' && '⟳ Mengekstrak…'}
      {status === 'READY' && '✓ Siap'}
      {status === 'FAILED' && '✗ Gagal'}
    </span>
  );
}

function ChatTab({
  penugasanId,
  role,
  skill,
}: {
  penugasanId: number;
  role: string;
  skill: string;
}) {
  const [prompt, setPrompt] = useState(
    role === 'AT'
      ? `Mulai analisis ${skill} untuk penugasan ini. Jalankan pipeline V6 dan verifikasi anomali.`
      : 'Susun draft LHR dari temuan.json yang sudah disetujui anggota tim.'
  );
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<{
    output: string;
    tool_calls: Array<{ tool: string; input: any }>;
    error: string | null;
  } | null>(null);
  const [elapsed, setElapsed] = useState(0);

  const start = async () => {
    setResult(null);
    setRunning(true);
    setElapsed(0);
    const startTime = Date.now();
    const timer = setInterval(() => setElapsed(Math.floor((Date.now() - startTime) / 1000)), 1000);

    try {
      const agent = role === 'AT' ? 'anggota_tim' : 'ketua_tim';
      const res = await api.runAgent(agent as any, penugasanId, prompt);
      setResult({ output: res.output, tool_calls: res.tool_calls, error: res.error });
    } catch (e: any) {
      setResult({ output: '', tool_calls: [], error: e.message });
    } finally {
      clearInterval(timer);
      setRunning(false);
    }
  };

  return (
    <div>
      <h2 className="text-lg font-bold text-primary-dark mb-3">
        {role === 'AT' ? 'Chat dengan Agen Anggota Tim' : 'Chat dengan Agen Ketua Tim'}
      </h2>

      <div className="bg-white border border-gray-200 rounded-lg p-4 mb-3 min-h-[300px] max-h-[600px] overflow-y-auto">
        {!result && !running && (
          <p className="text-gray-400 text-sm italic">Belum ada hasil…</p>
        )}
        {running && (
          <div className="flex items-center gap-2 text-blue-600">
            <span className="inline-block w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></span>
            <span className="text-sm">Agen sedang bekerja… ({elapsed}s)</span>
          </div>
        )}
        {result?.error && (
          <div className="bg-red-50 border border-red-200 rounded p-3 text-red-700 text-sm">
            Error: {result.error}
          </div>
        )}
        {result?.output && (
          <div className="bg-gray-50 rounded-lg p-3 text-sm whitespace-pre-wrap mb-3">
            {result.output}
          </div>
        )}
        {result?.tool_calls && result.tool_calls.length > 0 && (
          <details className="mt-3">
            <summary className="text-xs uppercase text-gray-500 font-semibold cursor-pointer hover:text-gray-700 select-none">
              Audit trail · {result.tool_calls.length} tool call{result.tool_calls.length === 1 ? '' : 's'} (klik untuk buka)
            </summary>
            <div className="mt-2">
              {result.tool_calls.map((tc, i) => (
                <div key={i} className="bg-yellow-50 border-l-2 border-accent rounded-r-lg p-2 text-xs font-mono mb-1">
                  → {tc.tool}({JSON.stringify(tc.input).slice(0, 120)}…)
                </div>
              ))}
            </div>
          </details>
        )}
      </div>

      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        className="w-full border border-gray-300 rounded-lg p-3 text-sm h-24"
        placeholder="Tulis perintah ke agen…"
        disabled={running}
      />
      <div className="mt-2 flex gap-2">
        <button
          onClick={start}
          disabled={running}
          className="px-4 py-2 rounded bg-primary text-white text-sm font-semibold hover:bg-primary-dark disabled:opacity-40"
        >
          {running ? `⟳ Berjalan (${elapsed}s)…` : '▶ Jalankan'}
        </button>
      </div>
      <p className="mt-2 text-xs text-gray-500">
        Catatan: agen butuh 30–90 detik untuk selesai. Tombol akan aktif kembali setelah respons masuk.
      </p>
    </div>
  );
}
type FileEntry = {
  name: string;
  path: string;
  size_bytes: number;
  mtime: string;
  ext: string;
};

type FileCategory = {
  key: string;
  label: string;
  files: FileEntry[];
};

function formatBytes(n: number): string {
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / 1024 / 1024).toFixed(1)} MB`;
}

function formatTime(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleString('id-ID', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return iso;
  }
}

function iconForExt(ext: string): string {
  switch (ext) {
    case '.docx':
      return '📄';
    case '.pdf':
      return '📕';
    case '.json':
    case '.jsonl':
      return '🔧';
    case '.md':
      return '📝';
    case '.xlsx':
    case '.csv':
      return '📊';
    case '.txt':
    case '.log':
      return '📃';
    default:
      return '📎';
  }
}

const PREVIEWABLE = new Set(['.md', '.json', '.jsonl', '.txt', '.csv', '.log']);

function OutputTab({ penugasan }: { penugasan: Penugasan }) {
  const [categories, setCategories] = useState<FileCategory[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [preview, setPreview] = useState<{ path: string; content: string; truncated: boolean } | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);

  const fetchFiles = async () => {
    setLoading(true);
    try {
      const res = await api.listFiles(penugasan.id);
      setCategories(res.categories);
      setError(null);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFiles();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [penugasan.id]);

  const handleDownload = async (file: FileEntry) => {
    try {
      const blob = await api.downloadFile(penugasan.id, file.path);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = file.name;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (e: any) {
      setError(e.message);
    }
  };

  const handlePreview = async (file: FileEntry) => {
    setPreviewLoading(true);
    try {
      const res = await api.previewFile(penugasan.id, file.path);
      setPreview({ path: res.path, content: res.content, truncated: res.truncated });
    } catch (e: any) {
      setError(e.message);
    } finally {
      setPreviewLoading(false);
    }
  };

  const isEmpty = !loading && (categories === null || categories.length === 0);

  return (
    <div>
      <div className="flex justify-between items-center mb-3">
        <h2 className="text-lg font-bold text-primary-dark">Output &amp; Laporan QC</h2>
        <button
          onClick={fetchFiles}
          className="px-3 py-1.5 text-xs rounded border border-gray-300 hover:bg-gray-50"
          disabled={loading}
        >
          {loading ? 'Memuat…' : '↻ Refresh'}
        </button>
      </div>

      {error && (
        <div className="mb-4 p-3 rounded bg-red-50 border border-red-200 text-red-700 text-sm">
          {error}
        </div>
      )}

      {loading && (
        <div className="bg-white border border-gray-200 rounded-lg p-5 text-sm text-gray-500">
          Memuat daftar file…
        </div>
      )}

      {isEmpty && (
        <div className="bg-white border border-gray-200 rounded-lg p-5 text-sm text-gray-600">
          <p className="mb-2">
            Belum ada file output. Jalankan agen di tab <strong>Chat</strong> untuk men-generate KKP, LHR, laporan QA.
          </p>
          <p className="text-xs text-gray-500">
            Folder server: <code className="bg-gray-100 px-1 rounded">{penugasan.folder_path}</code>
          </p>
        </div>
      )}

      {!loading && categories && categories.length > 0 && (
        <div className="space-y-4">
          {categories.map((cat) => (
            <div key={cat.key} className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <div className="bg-gray-50 px-4 py-2 border-b border-gray-200 flex justify-between items-center">
                <div>
                  <span className="font-semibold text-sm text-primary-dark">{cat.label}</span>
                  <span className="ml-2 text-xs text-gray-500">({cat.files.length} file)</span>
                </div>
                <code className="text-xs text-gray-400">{cat.key}</code>
              </div>
              <table className="w-full text-sm">
                <tbody>
                  {cat.files.map((f) => (
                    <tr key={f.path} className="border-b border-gray-100 last:border-0 hover:bg-gray-50">
                      <td className="px-4 py-2 w-8 text-base">{iconForExt(f.ext)}</td>
                      <td className="px-2 py-2">
                        <div className="font-medium">{f.name}</div>
                        <div className="text-xs text-gray-400 font-mono">{f.path}</div>
                      </td>
                      <td className="px-2 py-2 text-xs text-gray-500 whitespace-nowrap">
                        {formatBytes(f.size_bytes)}
                      </td>
                      <td className="px-2 py-2 text-xs text-gray-500 whitespace-nowrap">
                        {formatTime(f.mtime)}
                      </td>
                      <td className="px-2 py-2 text-right whitespace-nowrap">
                        {PREVIEWABLE.has(f.ext) && (
                          <button
                            onClick={() => handlePreview(f)}
                            className="text-xs px-2 py-1 rounded border border-gray-300 hover:bg-gray-100 mr-1"
                            disabled={previewLoading}
                          >
                            Preview
                          </button>
                        )}
                        <button
                          onClick={() => handleDownload(f)}
                          className="text-xs px-2 py-1 rounded bg-primary text-white hover:bg-primary-dark"
                        >
                          Download
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ))}
        </div>
      )}

      {preview && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-6 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[85vh] flex flex-col">
            <div className="flex justify-between items-center px-5 py-3 border-b border-gray-200">
              <div className="font-mono text-sm">{preview.path}</div>
              <button
                onClick={() => setPreview(null)}
                className="text-gray-500 hover:text-gray-800 text-xl"
                aria-label="Tutup preview"
              >
                ×
              </button>
            </div>
            <pre className="flex-1 overflow-auto p-5 text-xs whitespace-pre-wrap font-mono bg-gray-50">
              {preview.content}
            </pre>
            {preview.truncated && (
              <div className="px-5 py-2 text-xs text-amber-700 bg-amber-50 border-t border-amber-200">
                File besar — hanya 50 KB awal yang ditampilkan. Klik Download untuk file lengkap.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
