"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { 
  FileText, Search, Filter, Calendar, ArrowRight,
  Clock, CheckCircle, AlertTriangle, ShieldAlert
} from "lucide-react";
import { motion } from "framer-motion";
import { useApiClient } from "@/lib/api";

export default function HistoryPage() {
  const { getContracts } = useApiClient();
  const [contracts, setContracts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const res = await getContracts();
        setContracts(res.contracts || []);
      } catch (err) {
        console.error("Failed to load history", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [getContracts]);

  return (
    <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 space-y-6 relative">
      <div className="absolute top-0 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-[120px] pointer-events-none" />

      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Scan History</h1>
          <p className="text-zinc-400">View and manage your previously analyzed contracts.</p>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-500" />
            <input 
              type="text" 
              placeholder="Search history..." 
              className="pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white focus:outline-none focus:border-white/20 w-full md:w-64"
            />
          </div>
          <button className="flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-sm font-medium text-white hover:bg-white/10 transition-colors">
            <Filter className="h-4 w-4" /> Filter
          </button>
        </div>
      </div>

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-panel rounded-2xl border border-white/10 overflow-hidden"
      >
        <div className="overflow-x-auto">
          {loading ? (
             <div className="flex justify-center p-8 text-zinc-500">Loading...</div>
          ) : contracts.length === 0 ? (
             <div className="flex justify-center p-8 text-zinc-500">No contracts analyzed yet.</div>
          ) : (
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-white/10 bg-white/5">
                <th className="px-6 py-4 text-xs font-semibold text-zinc-400 uppercase tracking-wider">Document Name</th>
                <th className="px-6 py-4 text-xs font-semibold text-zinc-400 uppercase tracking-wider">Type</th>
                <th className="px-6 py-4 text-xs font-semibold text-zinc-400 uppercase tracking-wider">Date Scanned</th>
                <th className="px-6 py-4 text-xs font-semibold text-zinc-400 uppercase tracking-wider">Score</th>
                <th className="px-6 py-4 text-xs font-semibold text-zinc-400 uppercase tracking-wider text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {contracts.map((contract) => {
                const isComplete = contract.overall_risk_score !== null && contract.overall_risk_score !== undefined;
                return (
                <tr key={contract.id} className="hover:bg-white/5 transition-colors group">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-white/5 rounded-lg">
                        <FileText className="h-4 w-4 text-blue-400" />
                      </div>
                      <span className="font-medium text-zinc-200 group-hover:text-white transition-colors">{contract.original_filename}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2.5 py-1 bg-white/5 text-zinc-300 rounded-md text-xs border border-white/10 uppercase">
                      {contract.contract_type}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-2 text-sm text-zinc-400">
                      <Calendar className="h-3 w-3" />
                      {new Date(contract.created_at).toLocaleDateString()}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {isComplete ? (
                        <><span className="text-sm font-semibold text-white">{contract.overall_risk_score}</span><span className="text-xs text-zinc-500">/100</span></>
                    ) : (
                        <span className="text-sm text-yellow-400">Processing...</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <Link 
                      href={contract.latest_job_id ? `/scan/${contract.latest_job_id}` : "#"}
                      className="inline-flex items-center gap-1 text-sm text-blue-400 hover:text-blue-300 font-medium transition-colors"
                    >
                      View Report <ArrowRight className="h-4 w-4" />
                    </Link>
                  </td>
                </tr>
              )})}
            </tbody>
          </table>
          )}
        </div>
      </motion.div>
    </div>
  );
}
