/* eslint-disable */
// app/components/ReportGeneration.tsx
import React from "react";

interface ReportGenerationProps {
  report: any;
}

const ReportGeneration: React.FC<ReportGenerationProps> = ({ report }) => {
  if (!report) return null;

  return (
    <div className="bg-white/5 p-6 rounded-lg shadow-md border border-white/10">
      <h2 className="text-2xl font-semibold text-gray-200 mb-6">
        Report Generation
      </h2>
      <h3 className="text-lg font-semibold text-gray-300 mb-2">Summary</h3>
      <p className="text-gray-400 mb-4">{report.summary}</p>
      <h3 className="text-lg font-semibold text-gray-300 mb-2">Forecast</h3>
      <ul className="list-disc list-inside space-y-2 mb-4">
        {report.forecast.map((item: any, index: number) => (
          <li key={index} className="text-gray-400">
            {item.day}:{" "}
            <span className="text-pink-400 font-medium">
              {item.predictedPrice}
            </span>
          </li>
        ))}
      </ul>
      <h3 className="text-lg font-semibold text-gray-300 mb-2">
        Recommendation
      </h3>
      <p className="text-gray-400 font-semibold text-emerald-400">
        {report.recommendation}
      </p>
    </div>
  );
};

export default ReportGeneration;
