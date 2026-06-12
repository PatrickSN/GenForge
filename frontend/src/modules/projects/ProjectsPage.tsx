import AddIcon from "@mui/icons-material/Add";
import RefreshIcon from "@mui/icons-material/Refresh";
import {
  Alert,
  Box,
  Button,
  IconButton,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Tooltip,
  Typography,
} from "@mui/material";
import { FormEvent, useEffect, useState } from "react";

import { Project, createProject, listProjects } from "../../api/client";

type ProjectsPageProps = {
  token: string;
  onProjectsLoaded: (projects: Project[]) => void;
};

export function ProjectsPage({ token, onProjectsLoaded }: ProjectsPageProps) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [projectName, setProjectName] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    setError(null);
    try {
      const data = await listProjects(token);
      setProjects(data);
      onProjectsLoaded(data);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Falha ao listar projetos");
    }
  }

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    try {
      await createProject(token, { project_name: projectName, description });
      setProjectName("");
      setDescription("");
      await refresh();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Falha ao criar projeto");
    }
  }

  useEffect(() => {
    void refresh();
  }, []);

  return (
    <Stack spacing={3}>
      <Stack direction="row" justifyContent="space-between" alignItems="center">
        <Typography variant="h4">Projetos</Typography>
        <Tooltip title="Atualizar">
          <IconButton onClick={refresh} aria-label="Atualizar projetos">
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Stack>

      {error && <Alert severity="error">{error}</Alert>}

      <Paper component="form" onSubmit={handleCreate} elevation={0} sx={{ p: 2, border: "1px solid", borderColor: "divider" }}>
        <Stack direction={{ xs: "column", md: "row" }} spacing={2}>
          <TextField
            label="Projeto"
            value={projectName}
            onChange={(event) => setProjectName(event.target.value)}
            required
            fullWidth
          />
          <TextField
            label="Descricao"
            value={description}
            onChange={(event) => setDescription(event.target.value)}
            fullWidth
          />
          <Button type="submit" variant="contained" startIcon={<AddIcon />} sx={{ minWidth: 160 }}>
            Criar
          </Button>
        </Stack>
      </Paper>

      <Paper elevation={0} sx={{ border: "1px solid", borderColor: "divider", overflow: "hidden" }}>
        <Box sx={{ overflowX: "auto" }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Nome</TableCell>
                <TableCell>Descricao</TableCell>
                <TableCell>Criado em</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {projects.map((project) => (
                <TableRow key={project.id}>
                  <TableCell>{project.project_name}</TableCell>
                  <TableCell>{project.description ?? "-"}</TableCell>
                  <TableCell>{new Date(project.created_at).toLocaleString()}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Box>
      </Paper>
    </Stack>
  );
}
