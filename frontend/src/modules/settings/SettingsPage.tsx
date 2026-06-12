import StorageIcon from "@mui/icons-material/Storage";
import {
  Chip,
  Divider,
  FormControlLabel,
  Paper,
  Stack,
  Switch,
  Typography,
} from "@mui/material";

export function SettingsPage() {
  return (
    <Stack spacing={3}>
      <Typography variant="h4">Configuracoes</Typography>
      <Paper elevation={0} sx={{ p: 2, border: "1px solid", borderColor: "divider" }}>
        <Stack spacing={2}>
          <Stack direction="row" spacing={1.5} alignItems="center">
            <StorageIcon color="primary" />
            <Typography variant="h6">Ambiente</Typography>
          </Stack>
          <Stack direction="row" spacing={1} flexWrap="wrap">
            <Chip label="FastAPI" />
            <Chip label="PostgreSQL" />
            <Chip label="Redis" />
            <Chip label="Celery" />
            <Chip label="SnpEff futuro" variant="outlined" />
          </Stack>
          <Divider />
          <FormControlLabel control={<Switch checked disabled />} label="Processamento assíncrono de VCF" />
          <FormControlLabel control={<Switch disabled />} label="Anotação SnpEff" />
          <FormControlLabel control={<Switch disabled />} label="GWAS" />
          <FormControlLabel control={<Switch disabled />} label="Seleção genômica" />
        </Stack>
      </Paper>
    </Stack>
  );
}
