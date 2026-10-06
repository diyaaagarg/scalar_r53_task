import { Box, Button, Container, Header, SpaceBetween } from "@cloudscape-design/components";

export function ComingSoonPage({ title, description }: Readonly<{ title: string; description: string }>) {
  return <div className="coming-soon"><Container header={<Header variant="h1">{title}</Header>}><SpaceBetween size="l"><Box variant="p">{description}</Box><Box textAlign="center" padding="xl"><Box variant="h2">Coming soon</Box><Box color="text-body-secondary" padding={{ top: "s", bottom: "l" }}>This Route 53 experience is planned for a later phase.</Box><Button variant="primary" disabled>Get started</Button></Box></SpaceBetween></Container></div>;
}
