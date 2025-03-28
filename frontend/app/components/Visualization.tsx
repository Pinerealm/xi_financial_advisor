/* eslint-disable */
"use client";
// app/components/Visualization.tsx
import React from "react";
import { Line } from "react-chartjs-2";
import { Chart, registerables } from "chart.js";

Chart.register(...registerables);

interface VisualizationData {
  labels: string[];
  values: number[];
}

interface VisualizationProps {
  data: VisualizationData | null;
}

const Visualization: React.FC<VisualizationProps> = ({ data }) => {
  if (!data)
    return (
      <div className="text-gray-400">No visualization data available.</div>
    );

  const chartData = {
    labels: data.labels,
    datasets: [
      {
        label: "Predicted Price",
        data: data.values,
        fill: false,
        backgroundColor: "rgba(56, 189, 248, 0.4)", // Light blue fill
        borderColor: "rgba(56, 189, 248, 1)", // Vibrant blue line
        borderWidth: 3,
        pointRadius: 5,
        pointBackgroundColor: "rgba(56, 189, 248, 1)", // Blue points
        pointBorderColor: "#fff",
        pointHoverRadius: 8,
        pointHoverBackgroundColor: "rgba(56, 189, 248, 1)",
        pointHoverBorderColor: "#fff",
        tension: 0.4, // Add some curve to the line
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        grid: {
          color: "rgba(255, 255, 255, 0.1)", // Lighter grid lines
        },
        ticks: {
          color: "#ddd", // Light tick color
        },
      },
      y: {
        grid: {
          color: "rgba(255, 255, 255, 0.1)",
        },
        ticks: {
          color: "#ddd",
          callback: (value: string | number) => "$" + value, // Add dollar sign
        },
      },
    },
    plugins: {
      legend: {
        display: true,
        position: "top",
        labels: {
          color: "#ddd", // Light legend color
          font: {
            size: 14,
          },
        },
      },
      tooltip: {
        backgroundColor: "rgba(0, 0, 0, 0.8)", // Darker tooltip
        titleColor: "#fff",
        bodyColor: "#eee",
        borderColor: "rgba(255, 255, 255, 0.1)", // Light border
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: true,
        padding: 12,
        callbacks: {
          label: (context: any) => {
            let label = context.dataset.label || "";
            if (label) {
              label += ": ";
            }
            if (context.parsed.y !== null) {
              label += "$" + context.parsed.y.toFixed(2);
            }
            return label;
          },
        },
      },
    },
  };

  return (
    <div className="bg-white/5 p-6 rounded-lg shadow-md border border-white/10">
      <h2 className="text-2xl font-semibold text-gray-200 mb-6">
        Predicted Stock Price
      </h2>
      <div className="h-[300px] w-full">
        <Line data={chartData} options={chartOptions} />
      </div>
    </div>
  );
};

export default Visualization;
