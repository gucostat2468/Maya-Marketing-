import type { ReactNode } from "react";
import { createHashRouter, RouterProvider } from "react-router";

import { AppShell } from "./components/layout/AppShell";
import { NAV_ITEMS } from "./components/layout/nav";
import { Integrations } from "./pages/Integrations";
import { NotFound } from "./pages/NotFound";
import { Overview } from "./pages/Overview";
import { PlannedModule } from "./pages/PlannedModule";
import { Settings } from "./pages/Settings";

// Hash router: funciona igual no navegador (dev) e dentro do Tauri (arquivos locais).
const IMPLEMENTED: Record<string, ReactNode> = {
  overview: <Overview />,
  integrations: <Integrations />,
  settings: <Settings />,
};

const router = createHashRouter([
  {
    path: "/",
    element: <AppShell />,
    children: [
      ...NAV_ITEMS.map((item) => ({
        path: item.path === "/" ? undefined : item.path.slice(1),
        index: item.path === "/" ? true : undefined,
        element: IMPLEMENTED[item.key] ?? <PlannedModule moduleKey={item.key} />,
      })),
      { path: "*", element: <NotFound /> },
    ],
  },
]);

export function App() {
  return <RouterProvider router={router} />;
}
