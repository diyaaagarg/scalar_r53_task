"use client";

import { SideNavigation } from "@cloudscape-design/components";
import { usePathname } from "next/navigation";

export function Route53SideNavigation() {
  const pathname = usePathname();
  return <SideNavigation
    activeHref={pathname}
    header={{ href: "/dashboard", text: "Route 53" }}
    items={[
      { type: "link", text: "Dashboard", href: "/dashboard" },
      { type: "link", text: "Hosted zones", href: "/hosted-zones" },
      { type: "link", text: "Health checks", href: "/health-checks" },
      { type: "link", text: "Profiles", href: "/profiles" },
      { type: "section", text: "Global Resolver", items: [{ type: "link", text: "Global resolvers", href: "/resolver" }, { type: "link", text: "Shared DNS views", href: "/resolver" }] },
      { type: "section", text: "VPC Resolver", items: [{ type: "link", text: "VPCs", href: "/resolver" }, { type: "link", text: "Inbound endpoints", href: "/resolver" }, { type: "link", text: "Outbound endpoints", href: "/resolver" }, { type: "link", text: "Rules", href: "/resolver" }, { type: "link", text: "Query logging", href: "/resolver" }] },
      { type: "section", text: "Domains", items: [{ type: "link", text: "Registered domains", href: "/coming-soon" }, { type: "link", text: "Requests", href: "/coming-soon" }] },
      { type: "section", text: "Traffic flow", items: [{ type: "link", text: "Traffic policies", href: "/traffic-policies" }, { type: "link", text: "Policy records", href: "/traffic-policies" }] },
    ]}
  />;
}
