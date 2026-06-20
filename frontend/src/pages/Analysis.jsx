import { useEffect, useState } from "react";
import axios from "axios";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
  ResponsiveContainer,
} from "recharts";

const METRIC_COLORS = ["#1193d4", "#22c55e", "#f59e0b", "#a78bfa"];

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="rounded-lg border border-[#283339] bg-[#0f1416] px-3 py-2 text-sm shadow-lg">
        <p className="font-medium text-white">{label}</p>
        <p className="text-[#1193d4]">{payload[0].value}%</p>
      </div>
    );
  }
  return null;
};

export default function Analysis() {
  const [metrics, setMetrics] = useState(null);
  const [samples, setSamples] = useState(0);
  const [confusion, setConfusion] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const cached = sessionStorage.getItem("analysisData");

    if (cached) {
      const parsed = JSON.parse(cached);
      setMetrics(parsed.metrics);
      setSamples(parsed.samples);
      setConfusion(parsed.confusion ?? null);
      setLoading(false);
      return;
    }

    const fetchAnalysis = async () => {
      try {
        const res = await axios.get("http://127.0.0.1:5000/analysis");
        setMetrics(res.data.metrics);
        setSamples(res.data.samples_evaluated);
        setConfusion(res.data.confusion ?? null);
        sessionStorage.setItem(
          "analysisData",
          JSON.stringify({
            metrics: res.data.metrics,
            samples: res.data.samples_evaluated,
            confusion: res.data.confusion ?? null,
          })
        );
      } catch {
        setError("Failed to load analysis data.");
      } finally {
        setLoading(false);
      }
    };

    fetchAnalysis();
  }, []);

  const chartData = metrics
    ? [
        { label: "Accuracy",  value: metrics.accuracy },
        { label: "Precision", value: metrics.precision },
        { label: "Recall",    value: metrics.recall },
        { label: "F1 Score",  value: metrics.f1_score },
      ]
    : [];

  return (
    <>
      <style>{`
        @keyframes fade-up {
          from { opacity: 0; transform: translateY(16px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        .metric-card {
          animation: fade-up 0.5s ease both;
          transition: transform 0.2s, border-color 0.2s;
        }
        .metric-card:hover { transform: translateY(-2px); border-color: rgba(17,147,212,0.3); }
        .metric-card:nth-child(1) { animation-delay: 0.05s; }
        .metric-card:nth-child(2) { animation-delay: 0.10s; }
        .metric-card:nth-child(3) { animation-delay: 0.15s; }
        .metric-card:nth-child(4) { animation-delay: 0.20s; }
        .section-card {
          animation: fade-up 0.5s ease both;
          animation-delay: 0.25s;
        }
      `}</style>

      <section className="min-h-[calc(100vh-64px)] bg-[#111618] px-6 py-10">
        <div className="mx-auto max-w-7xl">

          {/* Header */}
          <div className="mb-10">
            <h1 className="text-3xl font-semibold tracking-tight text-white">
              Model Performance Analysis
            </h1>
            <p className="mt-2 max-w-2xl text-sm text-slate-400">
              Live performance metrics of the{" "}
              <span className="text-[#1193d4] font-medium">Hybrid Stacking Model</span>{" "}
              (Random Forest + Decision Tree) evaluated on a
              held-out 20% test split of the feature-engineered dataset.
            </p>
          </div>

          {/* Loading */}
          {loading && (
            <div className="flex h-64 items-center justify-center">
              <div className="h-8 w-8 animate-spin rounded-full border-2 border-[#1193d4] border-t-transparent" />
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="flex items-center gap-2 rounded-xl border border-red-500/40 bg-red-500/10 p-4 text-sm text-red-400">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="shrink-0">
                <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
              {error}
            </div>
          )}

          {!loading && metrics && (
            <>
              {/* Metric Cards */}
              <div className="mb-10 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
                {chartData.map((item, i) => (
                  <div
                    key={item.label}
                    className="metric-card relative rounded-xl border border-[#283339] bg-[#0f1416] p-6 shadow-[0_20px_40px_rgba(0,0,0,0.6)]"
                  >
                    <div
                      className="absolute inset-x-0 top-0 h-[2px] rounded-t-xl"
                      style={{ background: `linear-gradient(90deg, transparent, ${METRIC_COLORS[i]}, transparent)` }}
                    />
                    <p className="text-sm font-medium text-slate-400">{item.label}</p>
                    <p className="mt-2 text-3xl font-semibold text-white">{item.value}%</p>
                    {/* Mini progress bar */}
                    <div className="mt-3 h-1 w-full rounded-full bg-[#283339] overflow-hidden">
                      <div
                        className="h-full rounded-full"
                        style={{ width: `${item.value}%`, background: METRIC_COLORS[i] }}
                      />
                    </div>
                  </div>
                ))}
              </div>

              {/* Bar Chart */}
              <div className="section-card mb-8 rounded-xl border border-[#283339] bg-[#0f1416] p-6">
                <h2 className="mb-6 text-lg font-semibold text-white">Metrics Overview</h2>
                <ResponsiveContainer width="100%" height={260}>
                  <BarChart
                    data={chartData}
                    margin={{ top: 4, right: 16, left: -10, bottom: 0 }}
                    barSize={48}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#283339" vertical={false} />
                    <XAxis
                      dataKey="label"
                      tick={{ fill: "#94a3b8", fontSize: 13 }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <YAxis
                      domain={[Math.max(0, Math.min(...chartData.map((d) => d.value)) - 5), 100]}
                      tick={{ fill: "#94a3b8", fontSize: 12 }}
                      axisLine={false}
                      tickLine={false}
                      tickFormatter={(v) => `${v}%`}
                    />
                    <Tooltip content={<CustomTooltip />} cursor={{ fill: "#1193d415" }} />
                    <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                      {chartData.map((_, i) => (
                        <Cell key={i} fill={METRIC_COLORS[i]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Evaluation Explanation */}
              <div className="section-card mb-8 rounded-xl border border-[#283339] bg-[#0f1416] p-6">
                <h2 className="text-lg font-semibold text-white mb-3">Evaluation Methodology</h2>
                <p className="text-sm leading-relaxed text-slate-400">
                  The metrics above are computed by evaluating the trained Hybrid Stacking model
                  on a 20% test split (random_state=42) of the feature-engineered dataset, ensuring
                  the model is assessed on data it has never seen during training.
                </p>
                <p className="mt-3 text-sm leading-relaxed text-slate-400">
                  The stacking ensemble uses{" "}
                  <span className="text-white font-medium">Random Forest</span> and{" "}
                  <span className="text-white font-medium">Decision Tree</span> as base learners,
                  whose predictions are fed into a{" "}
                  <span className="text-white font-medium">Logistic Regression</span> meta-classifier.
                  This leverages RF's robustness against overfitting and DT's interpretability,
                  improving generalization over any single model.
                </p>
              </div>

              {/* Confusion Matrix */}
              <div className="section-card mb-8 rounded-xl border border-[#283339] bg-[#0f1416] p-6">
                <h2 className="mb-4 text-lg font-semibold text-white">Confusion Matrix</h2>
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse text-center text-sm text-white">
                    <thead>
                      <tr>
                        <th className="border border-[#283339] px-4 py-3 text-slate-400 font-medium" />
                        <th className="border border-[#283339] px-4 py-3 text-slate-300 font-medium">Predicted Safe</th>
                        <th className="border border-[#283339] px-4 py-3 text-slate-300 font-medium">Predicted Phishing</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td className="border border-[#283339] px-4 py-3 font-medium text-slate-300">Actual Safe</td>
                        <td className="border border-[#283339] px-4 py-3 text-green-400 font-semibold">
                          {confusion ? confusion.true_negative.toLocaleString() : "—"}
                        </td>
                        <td className="border border-[#283339] px-4 py-3 text-red-400 font-semibold">
                          {confusion ? confusion.false_positive.toLocaleString() : "—"}
                        </td>
                      </tr>
                      <tr>
                        <td className="border border-[#283339] px-4 py-3 font-medium text-slate-300">Actual Phishing</td>
                        <td className="border border-[#283339] px-4 py-3 text-red-400 font-semibold">
                          {confusion ? confusion.false_negative.toLocaleString() : "—"}
                        </td>
                        <td className="border border-[#283339] px-4 py-3 text-green-400 font-semibold">
                          {confusion ? confusion.true_positive.toLocaleString() : "—"}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <p className="mt-3 text-xs text-slate-500">
                  The confusion matrix shows the distribution of correct and incorrect predictions
                  across safe and phishing classes.
                </p>
              </div>

              {/* Footer */}
              <div className="text-sm text-slate-400">
                Evaluated on{" "}
                <span className="font-medium text-white">{samples.toLocaleString()}</span>{" "}
                test samples (20% held-out split) from the feature-engineered dataset.
              </div>
            </>
          )}
        </div>
      </section>
    </>
  );
}