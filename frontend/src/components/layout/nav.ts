import {
  BarChart3,
  BookOpen,
  Brush,
  Filter,
  Gauge,
  Image,
  Lightbulb,
  type LucideIcon,
  Megaphone,
  Plug,
  Search,
  Settings,
  TrendingUp,
  Users,
} from "lucide-react";

export interface NavItem {
  key: string; // igual à chave do registro de módulos no backend
  label: string;
  path: string;
  icon: LucideIcon;
}

export const NAV_GROUPS: { title: string; items: NavItem[] }[] = [
  {
    title: "Visão",
    items: [
      { key: "overview", label: "Visão Geral", path: "/", icon: Gauge },
      { key: "reports", label: "Relatórios", path: "/relatorios", icon: BarChart3 },
    ],
  },
  {
    title: "Aquisição",
    items: [
      { key: "campaigns", label: "Campanhas", path: "/campanhas", icon: Megaphone },
      { key: "google_ads", label: "Google Ads", path: "/google-ads", icon: Search },
      { key: "meta_ads", label: "Meta Ads", path: "/meta-ads", icon: Megaphone },
      { key: "social", label: "Social Growth", path: "/social", icon: TrendingUp },
    ],
  },
  {
    title: "Comercial",
    items: [
      { key: "leads", label: "Leads", path: "/leads", icon: Users },
      { key: "funnel", label: "Funil Comercial", path: "/funil", icon: Filter },
    ],
  },
  {
    title: "Inteligência",
    items: [
      {
        key: "campaign_intel",
        label: "Inteligência de Campanhas",
        path: "/inteligencia",
        icon: Lightbulb,
      },
      { key: "creator", label: "Criador de Campanhas", path: "/criador", icon: Brush },
      { key: "creatives", label: "Criativos", path: "/criativos", icon: Image },
      { key: "knowledge", label: "Central de Inteligência", path: "/central", icon: BookOpen },
    ],
  },
  {
    title: "Sistema",
    items: [
      { key: "integrations", label: "Integrações", path: "/integracoes", icon: Plug },
      { key: "settings", label: "Configurações", path: "/configuracoes", icon: Settings },
    ],
  },
];

export const NAV_ITEMS = NAV_GROUPS.flatMap((g) => g.items);
