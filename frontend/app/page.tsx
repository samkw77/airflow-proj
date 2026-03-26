"use client";

import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";

export default function Home() {
  const [data, setData] = useState<any[]>([]);

  useEffect(() => {
    fetch("/api/stocks")
      .then((res) => res.json())
      .then((data) => {
        const formatted = data.map((d: any) => ({
          ...d,
          date: new Date(d.date).toLocaleDateString(),
        }));
        setData(formatted);
      });
  }, []);

  return (
    <main style={{ padding: "20px" }}>
      <h1>CRWD - Last 30 Days Close Price</h1>

      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={data}>
          <CartesianGrid />
          <XAxis dataKey="date" />
          <YAxis domain={["auto", "auto"]} />
          <Tooltip />
          <Line
            type="monotone"
            dataKey="close"
            stroke="#8884d8"
            dot={(props: any) => {
              const { cx, cy, payload } = props;
              return payload.close > 420 ? (
                <circle cx={cx} cy={cy} r={5} fill="red" />
              ) : null;
            }}
          />
        </LineChart>
      </ResponsiveContainer>
    </main>
  );
}
