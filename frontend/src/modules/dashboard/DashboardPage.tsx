import DatasetIcon from "@mui/icons-material/Dataset";
import HubIcon from "@mui/icons-material/Hub";
import ScienceIcon from "@mui/icons-material/Science";
import { Grid, Paper, Stack, Typography } from "@mui/material";

import { Project } from "../../api/client";

type DashboardPageProps = {
  projects: Project[];
};

export function DashboardPage({ projects }: DashboardPageProps) {
  const cards = [
    { label: "Projetos", value: projects.length, icon: <HubIcon color="primary" /> },
    { label: "Pipelines", value: "1", icon: <ScienceIcon color="secondary" /> },
    { label: "Banco de variantes", value: "VCF", icon: <DatasetIcon color="info" /> },
  ];

  return (
    <Stack spacing={3}>
      <Typography variant="h4">Dashboard</Typography>
      <Grid container spacing={2}>
        {cards.map((card) => (
          <Grid item xs={12} md={4} key={card.label}>
            <Paper elevation={0} sx={{ p: 2, border: "1px solid", borderColor: "divider" }}>
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Stack>
                  <Typography color="text.secondary" variant="body2">
                    {card.label}
                  </Typography>
                  <Typography variant="h4">{card.value}</Typography>
                </Stack>
                {card.icon}
              </Stack>
            </Paper>
          </Grid>
        ))}
      </Grid>
    </Stack>
  );
}
