import LockOutlinedIcon from "@mui/icons-material/LockOutlined";
import PersonAddAlt1Icon from "@mui/icons-material/PersonAddAlt1";
import {
  Alert,
  Box,
  Button,
  Paper,
  Stack,
  TextField,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
} from "@mui/material";
import { FormEvent, useState } from "react";

import { login, register } from "../../api/client";

type LoginPageProps = {
  onToken: (token: string) => void;
};

export function LoginPage({ onToken }: LoginPageProps) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("admin@genforge.local");
  const [fullName, setFullName] = useState("GenForge Admin");
  const [password, setPassword] = useState("genforge123");
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    try {
      if (mode === "register") {
        await register(email, fullName, password);
      }
      const response = await login(email, password);
      onToken(response.access_token);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Falha de autenticacao");
    }
  }

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "grid",
        placeItems: "center",
        bgcolor: "background.default",
        px: 2,
      }}
    >
      <Paper
        component="form"
        onSubmit={handleSubmit}
        elevation={0}
        sx={{
          width: "100%",
          maxWidth: 440,
          p: 4,
          border: "1px solid",
          borderColor: "divider",
        }}
      >
        <Stack spacing={3}>
          <Stack direction="row" spacing={1.5} alignItems="center">
            {mode === "login" ? <LockOutlinedIcon color="primary" /> : <PersonAddAlt1Icon color="primary" />}
            <Typography variant="h5" fontWeight={700}>
              GenForge
            </Typography>
          </Stack>

          <ToggleButtonGroup
            color="primary"
            exclusive
            value={mode}
            onChange={(_, value: "login" | "register" | null) => value && setMode(value)}
            fullWidth
          >
            <ToggleButton value="login">Entrar</ToggleButton>
            <ToggleButton value="register">Criar acesso</ToggleButton>
          </ToggleButtonGroup>

          {error && <Alert severity="error">{error}</Alert>}

          {mode === "register" && (
            <TextField
              label="Nome"
              value={fullName}
              onChange={(event) => setFullName(event.target.value)}
              required
              fullWidth
            />
          )}
          <TextField
            label="E-mail"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
            fullWidth
          />
          <TextField
            label="Senha"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
            fullWidth
          />
          <Button type="submit" variant="contained" size="large">
            {mode === "login" ? "Entrar" : "Criar e entrar"}
          </Button>
        </Stack>
      </Paper>
    </Box>
  );
}
