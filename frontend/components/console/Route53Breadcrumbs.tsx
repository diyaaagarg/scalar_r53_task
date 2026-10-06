"use client";

import { BreadcrumbGroup } from "@cloudscape-design/components";
import { usePathname } from "next/navigation";

const labels: Record<string, string> = { dashboard: "Dashboard", "hosted-zones": "Hosted zones", "health-checks": "Health checks", profiles: "Profiles", resolver: "Resolver", "traffic-policies": "Traffic policies" };
export function Route53Breadcrumbs() {
  const parts = usePathname().split("/").filter(Boolean);
  const items = [{ text: "Route 53", href: "/dashboard" }, ...parts.map((part, index) => ({ text: labels[part] ?? part, href: `/${parts.slice(0, index + 1).join("/")}` }))];
  return <BreadcrumbGroup items={items} ariaLabel="Breadcrumbs" />;
}
