import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    message: "Backend is running 🚀",
    time: new Date().toISOString(),
  });
}
