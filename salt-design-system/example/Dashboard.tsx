import React from "react";
import {
  SaltProvider,
  BorderLayout,
  GridLayout,
  GridItem,
  StackLayout,
  FlexLayout,
  Card,
  Text,
  Display,
  Button,
  Avatar,
  Link,
  StatusIndicator
} from "@salt-ds/core";
import { 
  DownloadIcon, 
  RefreshIcon, 
  FilterIcon, 
  SettingsIcon 
} from "@salt-ds/icons";

// Helper component for KPI Cards (Pattern composition)
const MetricCard = ({ title, value, trend, status }: { title: string, value: string, trend: string, status: "success" | "error" }) => (
  <Card>
    <StackLayout gap={1}>
      <Text color="secondary" styleAs="label">{title}</Text>
      <Display styleAs="h3">{value}</Display>
      <FlexLayout align="center" gap={1}>
        <StatusIndicator status={status} />
        <Text styleAs="small">{trend}</Text>
      </FlexLayout>
    </StackLayout>
  </Card>
);

export const Dashboard = () => {
  return (
    // Rule #2: Root Provider & Rule #3: Theming (Light/Medium)
    <SaltProvider mode="light" density="medium">
      {/* Rule #2: Layout - Using BorderLayout for scaffolding */}
      <BorderLayout className="dashboard-container">
        
        {/* Header Region */}
        <BorderLayout.Header>
          <StackLayout direction="row" justify="space-between" align="center" style={{ padding: "var(--salt-spacing-300)" }}>
            <FlexLayout align="center" gap={2}>
              {/* Rule #1: Icons from @salt-ds/icons */}
              <Avatar size={2} name="Salt DS" />
              <Text styleAs="h3">Analytics Dashboard</Text>
            </FlexLayout>
            <FlexLayout gap={1}>
              <Button sentiment="neutral" variant="secondary">
                <FilterIcon aria-hidden /> Filter
              </Button>
              <Button sentiment="accented">
                <DownloadIcon aria-hidden /> Export
              </Button>
            </FlexLayout>
          </StackLayout>
        </BorderLayout.Header>

        {/* Main Content Region */}
        <BorderLayout.Main>
          <StackLayout gap={4} style={{ padding: "var(--salt-spacing-300)" }}>
            
            {/* Rule #2: Layout - Using GridLayout for dashboard grid */}
            <GridLayout columns={12} gap={3}>
              
              {/* Row 1: KPI Metrics (Spanning 3 columns each) */}
              <GridItem colSpan={{ xs: 12, sm: 6, md: 3 }}>
                <MetricCard title="Total Revenue" value="$4.2M" trend="+12% vs last month" status="success" />
              </GridItem>
              <GridItem colSpan={{ xs: 12, sm: 6, md: 3 }}>
                <MetricCard title="Active Users" value="12,450" trend="+5% new signups" status="success" />
              </GridItem>
              <GridItem colSpan={{ xs: 12, sm: 6, md: 3 }}>
                <MetricCard title="Bounce Rate" value="42.5%" trend="-2% improvement" status="success" />
              </GridItem>
              <GridItem colSpan={{ xs: 12, sm: 6, md: 3 }}>
                <MetricCard title="Server Uptime" value="99.9%" trend="Stable" status="success" />
              </GridItem>

              {/* Row 2: Main Chart Area (Spans 8 cols) & Sidebar (Spans 4 cols) */}
              <GridItem colSpan={{ xs: 12, md: 8 }}>
                <Card style={{ height: "100%", minHeight: "400px" }}>
                  <StackLayout gap={2}>
                    <FlexLayout justify="space-between" align="center">
                      <Text styleAs="h4">Traffic Overview</Text>
                      <Button variant="cta" sentiment="neutral">
                        <RefreshIcon />
                      </Button>
                    </FlexLayout>
                    <div style={{ 
                      flexGrow: 1, 
                      background: "var(--salt-container-secondary-background)", 
                      display: "flex", 
                      alignItems: "center", 
                      justifyContent: "center" 
                    }}>
                      <Text color="secondary">Chart Placeholder</Text>
                    </div>
                  </StackLayout>
                </Card>
              </GridItem>

              <GridItem colSpan={{ xs: 12, md: 4 }}>
                <Card>
                  <StackLayout gap={3}>
                    <FlexLayout justify="space-between" align="center">
                      <Text styleAs="h4">Recent Activity</Text>
                      <Link href="#">View All</Link>
                    </FlexLayout>
                    <StackLayout gap={2} separators>
                      <FlexLayout align="center" gap={1}>
                        <Avatar size={1} name="User A" />
                        <StackLayout gap={0}>
                          <Text>User A updated profile</Text>
                          <Text styleAs="small" color="secondary">2 mins ago</Text>
                        </StackLayout>
                      </FlexLayout>
                      <FlexLayout align="center" gap={1}>
                        <Avatar size={1} name="User B" />
                        <StackLayout gap={0}>
                          <Text>System Alert: High CPU</Text>
                          <Text styleAs="small" color="secondary">15 mins ago</Text>
                        </StackLayout>
                      </FlexLayout>
                    </StackLayout>
                  </StackLayout>
                </Card>
              </GridItem>

            </GridLayout>
          </StackLayout>
        </BorderLayout.Main>

      </BorderLayout>
    </SaltProvider>
  );
};