import { NextResponse } from "next/server";
import { Pool } from "pg";

const pool = new Pool({
  host: "localhost",
  port: 5432,
  user: "skwong",
  password: "postgres",
  database: "stock_pipeline",
});

export const dynamic = "force-dynamic";

export async function GET() {
  const result = await pool.query(`
    SELECT date, close
    FROM raw_stock_prices
    WHERE symbol = 'CRWD'
    ORDER BY date DESC
    LIMIT 30
  `);

  return NextResponse.json(result.rows.reverse());
}
