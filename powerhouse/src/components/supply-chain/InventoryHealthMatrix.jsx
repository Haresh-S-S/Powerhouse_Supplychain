import React, { useState } from 'react';
import {
  Boxes,
  ArrowRightLeft,
  AlertTriangle,
  CheckCircle,
  HelpCircle,
  TrendingDown,
  Truck,
  Sparkles,
  ShieldAlert,
} from 'lucide-react';
import Button from '../ui/Button';

const STATUS_PILLS = {
  Healthy: { bg: 'bg-emerald-950/80', border: 'border-emerald-800', text: 'text-emerald-400', dot: 'bg-emerald-400' },
  Warning: { bg: 'bg-amber-950/80', border: 'border-amber-800', text: 'text-amber-400', dot: 'bg-amber-400' },
  Critical: { bg: 'bg-rose-950/80', border: 'border-rose-800', text: 'text-rose-400', dot: 'bg-rose-400' },
  Overstocked: { bg: 'bg-blue-950/80', border: 'border-blue-800', text: 'text-blue-400', dot: 'bg-blue-400' },
};

export default function InventoryHealthMatrix({ inventoryData, onTriggerRebalance }) {
  const [selectedSku, setSelectedSku] = useState('SKU-DRAM-001');

  const warehouses = inventoryData?.warehouse_columns || [
    { code: 'DC-NORTH', name: 'DC North (Hamburg)' },
    { code: 'DC-SOUTH', name: 'DC South (Dallas)' },
    { code: 'DC-WEST', name: 'DC West (Tokyo)' },
    { code: 'DC-CENTRAL', name: 'DC Central (Mumbai)' },
  ];

  const matrix = inventoryData?.matrix || [];
  const criticalComp = inventoryData?.critical_sku_comparison || {
    sku: 'SKU-DRAM-001',
    name: 'DRAM-16GB-DDR5',
    warehouse: 'DC South (Dallas)',
    current_inventory: 4280,
    safety_stock: 5100,
    forecast_demand_30d: 4850,
    shortfall: -820,
    status: 'Critical',
    days_of_cover: 5.8,
  };

  return (
    <div className="bg-[#111827] rounded-2xl border border-[#1E293B] p-5 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-bold text-white">Multi-Echelon Inventory Health Matrix</h3>
            <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-cyan-950/70 text-cyan-300 border border-cyan-800 font-mono">
              Inventory Fusion Engine
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            2D Heatmap of critical SKUs across regional distribution centers and hubs
          </p>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-3 text-[11px]">
          <span className="flex items-center gap-1.5 text-emerald-400">
            <span className="w-2 h-2 rounded-full bg-emerald-500" /> Healthy
          </span>
          <span className="flex items-center gap-1.5 text-amber-400">
            <span className="w-2 h-2 rounded-full bg-amber-500" /> Warning
          </span>
          <span className="flex items-center gap-1.5 text-rose-400">
            <span className="w-2 h-2 rounded-full bg-rose-500 animate-pulse" /> Critical
          </span>
          <span className="flex items-center gap-1.5 text-blue-400">
            <span className="w-2 h-2 rounded-full bg-blue-500" /> Overstocked
          </span>
        </div>
      </div>

      {/* Heatmap 2D Matrix Table */}
      <div className="overflow-x-auto scrollbar-thin rounded-xl border border-slate-800">
        <table className="w-full text-xs text-left">
          <thead className="bg-slate-900/90 text-slate-400 font-semibold border-b border-slate-800">
            <tr>
              <th className="py-2.5 px-3">SKU & Material</th>
              <th className="py-2.5 px-2">Category</th>
              {warehouses.map((w) => (
                <th key={w.code} className="py-2.5 px-3 text-center">
                  {w.name}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/80 bg-[#0B1120]">
            {matrix.slice(0, 8).map((row) => (
              <tr
                key={row.sku}
                onClick={() => setSelectedSku(row.sku)}
                className={`transition-colors cursor-pointer ${
                  selectedSku === row.sku ? 'bg-slate-800/60' : 'hover:bg-slate-900/50'
                }`}
              >
                <td className="py-2.5 px-3">
                  <div className="font-bold text-white">{row.name}</div>
                  <div className="text-[10px] text-slate-400 font-mono">{row.sku}</div>
                </td>
                <td className="py-2.5 px-2 text-slate-400">{row.category}</td>
                {warehouses.map((w) => {
                  const cell = row.cells?.[w.code] || { status: 'Healthy', on_hand: 3200 };
                  const pill = STATUS_PILLS[cell.status] || STATUS_PILLS.Healthy;

                  return (
                    <td key={w.code} className="py-2.5 px-3 text-center">
                      <span
                        className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-bold border ${pill.bg} ${pill.border} ${pill.text}`}
                      >
                        <span className={`w-1.5 h-1.5 rounded-full ${pill.dot}`} />
                        {cell.on_hand ? `${Math.round(cell.on_hand).toLocaleString()} u` : cell.status}
                      </span>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Critical SKU Bar Chart & Inventory Rebalancing Agent Recommendation */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 pt-2">
        {/* Critical SKU Stock Level Comparison Bar Chart */}
        <div className="p-4 rounded-xl bg-[#0B1120] border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-xs font-bold text-slate-200 flex items-center gap-2">
              <Boxes className="w-4 h-4 text-rose-400" />
              Stock Position Comparison — {criticalComp.name}
            </h4>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-rose-950 text-rose-300 border border-rose-800 font-mono">
              {criticalComp.warehouse}
            </span>
          </div>

          <div className="space-y-2.5 pt-2">
            {/* Current Stock Bar */}
            <div className="space-y-1 text-xs">
              <div className="flex items-center justify-between text-slate-300">
                <span>Current On-Hand Stock</span>
                <span className="font-mono font-bold text-white">{criticalComp.current_inventory.toLocaleString()} units</span>
              </div>
              <div className="w-full h-3 bg-slate-900 rounded-full overflow-hidden border border-slate-800">
                <div
                  className="h-full bg-rose-500 rounded-full"
                  style={{ width: `${(criticalComp.current_inventory / 6000) * 100}%` }}
                />
              </div>
            </div>

            {/* Safety Stock Bar */}
            <div className="space-y-1 text-xs">
              <div className="flex items-center justify-between text-slate-300">
                <span>Prescribed Safety Stock Threshold</span>
                <span className="font-mono font-bold text-amber-400">{criticalComp.safety_stock.toLocaleString()} units</span>
              </div>
              <div className="w-full h-3 bg-slate-900 rounded-full overflow-hidden border border-slate-800">
                <div
                  className="h-full bg-amber-500 rounded-full"
                  style={{ width: `${(criticalComp.safety_stock / 6000) * 100}%` }}
                />
              </div>
            </div>

            {/* Forecast Demand Bar */}
            <div className="space-y-1 text-xs">
              <div className="flex items-center justify-between text-slate-300">
                <span>30-Day Forecast Demand (P50)</span>
                <span className="font-mono font-bold text-cyan-400">{criticalComp.forecast_demand_30d.toLocaleString()} units</span>
              </div>
              <div className="w-full h-3 bg-slate-900 rounded-full overflow-hidden border border-slate-800">
                <div
                  className="h-full bg-cyan-500 rounded-full"
                  style={{ width: `${(criticalComp.forecast_demand_30d / 6000) * 100}%` }}
                />
              </div>
            </div>
          </div>

          {/* Shortfall Alert Callout */}
          <div className="p-3 rounded-lg bg-rose-950/40 border border-rose-800/60 flex items-center justify-between text-xs">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
              <div>
                <span className="font-bold text-rose-200">Critical Buffer Shortfall: </span>
                <span className="font-mono font-bold text-rose-300">{criticalComp.shortfall} units</span>
              </div>
            </div>
            <span className="text-[11px] text-slate-400 font-mono">
              Stockout in: <strong className="text-rose-400">{criticalComp.days_of_cover} days</strong>
            </span>
          </div>
        </div>

        {/* AI Rebalancing Recommendation Card */}
        <div className="p-4 rounded-xl bg-[#0B1120] border border-cyan-900/60 flex flex-col justify-between space-y-3">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[10px] uppercase font-bold text-cyan-400 tracking-wider flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5" />
                AI Inventory Rebalancing Workflow
              </span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-950 text-amber-300 border border-amber-800">
                APPROVAL REQUIRED
              </span>
            </div>

            <h4 className="text-sm font-bold text-white">
              Transfer 800 units from DC North (Hamburg) → DC South (Dallas)
            </h4>

            <p className="text-xs text-slate-300 leading-relaxed">
              DC North currently holds <strong>9,400 units (2.4× safety stock buffer)</strong>. 
              Executing an inter-DC freight transfer eliminates the 6-day stockout vulnerability at DC South.
            </p>

            <div className="grid grid-cols-2 gap-2 text-xs pt-1">
              <div className="p-2 rounded-lg bg-slate-900 border border-slate-800">
                <span className="text-[10px] text-slate-400 block">Shortage Reduction</span>
                <span className="text-sm font-black text-emerald-400">72.0%</span>
              </div>
              <div className="p-2 rounded-lg bg-slate-900 border border-slate-800">
                <span className="text-[10px] text-slate-400 block">Logistics Freight Cost</span>
                <span className="text-sm font-black text-white">$8,420.00</span>
              </div>
            </div>
          </div>

          <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between gap-3">
            <span className="text-[10px] text-slate-400">High-impact operational transfer</span>
            <Button
              variant="primary"
              size="sm"
              onClick={() => onTriggerRebalance && onTriggerRebalance('SKU-DRAM-001')}
              className="bg-cyan-600 hover:bg-cyan-500 text-white text-xs flex items-center gap-1.5"
            >
              <ArrowRightLeft className="w-3.5 h-3.5" />
              <span>Submit for Human Approval</span>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
