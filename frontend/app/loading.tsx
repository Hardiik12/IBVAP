import React from "react";
import { Skeleton } from "../components/ui/Skeleton";

export default function Loading() {
  return (
    <div className="space-y-6 animate-fade-in">
      {/* Top Metrics Skeletons */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Skeleton className="h-24" />
        <Skeleton className="h-24" />
        <Skeleton className="h-24" />
        <Skeleton className="h-24" />
      </div>

      {/* Main Content Grid Skeleton */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Skeleton className="lg:col-span-2 h-[450px]" />
        <Skeleton className="h-[450px]" />
      </div>
    </div>
  );
}
