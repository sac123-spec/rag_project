import React from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent
} from "@/components/ui/Card";
import {
  BarChart,
  Bar,
  Tooltip,
  XAxis,
  YAxis,
  ResponsiveContainer
} from "recharts";

const docData = [
  { name: "Mon", value: 12 },
  { name: "Tue", value: 18 },
  { name: "Wed", value: 10 },
  { name: "Thu", value: 22 },
  { name: "Fri", value: 15 },
  { name: "Sat", value: 8 },
  { name: "Sun", value: 14 }
];

const DashboardPage: React.FC = () => {
  return (
    <div className="grid gap-6 grid-cols-1 lg:grid-cols-3">
      <Card>
        <CardHeader>
          <CardTitle>Total Documents</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-3xl font-bold text-primary">47</p>
          <p className="text-muted-foreground text-sm">Across the system</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Total Queries</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-3xl font-bold text-primary">1,204</p>
          <p className="text-muted-foreground text-sm">Last 30 days</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Model Accuracy</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-3xl font-bold text-primary">92%</p>
          <p className="text-muted-foreground text-sm">After recent training</p>
        </CardContent>
      </Card>

      <Card className="col-span-1 lg:col-span-3">
        <CardHeader>
          <CardTitle>Documents Processed (Last 7 Days)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="w-full h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={docData}>
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="hsl(var(--primary))" radius={6} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default DashboardPage;
