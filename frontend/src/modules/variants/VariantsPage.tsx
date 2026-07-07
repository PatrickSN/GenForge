import FilterAltIcon from "@mui/icons-material/FilterAlt";
import RefreshIcon from "@mui/icons-material/Refresh";
import SearchIcon from "@mui/icons-material/Search";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import {
  Alert,
  Box,
  Button,
  Chip,
  FormControl,
  IconButton,
  InputLabel,
  LinearProgress,
  MenuItem,
  Paper,
  Select,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TablePagination,
  TableRow,
  TextField,
  Tooltip,
  Typography,
} from "@mui/material";
import { ChangeEvent, FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import Plot from "react-plotly.js";

import {
  Project,
  Variant,
  VariantFile,
  VariantProcessingJob,
  listVariantFiles,
  listVariantJobs,
  listVariants,
  uploadVcf,
} from "../../api/client";

type VariantsPageProps = {
  token: string;
  projects: Project[];
};

function formatDate(value: string): string {
  return new Date(value).toLocaleString();
}

function formatBytes(value: number): string {
  if (value < 1024) return `${value} B`;
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`;
  return `${(value / 1024 / 1024).toFixed(1)} MB`;
}

export function VariantsPage({ token, projects }: VariantsPageProps) {
  const [projectId, setProjectId] = useState(projects[0]?.id ?? "");
  const [chromosome, setChromosome] = useState("");
  const [geneId, setGeneId] = useState("");
  const [impact, setImpact] = useState("");
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [variants, setVariants] = useState<Variant[]>([]);
  const [total, setTotal] = useState(0);
  const [limit, setLimit] = useState(25);
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [statusLoading, setStatusLoading] = useState(false);
  const [variantFiles, setVariantFiles] = useState<VariantFile[]>([]);
  const [variantJobs, setVariantJobs] = useState<VariantProcessingJob[]>([]);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const selectedProject = useMemo(
    () => projects.find((project) => project.id === projectId),
    [projectId, projects],
  );

  const fileNameById = useMemo(
    () => new Map(variantFiles.map((file) => [file.id, file.original_filename])),
    [variantFiles],
  );

  const refreshProcessingStatus = useCallback(
    async (nextProjectId = projectId) => {
      if (!nextProjectId) {
        setVariantFiles([]);
        setVariantJobs([]);
        return;
      }
      setStatusLoading(true);
      try {
        const [filesPage, jobsPage] = await Promise.all([
          listVariantFiles(token, { projectId: nextProjectId, limit: 10, offset: 0 }),
          listVariantJobs(token, { projectId: nextProjectId, limit: 10, offset: 0 }),
        ]);
        setVariantFiles(filesPage.items);
        setVariantJobs(jobsPage.items);
      } catch (caught) {
        setError(caught instanceof Error ? caught.message : "Falha ao carregar status dos uploads");
      } finally {
        setStatusLoading(false);
      }
    },
    [projectId, token],
  );

  useEffect(() => {
    if (!projectId && projects[0]) {
      setProjectId(projects[0].id);
      return;
    }
    if (projectId && !projects.some((project) => project.id === projectId)) {
      setProjectId(projects[0]?.id ?? "");
      setVariants([]);
      setVariantFiles([]);
      setVariantJobs([]);
      setTotal(0);
      setOffset(0);
    }
  }, [projectId, projects]);

  useEffect(() => {
    void refreshProcessingStatus(projectId);
  }, [projectId, refreshProcessingStatus]);

  async function fetchVariants(nextOffset = offset, nextLimit = limit, keepMessage = false) {
    setError(null);
    if (!keepMessage) {
      setMessage(null);
    }
    if (!projectId) {
      setError("Crie ou selecione um projeto");
      return;
    }
    setLoading(true);
    try {
      const page = await listVariants(token, {
        projectId,
        chromosome,
        geneId,
        impact,
        start,
        end,
        limit: nextLimit,
        offset: nextOffset,
      });
      setVariants(page.items);
      setTotal(page.total);
      setLimit(page.limit);
      setOffset(page.offset);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Falha ao buscar variantes");
    } finally {
      setLoading(false);
    }
  }

  async function handleSearch(event?: FormEvent<HTMLFormElement>) {
    event?.preventDefault();
    await fetchVariants(0, limit);
  }

  async function handleUpload(event: ChangeEvent<HTMLInputElement>) {
    setError(null);
    setMessage(null);
    const file = event.target.files?.[0];
    if (!file || !projectId) return;
    const fileName = file.name.toLowerCase();
    if (!fileName.endsWith(".vcf") && !fileName.endsWith(".vcf.gz")) {
      setError("Envie um arquivo .vcf ou .vcf.gz.");
      event.target.value = "";
      return;
    }
    setUploading(true);
    try {
      const result = await uploadVcf(token, projectId, file);
      setVariantFiles((items) => [
        result.file,
        ...items.filter((item) => item.id !== result.file.id),
      ].slice(0, 10));
      setVariantJobs((items) => [
        result.job,
        ...items.filter((item) => item.id !== result.job.id),
      ].slice(0, 10));
      await refreshProcessingStatus(projectId);
      await fetchVariants(0, limit, true);
      setMessage(`Upload registrado. Job ${result.job.status}, arquivo ${result.file.status}.`);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Falha no upload");
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  }

  return (
    <Stack spacing={3}>
      <Stack direction={{ xs: "column", md: "row" }} justifyContent="space-between" alignItems={{ xs: "stretch", md: "center" }} spacing={2}>
        <Typography variant="h4">Variantes</Typography>
        <Button component="label" variant="contained" startIcon={<UploadFileIcon />} disabled={!projectId || uploading}>
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
                onChange={(event) => {
                  setProjectId(event.target.value);
                  setVariants([]);
                  setTotal(0);
                  setOffset(0);
                }}
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
            <TextField label="Inicio" type="number" value={start} onChange={(event) => setStart(event.target.value)} />
            <TextField label="Fim" type="number" value={end} onChange={(event) => setEnd(event.target.value)} />
            <Button type="submit" variant="outlined" startIcon={<SearchIcon />} sx={{ minWidth: 150 }} disabled={loading}>
              Buscar
            </Button>
          </Stack>
        </Stack>
      </Paper>

      {(loading || uploading || statusLoading) && <LinearProgress />}

      {projectId && (
        <Paper elevation={0} sx={{ p: 2, border: "1px solid", borderColor: "divider" }}>
          <Stack spacing={2}>
            <Stack direction="row" justifyContent="space-between" alignItems="center">
              <Typography variant="h6">Uploads e processamento</Typography>
              <Tooltip title="Atualizar status">
                <span>
                  <IconButton
                    aria-label="Atualizar status de uploads e jobs"
                    onClick={() => void refreshProcessingStatus(projectId)}
                    disabled={statusLoading}
                  >
                    <RefreshIcon />
                  </IconButton>
                </span>
              </Tooltip>
            </Stack>
            <Stack direction={{ xs: "column", lg: "row" }} spacing={3}>
              <Box sx={{ flex: 1, minWidth: 0, overflowX: "auto" }}>
                <Typography variant="subtitle1">Arquivos VCF</Typography>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Arquivo</TableCell>
                      <TableCell>Tamanho</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Criado em</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {variantFiles.map((file) => (
                      <TableRow key={file.id}>
                        <TableCell>{file.original_filename}</TableCell>
                        <TableCell>{formatBytes(file.size_bytes)}</TableCell>
                        <TableCell>
                          <Chip size="small" label={file.status} />
                        </TableCell>
                        <TableCell>{formatDate(file.created_at)}</TableCell>
                      </TableRow>
                    ))}
                    {variantFiles.length === 0 && (
                      <TableRow>
                        <TableCell colSpan={4}>
                          <Typography color="text.secondary">Nenhum arquivo enviado.</Typography>
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </Box>
              <Box sx={{ flex: 1, minWidth: 0, overflowX: "auto" }}>
                <Typography variant="subtitle1">Jobs</Typography>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Arquivo</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Variantes</TableCell>
                      <TableCell>Atualizado em</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {variantJobs.map((job) => (
                      <TableRow key={job.id}>
                        <TableCell>{fileNameById.get(job.file_id) ?? job.file_id}</TableCell>
                        <TableCell>
                          <Chip
                            size="small"
                            color={job.status === "failed" ? "error" : job.status === "finished" ? "success" : "primary"}
                            label={job.status}
                          />
                        </TableCell>
                        <TableCell>{job.variants_inserted}</TableCell>
                        <TableCell>{formatDate(job.updated_at)}</TableCell>
                      </TableRow>
                    ))}
                    {variantJobs.length === 0 && (
                      <TableRow>
                        <TableCell colSpan={4}>
                          <Typography color="text.secondary">Nenhum job registrado.</Typography>
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </Box>
            </Stack>
          </Stack>
        </Paper>
      )}

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
                xaxis: { title: { text: "Cromossomo" } },
                yaxis: { title: { text: "Posicao" } },
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
                  {variants.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={6}>
                        <Typography color="text.secondary">Nenhuma variante encontrada.</Typography>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </Box>
            <TablePagination
              component="div"
              count={total}
              page={Math.floor(offset / limit)}
              rowsPerPage={limit}
              rowsPerPageOptions={[10, 25, 50, 100]}
              labelRowsPerPage="Linhas por pagina"
              onPageChange={(_, page) => void fetchVariants(page * limit, limit)}
              onRowsPerPageChange={(event) => {
                const nextLimit = Number(event.target.value);
                setLimit(nextLimit);
                void fetchVariants(0, nextLimit);
              }}
            />
          </Box>
        </Stack>
      </Paper>
    </Stack>
  );
}
