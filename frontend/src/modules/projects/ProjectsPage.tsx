import AddIcon from "@mui/icons-material/Add";
import CloseIcon from "@mui/icons-material/Close";
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit";
import RefreshIcon from "@mui/icons-material/Refresh";
import SaveIcon from "@mui/icons-material/Save";
import VisibilityIcon from "@mui/icons-material/Visibility";
import {
  Alert,
  Box,
  Button,
  Chip,
  Divider,
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
import { FormEvent, useCallback, useEffect, useState } from "react";

import {
  Project,
  createProject,
  deleteProject,
  getProject,
  listProjects,
  updateProject,
} from "../../api/client";

type ProjectsPageProps = {
  token: string;
  onProjectsLoaded: (projects: Project[]) => void;
};

function formatDate(value: string): string {
  return new Date(value).toLocaleString();
}

export function ProjectsPage({ token, onProjectsLoaded }: ProjectsPageProps) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [projectName, setProjectName] = useState("");
  const [description, setDescription] = useState("");
  const [editingProjectId, setEditingProjectId] = useState<string | null>(null);
  const [editProjectName, setEditProjectName] = useState("");
  const [editDescription, setEditDescription] = useState("");
  const [savingProjectId, setSavingProjectId] = useState<string | null>(null);
  const [deletingProjectId, setDeletingProjectId] = useState<string | null>(null);
  const [loadingDetails, setLoadingDetails] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setError(null);
    try {
      const data = await listProjects(token);
      setProjects(data);
      onProjectsLoaded(data);
      setSelectedProject((current) => {
        if (!current) return current;
        return data.find((project) => project.id === current.id) ?? null;
      });
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Falha ao listar projetos");
    }
  }, [onProjectsLoaded, token]);

  const openProjectDetails = useCallback(async (projectId: string) => {
    setError(null);
    setLoadingDetails(true);
    try {
      setSelectedProject(await getProject(token, projectId));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Falha ao carregar detalhes do projeto");
    } finally {
      setLoadingDetails(false);
    }
  }, [token]);

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    try {
      const project = await createProject(token, {
        project_name: projectName.trim(),
        description: description.trim() || undefined,
      });
      setProjectName("");
      setDescription("");
      await refresh();
      await openProjectDetails(project.id);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Falha ao criar projeto");
    }
  }

  function startEditing(project: Project) {
    setEditingProjectId(project.id);
    setEditProjectName(project.project_name);
    setEditDescription(project.description ?? "");
    setError(null);
  }

  function cancelEditing() {
    setEditingProjectId(null);
    setEditProjectName("");
    setEditDescription("");
  }

  async function handleUpdate(projectId: string) {
    const nextName = editProjectName.trim();
    if (!nextName) {
      setError("Informe o nome do projeto.");
      return;
    }
    setError(null);
    setSavingProjectId(projectId);
    try {
      const project = await updateProject(token, projectId, {
        project_name: nextName,
        description: editDescription.trim() || null,
      });
      const nextProjects = projects.map((item) => (item.id === projectId ? project : item));
      setProjects(nextProjects);
      onProjectsLoaded(nextProjects);
      setSelectedProject((current) => (current?.id === projectId ? project : current));
      cancelEditing();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Falha ao atualizar projeto");
    } finally {
      setSavingProjectId(null);
    }
  }

  async function handleDelete(project: Project) {
    const confirmed = window.confirm(`Excluir o projeto "${project.project_name}"?`);
    if (!confirmed) return;
    setError(null);
    setDeletingProjectId(project.id);
    try {
      await deleteProject(token, project.id);
      const nextProjects = projects.filter((item) => item.id !== project.id);
      setProjects(nextProjects);
      onProjectsLoaded(nextProjects);
      setSelectedProject((current) => (current?.id === project.id ? null : current));
      if (editingProjectId === project.id) {
        cancelEditing();
      }
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Falha ao excluir projeto");
    } finally {
      setDeletingProjectId(null);
    }
  }

  useEffect(() => {
    void refresh();
  }, [refresh]);

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

      {selectedProject && (
        <Paper elevation={0} sx={{ p: 2, border: "1px solid", borderColor: "divider" }}>
          <Stack spacing={2}>
            <Stack direction={{ xs: "column", md: "row" }} justifyContent="space-between" spacing={1}>
              <Box>
                <Typography variant="overline" color="text.secondary">
                  Projeto selecionado
                </Typography>
                <Typography variant="h5">{selectedProject.project_name}</Typography>
              </Box>
              <Stack direction="row" spacing={1} flexWrap="wrap">
                <Chip label={`Criado em ${formatDate(selectedProject.created_at)}`} />
                <Chip label={`Atualizado em ${formatDate(selectedProject.updated_at)}`} />
              </Stack>
            </Stack>
            <Divider />
            <Stack direction={{ xs: "column", md: "row" }} spacing={2}>
              <Box sx={{ flex: 1, minWidth: 0 }}>
                <Typography color="text.secondary" variant="body2">
                  Descricao
                </Typography>
                <Typography>{selectedProject.description || "-"}</Typography>
              </Box>
              <Box sx={{ flex: 1, minWidth: 0 }}>
                <Typography color="text.secondary" variant="body2">
                  ID do projeto
                </Typography>
                <Typography sx={{ wordBreak: "break-all" }}>{selectedProject.id}</Typography>
              </Box>
            </Stack>
          </Stack>
        </Paper>
      )}

      <Paper elevation={0} sx={{ border: "1px solid", borderColor: "divider", overflow: "hidden" }}>
        <Box sx={{ overflowX: "auto" }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Nome</TableCell>
                <TableCell>Descricao</TableCell>
                <TableCell>Criado em</TableCell>
                <TableCell align="right">Acoes</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {projects.map((project) => {
                const isEditing = editingProjectId === project.id;
                return (
                  <TableRow key={project.id} selected={selectedProject?.id === project.id}>
                    <TableCell>
                      {isEditing ? (
                        <TextField
                          value={editProjectName}
                          onChange={(event) => setEditProjectName(event.target.value)}
                          size="small"
                          required
                          fullWidth
                        />
                      ) : (
                        project.project_name
                      )}
                    </TableCell>
                    <TableCell>
                      {isEditing ? (
                        <TextField
                          value={editDescription}
                          onChange={(event) => setEditDescription(event.target.value)}
                          size="small"
                          fullWidth
                        />
                      ) : (
                        project.description ?? "-"
                      )}
                    </TableCell>
                    <TableCell>{formatDate(project.created_at)}</TableCell>
                    <TableCell align="right">
                      {isEditing ? (
                        <Stack direction="row" spacing={0.5} justifyContent="flex-end">
                          <Tooltip title="Salvar">
                            <span>
                              <IconButton
                                aria-label={`Salvar ${project.project_name}`}
                                onClick={() => void handleUpdate(project.id)}
                                disabled={savingProjectId === project.id}
                              >
                                <SaveIcon />
                              </IconButton>
                            </span>
                          </Tooltip>
                          <Tooltip title="Cancelar">
                            <IconButton
                              aria-label={`Cancelar edicao de ${project.project_name}`}
                              onClick={cancelEditing}
                            >
                              <CloseIcon />
                            </IconButton>
                          </Tooltip>
                        </Stack>
                      ) : (
                        <Stack direction="row" spacing={0.5} justifyContent="flex-end">
                          <Tooltip title="Abrir detalhes">
                            <span>
                              <IconButton
                                aria-label={`Abrir detalhes de ${project.project_name}`}
                                onClick={() => void openProjectDetails(project.id)}
                                disabled={loadingDetails}
                              >
                                <VisibilityIcon />
                              </IconButton>
                            </span>
                          </Tooltip>
                          <Tooltip title="Editar">
                            <IconButton
                              aria-label={`Editar ${project.project_name}`}
                              onClick={() => startEditing(project)}
                            >
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Excluir">
                            <span>
                              <IconButton
                                aria-label={`Excluir ${project.project_name}`}
                                onClick={() => void handleDelete(project)}
                                disabled={deletingProjectId === project.id}
                              >
                                <DeleteIcon />
                              </IconButton>
                            </span>
                          </Tooltip>
                        </Stack>
                      )}
                    </TableCell>
                  </TableRow>
                );
              })}
              {projects.length === 0 && (
                <TableRow>
                  <TableCell colSpan={4}>
                    <Typography color="text.secondary">Nenhum projeto cadastrado.</Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </Box>
      </Paper>
    </Stack>
  );
}
