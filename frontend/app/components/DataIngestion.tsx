/* eslint-disable */
"use client";
// app/components/DataIngestion.tsx
import React, { useState } from "react";
import { fetchFinancialData } from "../../lib/apiUtils";

interface DataIngestionProps {
  onDataFetched: (symbol: string) => void;
}

const DataIngestion: React.FC<DataIngestionProps> = ({ onDataFetched }) => {
  const [symbol, setSymbol] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log("submit data");
    const data = await fetchFinancialData(symbol);
    console.log("data", data);
    onDataFetched(data);
  };

  return (
    <form onSubmit={handleSubmit} className="flex items-center space-x-4">
      <input
        type="text"
        value={symbol}
        onChange={(e) => setSymbol(e.target.value)}
        placeholder="Enter Stock Symbol (e.g., AAPL)"
        className="border p-2"
      />
      <button type="submit" className="bg-blue-500 text-white p-2 rounded">
        Analyze
      </button>
    </form>
  );
};

export default DataIngestion;
