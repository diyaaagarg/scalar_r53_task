"use client";

import { AppLayout } from "@cloudscape-design/components";
import { AwsTopNavigation } from "@/components/console/AwsTopNavigation";
import { Route53Breadcrumbs } from "@/components/console/Route53Breadcrumbs";
import { Route53SideNavigation } from "@/components/console/Route53SideNavigation";

export function ConsoleShell({ children }: Readonly<{ children: React.ReactNode }>) {
  return <><AwsTopNavigation /><AppLayout navigation={<Route53SideNavigation />} breadcrumbs={<Route53Breadcrumbs />} contentType="default" toolsHide navigationWidth={264} content={<>{children}<footer className="console-footer">© 2026, Amazon Web Services, Inc. or its affiliates. &nbsp; Privacy &nbsp; Terms &nbsp; Cookie preferences</footer></>} /></>;
}
