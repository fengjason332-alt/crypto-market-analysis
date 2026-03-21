import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { LanguageProvider } from "./contexts/LanguageContext";
import { WatchlistProvider } from "./contexts/WatchlistContext";
import "./styles/globals.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <LanguageProvider>
      <WatchlistProvider>
        <App />
      </WatchlistProvider>
    </LanguageProvider>
  </React.StrictMode>
);
