import BiotechIcon from "@mui/icons-material/Biotech";
import DashboardIcon from "@mui/icons-material/Dashboard";
import FolderIcon from "@mui/icons-material/Folder";
import LogoutIcon from "@mui/icons-material/Logout";
import SettingsIcon from "@mui/icons-material/Settings";
import {
  AppBar,
  Box,
  Button,
  Container,
  Drawer,
  IconButton,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
} from "@mui/material";
import { useEffect, useState } from "react";

import { Project, listProjects } from "./api/client";
import { LoginPage } from "./modules/auth/LoginPage";
import { DashboardPage } from "./modules/dashboard/DashboardPage";
import { ProjectsPage } from "./modules/projects/ProjectsPage";
import { SettingsPage } from "./modules/settings/SettingsPage";
import { VariantsPage } from "./modules/variants/VariantsPage";

type View = "dashboard" | "projects" | "variants" | "settings";

const drawerWidth = 240;

const navItems: Array<{ view: View; label: string; icon: JSX.Element }> = [
  { view: "dashboard", label: "Dashboard", icon: <DashboardIcon /> },
  { view: "projects", label: "Projetos", icon: <FolderIcon /> },
  { view: "variants", label: "Variantes", icon: <BiotechIcon /> },
  { view: "settings", label: "Configuracoes", icon: <SettingsIcon /> },
];

export default function App() {
  const [token, setToken] = useState(() => localStorage.getItem("genforge.token"));
  const [view, setView] = useState<View>("dashboard");
  const [projects, setProjects] = useState<Project[]>([]);

  useEffect(() => {
    if (token) {
      localStorage.setItem("genforge.token", token);
      listProjects(token)
        .then(setProjects)
        .catch(() => setProjects([]));
    } else {
      localStorage.removeItem("genforge.token");
    }
  }, [token]);

  if (!token) {
    return <LoginPage onToken={setToken} />;
  }

  return (
    <Box sx={{ display: "flex", minHeight: "100vh", bgcolor: "background.default" }}>
      <AppBar position="fixed" elevation={0} sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <BiotechIcon sx={{ mr: 1 }} />
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            GenForge
          </Typography>
          <IconButton color="inherit" aria-label="Sair" onClick={() => setToken(null)}>
            <LogoutIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          [`& .MuiDrawer-paper`]: {
            width: drawerWidth,
            boxSizing: "border-box",
            borderRight: "1px solid",
            borderColor: "divider",
          },
        }}
      >
        <Toolbar />
        <List sx={{ px: 1 }}>
          {navItems.map((item) => (
            <ListItemButton
              key={item.view}
              selected={view === item.view}
              onClick={() => setView(item.view)}
              sx={{ borderRadius: 1, mb: 0.5 }}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.label} />
            </ListItemButton>
          ))}
        </List>
      </Drawer>

      <Box component="main" sx={{ flexGrow: 1, minWidth: 0 }}>
        <Toolbar />
        <Container maxWidth="xl" sx={{ py: 3 }}>
          {view === "dashboard" && <DashboardPage projects={projects} />}
          {view === "projects" && <ProjectsPage token={token} onProjectsLoaded={setProjects} />}
          {view === "variants" && <VariantsPage token={token} projects={projects} />}
          {view === "settings" && <SettingsPage />}
          {projects.length === 0 && view !== "projects" && (
            <Box sx={{ mt: 3 }}>
              <Button variant="outlined" startIcon={<FolderIcon />} onClick={() => setView("projects")}>
                Criar projeto
              </Button>
            </Box>
          )}
        </Container>
      </Box>
    </Box>
  );
}
