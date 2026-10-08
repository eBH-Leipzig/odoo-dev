# eBike-Haus Leipzig (eBH) - Odoo WaWi Development

Entwicklungsumgebung und Custom-Module für das Warenwirtschafts- und Kassensystem des eBike-Haus Leipzig auf Basis von Odoo 19 Community Edition.

## 🚀 Schnellstart & Lokale Entwicklung

Die lokale Entwicklungsumgebung läuft über Docker Compose mit Live-Reloading für alle Module in `custom_addons/`.

1. **Umgebungsvariablen einrichten:**
   ```bash
   cp .env.example .env
   ```
2. **Entwicklungsumgebung starten:**
   ```bash
   docker compose up -d
   ```
3. **Im Browser öffnen:**
   [http://localhost:8069](http://localhost:8069)

## 📖 Dokumentation

- **[Benutzerhandbuch (USER_GUIDE.md)](USER_GUIDE.md):** Leicht verständliche Schritt-für-Schritt-Anleitung für nicht-technische Nutzer (Container starten, Änderungen auf localhost live begutachten, Module aktualisieren).
- **[Entwickler-Richtlinien (CLAUDE.md)](CLAUDE.md):** OCA-Standards, Modul-Architektur, Testanforderungen und Docker-Befehle für Entwickler.
- **[Projekt-Regeln (.zoorules)](.zoorules):** Konventionen, Odoo-Core-Referenzen und Agenten-Workflow.

