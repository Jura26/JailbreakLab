"use client";

import { useState, useEffect, useRef } from "react";
import { BarChart3 } from "lucide-react";
import StatisticsFilters from "./statistics/StatisticsFilters";
import StatisticsCards from "./statistics/StatisticsCards";
import StatisticsCharts from "./statistics/StatisticsCharts";

const API_URL = import.meta.env.VITE_API_BASE_URL;

interface StatRecord {
   id: string;
   created_at: string;
   session_id: string;
   model_type: string;
   attack_type: string;
   defense_type: string;
   attack_success: boolean;
   was_blocked: boolean;
}

interface FilterOptions {
   attack_types: string[];
   defense_types: string[];
   model_types: string[];
}

export default function StatisticsView() {
   const [data, setData] = useState<StatRecord[]>([]);
   const [filters, setFilters] = useState<FilterOptions>({
      attack_types: [],
      defense_types: [],
      model_types: [],
   });
   const [selectedAttack, setSelectedAttack] = useState<string>("all");
   const [selectedDefense, setSelectedDefense] = useState<string>("all");
   const [loading, setLoading] = useState(true);
   const isFetchingRef = useRef(false);
   const debounceTimeoutRef = useRef<number | null>(null);
   const isInitialLoadRef = useRef(true);

   // New metrics state
   const [asrData, setAsrData] = useState<any>({});
   const [defenseBypassData, setDefenseBypassData] = useState<any>({});
   const [queryBudgetData, setQueryBudgetData] = useState<any>({});
   const [refusalData, setRefusalData] = useState<any>({});
   const [toolLeakageData, setToolLeakageData] = useState<any>({});
   const [additionalData, setAdditionalData] = useState<any>({});

   useEffect(() => {
      fetch(`${API_URL}/api/statistics/filters`)
         .then((res) => res.json())
         .then((data) => setFilters(data))
         .catch((err) => console.error("Error fetching filters:", err));
   }, []);

   useEffect(() => {
      // Clear any existing timeout
      if (debounceTimeoutRef.current) {
         clearTimeout(debounceTimeoutRef.current);
      }

      const delay = isInitialLoadRef.current ? 0 : 300; // No delay for initial load
      isInitialLoadRef.current = false;

      // Debounce the API calls (or run immediately for initial load)
      debounceTimeoutRef.current = setTimeout(() => {
         // Prevent duplicate requests
         if (isFetchingRef.current) {
            return;
         }

         isFetchingRef.current = true;
         setLoading(true);
         const params = new URLSearchParams();
         params.set("attack_type", selectedAttack);
         params.set("defense_type", selectedDefense);

         // Fetch all metrics in parallel
         const fetches = [
            fetch(`${API_URL}/api/statistics?${params}`).then((r) => r.json()),
            fetch(`${API_URL}/api/statistics/asr?${params}`).then((r) =>
               r.json()
            ),
            fetch(`${API_URL}/api/statistics/defense-bypass?${params}`).then(
               (r) => r.json()
            ),
            fetch(`${API_URL}/api/statistics/query-budget?${params}`).then(
               (r) => r.json()
            ),
            fetch(`${API_URL}/api/statistics/refusal?${params}`).then((r) =>
               r.json()
            ),
            fetch(`${API_URL}/api/statistics/tool-leakage?${params}`).then(
               (r) => r.json()
            ),
            fetch(`${API_URL}/api/statistics/additional?${params}`).then((r) =>
               r.json()
            ),
         ];

         Promise.all(fetches)
            .then(
               ([
                  statsResult,
                  asrResult,
                  defenseBypassResult,
                  queryBudgetResult,
                  refusalResult,
                  toolLeakageResult,
                  additionalResult,
               ]) => {
                  setData(statsResult.data || []);
                  setAsrData(asrResult);
                  setDefenseBypassData(defenseBypassResult);
                  setQueryBudgetData(queryBudgetResult);
                  setRefusalData(refusalResult);
                  setToolLeakageData(toolLeakageResult);
                  setAdditionalData(additionalResult);
                  setLoading(false);
               }
            )
            .catch((err) => {
               console.error("Error fetching statistics:", err);
               setLoading(false);
            })
            .finally(() => {
               isFetchingRef.current = false;
            });
      }, delay); // 0ms for initial load, 300ms debounce for filter changes

      // Cleanup function to clear timeout
      return () => {
         if (debounceTimeoutRef.current) {
            clearTimeout(debounceTimeoutRef.current);
         }
      };
   }, [selectedAttack, selectedDefense]);

   // Cleanup on unmount
   useEffect(() => {
      return () => {
         isFetchingRef.current = false;
         if (debounceTimeoutRef.current) {
            clearTimeout(debounceTimeoutRef.current);
         }
      };
   }, []);

   const totalTests = data.length;
   const successfulAttacks = data.filter((d) => d.attack_success).length;
   const failedAttacks = totalTests - successfulAttacks;
   const successRate =
      totalTests > 0
         ? ((successfulAttacks / totalTests) * 100).toFixed(1)
         : "0";

   const pieData = [
      { name: "Attack Succeeded", value: successfulAttacks },
      { name: "Attack Failed", value: failedAttacks },
   ];

   const attackTypes = [...new Set(data.map((d) => d.attack_type))];
   const attackStats = attackTypes
      .map((attackType) => {
         const filtered = data.filter((d) => d.attack_type === attackType);
         const success = filtered.filter((d) => d.attack_success).length;
         const rate =
            filtered.length > 0 ? (success / filtered.length) * 100 : 0;
         return { name: attackType, successRate: rate, total: filtered.length };
      })
      .filter((d) => d.total > 0);

   const defenseTypes = [...new Set(data.map((d) => d.defense_type))];
   const defenseStats = defenseTypes
      .map((defenseType) => {
         const filtered = data.filter((d) => d.defense_type === defenseType);
         const success = filtered.filter((d) => d.attack_success).length;
         const rate =
            filtered.length > 0 ? (success / filtered.length) * 100 : 0;
         return {
            name: defenseType,
            successRate: rate,
            total: filtered.length,
         };
      })
      .filter((d) => d.total > 0);

   const modelTypes = [...new Set(data.map((d) => d.model_type))];
   const modelStats = modelTypes
      .map((modelType) => {
         const filtered = data.filter((d) => d.model_type === modelType);
         const success = filtered.filter((d) => d.attack_success).length;
         const rate =
            filtered.length > 0 ? (success / filtered.length) * 100 : 0;
         return { name: modelType, successRate: rate, total: filtered.length };
      })
      .filter((d) => d.total > 0);

   const bestAttack =
      attackStats.length > 0
         ? attackStats.reduce((a, b) => (a.successRate > b.successRate ? a : b))
         : null;
   const bestDefense =
      defenseStats.length > 0
         ? defenseStats.reduce((a, b) =>
              a.successRate < b.successRate ? a : b
           )
         : null;

   return (
      <div className="flex flex-col gap-3 h-full overflow-y-auto pr-2">
         {/* Filters Section */}
         <StatisticsFilters
            filters={filters}
            selectedAttack={selectedAttack}
            selectedDefense={selectedDefense}
            onAttackChange={setSelectedAttack}
            onDefenseChange={setSelectedDefense}
         />

         {loading ? (
            <div className="flex items-center justify-center h-96 bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl border border-[#2d2d3d]">
               <div className="text-center">
                  <div className="w-12 h-12 border-4 border-[#6366f1]/30 border-t-[#6366f1] rounded-full animate-spin mx-auto mb-4"></div>
                  <p className="text-[#94a3b8] font-medium">
                     Loading statistics...
                  </p>
               </div>
            </div>
         ) : totalTests === 0 ? (
            <div className="flex items-center justify-center h-96 bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl border border-[#2d2d3d]">
               <div className="text-center">
                  <div className="bg-[#6366f1]/10 w-16 h-16 rounded-xl flex items-center justify-center mx-auto mb-4 border border-[#6366f1]/20">
                     <BarChart3 className="text-[#6366f1] w-8 h-8" />
                  </div>
                  <p className="text-[#94a3b8] font-medium text-lg">
                     No data available
                  </p>
                  <p className="text-[#64748b] text-sm mt-1">
                     Run some tests first to see statistics
                  </p>
               </div>
            </div>
         ) : (
            <>
               <StatisticsCards
                  totalTests={totalTests}
                  successRate={successRate}
                  bestAttack={bestAttack}
                  bestDefense={bestDefense}
                  asrData={asrData}
                  defenseBypassData={defenseBypassData}
                  queryBudgetData={queryBudgetData}
                  refusalData={refusalData}
                  additionalData={additionalData}
                  toolLeakageData={toolLeakageData}
               />

               <StatisticsCharts
                  pieData={pieData}
                  attackStats={attackStats}
                  defenseStats={defenseStats}
                  modelStats={modelStats}
                  asrData={asrData}
                  defenseBypassData={defenseBypassData}
                  queryBudgetData={queryBudgetData}
                  refusalData={refusalData}
               />
            </>
         )}
      </div>
   );
}
