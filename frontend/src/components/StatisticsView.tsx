"use client";

import { useState, useEffect } from "react";
import { BarChart3, Filter, Target, Shield, TrendingUp } from "lucide-react";
import {
   PieChart,
   Pie,
   Cell,
   BarChart,
   Bar,
   XAxis,
   YAxis,
   CartesianGrid,
   Tooltip,
   ResponsiveContainer,
   Legend,
} from "recharts";

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

const COLORS = {
   success: "#10b981",
   failure: "#ef4444",
};

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

   useEffect(() => {
      fetch(`${API_URL}/api/statistics/filters`)
         .then((res) => res.json())
         .then((data) => setFilters(data))
         .catch((err) => console.error("Error fetching filters:", err));
   }, []);

   useEffect(() => {
      setLoading(true);
      const params = new URLSearchParams();
      params.set("attack_type", selectedAttack);
      params.set("defense_type", selectedDefense);

      fetch(`${API_URL}/api/statistics?${params}`)
         .then((res) => res.json())
         .then((result) => {
            setData(result.data || []);
            setLoading(false);
         })
         .catch((err) => {
            console.error("Error fetching statistics:", err);
            setLoading(false);
         });
   }, [selectedAttack, selectedDefense]);

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
         <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d] shadow-2xl">
            <div className="flex items-center gap-2 mb-4">
               <div className="bg-[#6366f1]/10 p-2 rounded-lg border border-[#6366f1]/20">
                  <Filter className="text-[#6366f1] w-5 h-5" />
               </div>
               <h2 className="text-lg font-bold text-[#f8fafc]">Filters</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
               <div>
                  <label className="text-sm font-medium text-[#94a3b8] mb-2 block">
                     Attack Type
                  </label>
                  <select
                     value={selectedAttack}
                     onChange={(e) => setSelectedAttack(e.target.value)}
                     className="w-full bg-[#252532] border-2 border-[#2d2d3d] rounded-lg px-4 py-2.5 text-[#f8fafc] cursor-pointer hover:border-[#ef4444]/50 focus:border-[#ef4444] focus:outline-none font-medium text-sm appearance-none transition-all duration-200"
                     style={{
                        backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%23ef4444'%3E%3Cpath strokeLinecap='round' strokeLinejoin='round' strokeWidth='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E")`,
                        backgroundRepeat: "no-repeat",
                        backgroundPosition: "right 0.5rem center",
                        backgroundSize: "1.5rem 1.5rem",
                     }}
                  >
                     <option value="all">All Attacks</option>
                     {filters.attack_types.map((type) => (
                        <option key={type} value={type}>
                           {type}
                        </option>
                     ))}
                  </select>
               </div>
               <div>
                  <label className="text-sm font-medium text-[#94a3b8] mb-2 block">
                     Defense Type
                  </label>
                  <select
                     value={selectedDefense}
                     onChange={(e) => setSelectedDefense(e.target.value)}
                     className="w-full bg-[#252532] border-2 border-[#2d2d3d] rounded-lg px-4 py-2.5 text-[#f8fafc] cursor-pointer hover:border-[#10b981]/50 focus:border-[#10b981] focus:outline-none font-medium text-sm appearance-none transition-all duration-200"
                     style={{
                        backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%2310b981'%3E%3Cpath strokeLinecap='round' strokeLinejoin='round' strokeWidth='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E")`,
                        backgroundRepeat: "no-repeat",
                        backgroundPosition: "right 0.5rem center",
                        backgroundSize: "1.5rem 1.5rem",
                     }}
                  >
                     <option value="all">All Defenses</option>
                     {filters.defense_types.map((type) => (
                        <option key={type} value={type}>
                           {type}
                        </option>
                     ))}
                  </select>
               </div>
            </div>
         </div>

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
               {/* Stats Cards */}
               <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                  <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d] shadow-2xl hover:border-[#6366f1]/30 transition-all duration-200">
                     <div className="flex items-center gap-2 mb-2">
                        <div className="bg-[#6366f1]/10 p-1.5 rounded-lg border border-[#6366f1]/20">
                           <BarChart3 className="text-[#6366f1] w-4 h-4" />
                        </div>
                        <span className="text-xs font-medium text-[#94a3b8] uppercase tracking-wider">
                           Total Tests
                        </span>
                     </div>
                     <div className="text-2xl font-bold text-[#f8fafc]">
                        {totalTests.toLocaleString()}
                     </div>
                  </div>

                  <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d] shadow-2xl hover:border-[#ef4444]/30 transition-all duration-200">
                     <div className="flex items-center gap-2 mb-2">
                        <div className="bg-[#ef4444]/10 p-1.5 rounded-lg border border-[#ef4444]/20">
                           <TrendingUp className="text-[#ef4444] w-4 h-4" />
                        </div>
                        <span className="text-xs font-medium text-[#94a3b8] uppercase tracking-wider">
                           Success Rate
                        </span>
                     </div>
                     <div className="text-2xl font-bold text-[#ef4444]">
                        {successRate}%
                     </div>
                  </div>

                  <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d] shadow-2xl hover:border-[#a855f7]/30 transition-all duration-200">
                     <div className="flex items-center gap-2 mb-2">
                        <div className="bg-[#a855f7]/10 p-1.5 rounded-lg border border-[#a855f7]/20">
                           <Target className="text-[#a855f7] w-4 h-4" />
                        </div>
                        <span className="text-xs font-medium text-[#94a3b8] uppercase tracking-wider">
                           Best Attack
                        </span>
                     </div>
                     <div className="text-sm font-bold text-[#f8fafc] truncate">
                        {bestAttack ? bestAttack.name : "N/A"}
                     </div>
                  </div>

                  <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d] shadow-2xl hover:border-[#10b981]/30 transition-all duration-200">
                     <div className="flex items-center gap-2 mb-2">
                        <div className="bg-[#10b981]/10 p-1.5 rounded-lg border border-[#10b981]/20">
                           <Shield className="text-[#10b981] w-4 h-4" />
                        </div>
                        <span className="text-xs font-medium text-[#94a3b8] uppercase tracking-wider">
                           Best Defense
                        </span>
                     </div>
                     <div className="text-sm font-bold text-[#f8fafc] truncate">
                        {bestDefense ? bestDefense.name : "N/A"}
                     </div>
                  </div>
               </div>

               {/* Charts Section */}
               <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
                  <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d] shadow-2xl">
                     <h3 className="text-base font-bold text-[#f8fafc] mb-4 flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-[#10b981] animate-pulse" />
                        Attack Success Distribution
                     </h3>
                     <ResponsiveContainer width="100%" height={280}>
                        <PieChart>
                           <Pie
                              data={pieData}
                              cx="50%"
                              cy="50%"
                              innerRadius={70}
                              outerRadius={110}
                              paddingAngle={5}
                              dataKey="value"
                              label={({ name, percent }) =>
                                 `${name}: ${((percent ?? 0) * 100).toFixed(
                                    0
                                 )}%`
                              }
                              labelLine={false}
                           >
                              <Cell fill={COLORS.success} />
                              <Cell fill={COLORS.failure} />
                           </Pie>
                           <Tooltip
                              contentStyle={{
                                 backgroundColor: "#1a1a24",
                                 border: "1px solid #2d2d3d",
                                 borderRadius: "8px",
                                 padding: "8px",
                              }}
                              itemStyle={{ color: "#f8fafc", fontWeight: 500 }}
                              labelStyle={{ color: "#f8fafc", fontWeight: 600 }}
                           />
                           <Legend
                              wrapperStyle={{ paddingTop: "20px" }}
                              iconType="circle"
                           />
                        </PieChart>
                     </ResponsiveContainer>
                  </div>

                  <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d] shadow-2xl">
                     <h3 className="text-base font-bold text-[#f8fafc] mb-4 flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-[#ef4444] animate-pulse" />
                        Success Rate by Attack Type
                     </h3>
                     <ResponsiveContainer width="100%" height={280}>
                        <BarChart data={attackStats} layout="vertical">
                           <CartesianGrid
                              strokeDasharray="3 3"
                              stroke="#2d2d3d"
                              opacity={0.5}
                           />
                           <XAxis
                              type="number"
                              domain={[0, 100]}
                              stroke="#94a3b8"
                              tick={{ fontSize: 12, fill: "#94a3b8" }}
                           />
                           <YAxis
                              type="category"
                              dataKey="name"
                              stroke="#94a3b8"
                              tick={{ fontSize: 11, fill: "#94a3b8" }}
                              width={110}
                           />
                           <Tooltip
                              contentStyle={{
                                 backgroundColor: "#1a1a24",
                                 border: "1px solid #2d2d3d",
                                 borderRadius: "8px",
                                 padding: "8px",
                              }}
                              labelStyle={{ color: "#f8fafc", fontWeight: 600 }}
                              formatter={(value: number | undefined) => [
                                 `${(value ?? 0).toFixed(1)}%`,
                                 "Success Rate",
                              ]}
                           />
                           <Bar
                              dataKey="successRate"
                              fill="#ef4444"
                              radius={[0, 8, 8, 0]}
                           />
                        </BarChart>
                     </ResponsiveContainer>
                  </div>
               </div>

               <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
                  <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d] shadow-2xl">
                     <h3 className="text-base font-bold text-[#f8fafc] mb-4 flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-[#10b981] animate-pulse" />
                        Success Rate by Defense Type
                     </h3>
                     <ResponsiveContainer width="100%" height={280}>
                        <BarChart data={defenseStats} layout="vertical">
                           <CartesianGrid
                              strokeDasharray="3 3"
                              stroke="#2d2d3d"
                              opacity={0.5}
                           />
                           <XAxis
                              type="number"
                              domain={[0, 100]}
                              stroke="#94a3b8"
                              tick={{ fontSize: 12, fill: "#94a3b8" }}
                           />
                           <YAxis
                              type="category"
                              dataKey="name"
                              stroke="#94a3b8"
                              tick={{ fontSize: 11, fill: "#94a3b8" }}
                              width={130}
                           />
                           <Tooltip
                              contentStyle={{
                                 backgroundColor: "#1a1a24",
                                 border: "1px solid #2d2d3d",
                                 borderRadius: "8px",
                                 padding: "8px",
                              }}
                              labelStyle={{ color: "#f8fafc", fontWeight: 600 }}
                              formatter={(value: number | undefined) => [
                                 `${(value ?? 0).toFixed(1)}%`,
                                 "Success Rate",
                              ]}
                           />
                           <Bar
                              dataKey="successRate"
                              fill="#10b981"
                              radius={[0, 8, 8, 0]}
                           />
                        </BarChart>
                     </ResponsiveContainer>
                  </div>

                  <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d] shadow-2xl">
                     <h3 className="text-base font-bold text-[#f8fafc] mb-4 flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-[#3b82f6] animate-pulse" />
                        Success Rate by Model Type
                     </h3>
                     <ResponsiveContainer width="100%" height={280}>
                        <BarChart data={modelStats} layout="vertical">
                           <CartesianGrid
                              strokeDasharray="3 3"
                              stroke="#2d2d3d"
                              opacity={0.5}
                           />
                           <XAxis
                              type="number"
                              domain={[0, 100]}
                              stroke="#94a3b8"
                              tick={{ fontSize: 12, fill: "#94a3b8" }}
                           />
                           <YAxis
                              type="category"
                              dataKey="name"
                              stroke="#94a3b8"
                              tick={{ fontSize: 11, fill: "#94a3b8" }}
                              width={100}
                           />
                           <Tooltip
                              contentStyle={{
                                 backgroundColor: "#1a1a24",
                                 border: "1px solid #2d2d3d",
                                 borderRadius: "8px",
                                 padding: "8px",
                              }}
                              labelStyle={{ color: "#f8fafc", fontWeight: 600 }}
                              formatter={(value: number | undefined) => [
                                 `${(value ?? 0).toFixed(1)}%`,
                                 "Success Rate",
                              ]}
                           />
                           <Bar
                              dataKey="successRate"
                              fill="#3b82f6"
                              radius={[0, 8, 8, 0]}
                           />
                        </BarChart>
                     </ResponsiveContainer>
                  </div>
               </div>
            </>
         )}
      </div>
   );
}
