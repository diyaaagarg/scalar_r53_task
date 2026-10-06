"use client";

import { TopNavigation } from "@cloudscape-design/components";
import { useAuth } from "@/providers/AuthProvider";
import { useColorMode } from "@/providers/ColorModeProvider";

export function AwsTopNavigation() {
  const { session, signOut } = useAuth();
  const { colorMode, toggleColorMode } = useColorMode();
  return <TopNavigation
    identity={{ href: "/dashboard", title: "AWS", logo: { alt: "AWS", src: "/aws-logo.png" } }}
    i18nStrings={{ searchIconAriaLabel: "Search", searchDismissIconAriaLabel: "Close search" }}
    search={<input aria-label="Search AWS services" placeholder="Search" className="aws-top-search" />}
    utilities={[
      { type: "button", iconName: "command-prompt", title: "CloudShell", ariaLabel: "CloudShell" },
      { type: "button", iconName: "notification", title: "Notifications", ariaLabel: "Notifications" },
      { type: "button", iconName: "support", title: "Support", ariaLabel: "Support" },
      { type: "button", iconName: "light-dark", title: `Switch to ${colorMode === "dark" ? "light" : "dark"} mode (Alt+M)`, ariaLabel: "Toggle color mode", onClick: toggleColorMode },
      { type: "menu-dropdown", text: session?.region === "us-east-1" ? "United States (N. Virginia)" : session?.region ?? "Global", items: [{ id: "global", text: "Global" }, { id: "us-east-1", text: "United States (N. Virginia)" }] },
      { type: "menu-dropdown", text: session?.user.display_name ?? "Account", description: session?.account.aws_account_id, items: [{ id: "signout", text: "Sign out" }], onItemClick: ({ detail }) => { if (detail.id === "signout") void signOut(); } },
    ]}
  />;
}
