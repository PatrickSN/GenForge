import { createTheme } from "@mui/material/styles";

export const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#1f6f68",
    },
    secondary: {
      main: "#8b5e34",
    },
    background: {
      default: "#f6f8f7",
      paper: "#ffffff",
    },
    info: {
      main: "#315c9c",
    },
  },
  typography: {
    fontFamily: [
      "Inter",
      "Roboto",
      "Arial",
      "sans-serif",
    ].join(","),
    h4: {
      fontWeight: 700,
      letterSpacing: 0,
    },
    h6: {
      fontWeight: 700,
      letterSpacing: 0,
    },
    button: {
      textTransform: "none",
      fontWeight: 700,
    },
  },
  shape: {
    borderRadius: 8,
  },
});
