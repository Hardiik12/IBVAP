import React from "react";
import { Skeleton } from "../../components/ui/Skeleton";

export default function EventsLoading() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-10 w-64" />
      <Skeleton className="h-12" />
      <Skeleton className="h-96" />
    </div>
  );
}
