import FilterAltIcon from "@mui/icons-material/FilterAlt";
import SearchIcon from "@mui/icons-material/Search";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import {
  Alert,
  Box,
  Button,
  FormControl,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { ChangeEvent, FormEvent, useMemo, useState } from "react";
import Plot from "react-plotly.js";

import { Project, Variant, listVariants, uploadVcf } from "../../api/client";

type VariantsPageProps = {
  token: string;
  projects: Project[];
};

export function VariantsPage({ token, projects }: VariantsPageProps) {
  const [projectId, setProjectId] = useState(projects[0]?.id ?? "");
  const [chromosome, setChromosome] = useState("");
  const [geneId, setGeneId] = useState("");
  const [impact, setImpact] = useState("");
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [variants, setVariants] = useState<Variant[]>([]);
  const [total, setTotal] = useState(0);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const selectedProject = useMemo(
    () => projects.find((project) => project.id === projectId),
    [projectId, projects],
  );

  async function handleSearch(event?: FormEvent<HTMLFormElement>) {
    event?.preventDefault();
    setError(null);
    setMessage(null);
    if (!projectId) {
      setError("Crie ou selecione um projeto");
      return;
    }
    try {
      const page = await listVariants(token, {
        projectId,
        chromosome,
        geneId,
        impact,
        start,
        end,
      });
      setVariants(page.items);
      setTotal(page.total);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Falha ao buscar variantes");
    }
  }

  async function handleUpload(event: ChangeEvent<HTMLInputElement>) {
    setError(null);
    setMessage(null);
    const file = event.target.files?.[0];
    if (!file || !projectId) return;
    try {
      const result = await uploadVcf(token, projectId, file);
      setMessage(`Upload registrado: job ${result.job.status}`);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Falha no upload");
    } finally {
      event.target.value = "";
    }
  }

  return (
    <Stack spacing={3}>
      <Stack direction={{ xs: "column", md: "row" }} justifyContent="space-between" alignItems={{ xs: "stretch", md: "center" }} spacing={2}>
        <Typography variant="h4">Variantes</Typography>
        <Button component="label" variant="contained" startIcon={<UploadFileIcon />} disabled={!projectId}>
          Upload VCF
          <input hidden type="file" accept=".vcf,.vcf.gz" onChange={handleUpload} />
        </Button>
      </Stack>

      {error && <Alert severity="error">{error}</Alert>}
      {message && <Alert severity="success">{message}</Alert>}

      <Paper component="form" onSubmit={handleSearch} elevation={0} sx={{ p: 2, border: "1px solid", borderColor: "divider" }}>
        <Stack spacing={2}>
          <Stack direction="row" spacing={1} alignItems="center">
            <FilterAltIcon color="primary" />
            <Typography variant="h6">{selectedProject?.project_name ?? "Consulta"}</Typography>
          </Stack>
          <Stack direction={{ xs: "column", lg: "row" }} spacing={2}>
            <FormControl fullWidth>
              <InputLabel id="project-select-label">Projeto</InputLabel>
              <Select
                labelId="project-select-label"
                label="Projeto"
                value={projectId}
                onChange={(event) => setProjectId(event.target.value)}
              >
                {projects.map((project) => (
                  <MenuItem key={project.id} value={project.id}>
                    {project.project_name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField label="Cromossomo" value={chromosome} onChange={(event) => setChromosome(event.target.value)} />
            <TextField label="Gene" value={geneId} onChange={(event) => setGeneId(event.target.value)} />
            <TextField label="Impacto" value={impact} onChange={(event) => setImpact(event.target.value)} />
            <TextField label="Inicio" value={start} onChange={(event) => setStart(event.target.value)} />
            <TextField label="Fim" value={end} onChange={(event) => setEnd(event.target.value)} />
            <Button type="submit" variant="outlined" startIcon={<SearchIcon />} sx={{ minWidth: 150 }}>
              Buscar
            </Button>
          </Stack>
        </Stack>
      </Paper>

      <Paper elevation={0} sx={{ p: 2, border: "1px solid", borderColor: "divider" }}>
        <Stack direction={{ xs: "column", lg: "row" }} spacing={3}>
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Typography variant="h6">Distribuicao</Typography>
            <Plot
              data={[
                {
                  x: variants.map((variant) => variant.chromosome),
                  y: variants.map((variant) => variant.position),
                  mode: "markers",
                  type: "scatter",
                  marker: { color: "#1f6f68", size: 8 },
                },
              ]}
              layout={{
                autosize: true,
                height: 320,
                margin: { l: 50, r: 20, t: 20, b: 45 },
                paper_bgcolor: "rgba(0,0,0,0)",
                plot_bgcolor: "rgba(0,0,0,0)",
                xaxis: { title: "Cromossomo" },
                yaxis: { title: "Posicao" },
              }}
              style={{ width: "100%" }}
              config={{ displayModeBar: false, responsive: true }}
            />
          </Box>
          <Box sx={{ flex: 2, minWidth: 0 }}>
            <Typography variant="h6">{total} variantes</Typography>
            <Box sx={{ overflowX: "auto" }}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Cromossomo</TableCell>
                    <TableCell>Posicao</TableCell>
                    <TableCell>Ref</TableCell>
                    <TableCell>Alt</TableCell>
                    <TableCell>Impacto</TableCell>
                    <TableCell>Gene</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {variants.map((variant) => (
                    <TableRow key={variant.id}>
                      <TableCell>{variant.chromosome}</TableCell>
                      <TableCell>{variant.position}</TableCell>
                      <TableCell>{variant.reference}</TableCell>
                      <TableCell>{variant.alternative}</TableCell>
                      <TableCell>{variant.impact ?? "-"}</TableCell>
                      <TableCell>{variant.gene_id ?? "-"}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Box>
          </Box>
        </Stack>
      </Paper>
    </Stack>
  );
}
