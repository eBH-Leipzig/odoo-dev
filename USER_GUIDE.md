# Benutzerhandbuch: Lokale Odoo-Entwicklungsumgebung

Dieses Handbuch richtet sich an alle Teammitglieder und Einsteiger (auch ohne tiefere Programmierkenntnisse), die neue Funktionen und Module in Odoo vor der offiziellen Freigabe auf dem eigenen Computer testen möchten.

---

## 1. Was ist die lokale Testumgebung?
Mit der lokalen Umgebung läuft eine vollständige Odoo-Instanz inklusive Datenbank direkt auf deinem Rechner ("localhost").
- **Vorteil:** Du kannst neue Funktionen, Eingabemasken, Werkstattformulare oder Leasing-Optionen live im Browser ausprobieren, **bevor** sie auf den echten Server (Hostinger VPS) übertragen werden.
- **Sicherheit:** Hier kann nichts kaputtgehen – es handelt sich um eine isolierte Testdatenbank.
- **Echtzeit-Aktualisierung (Hot-Reload):** Code- und Ansichtsänderungen in `custom_addons/` werden automatisch geladen.

---

## 2. Voraussetzungen
1. **Docker Desktop** muss auf deinem PC installiert und gestartet sein (das kleine Wal-Symbol in der Taskleiste sollte aktiv sein).
2. Die Konfigurationsdatei `.env` muss im Projektverzeichnis vorhanden sein (falls nicht vorhanden, erstelle eine Kopie von `.env.example` und benenne sie in `.env` um).

---

## 3. Odoo lokal starten

Öffne ein Terminal (z. B. in VS Code mit `Strg + ö` oder über das Menü `Terminal > Neues Terminal`) und gib folgenden Befehl ein:

```bash
docker compose up -d
```

- Das `-d` bedeutet "im Hintergrund" (detached).
- Beim ersten Mal lädt Docker die benötigten Pakete herunter – das kann wenige Minuten dauern.
- Sobald `Started` bzw. `Running` erscheint, sind die beiden Dienste bereit:
  - `odoo-web-dev` (Odoo Webserver)
  - `odoo-db-dev` (PostgreSQL Datenbank)

---

## 4. Odoo im Browser öffnen & Änderungen testen

1. Öffne deinen Webbrowser (z. B. Chrome, Firefox oder Edge).
2. Rufe folgende Adresse auf:
   ```
   http://localhost:8069
   ```
3. Melde dich an (Standard-Benutzer je nach initialer Datenbankeinrichtung bzw. Einrichtungsassistent von Odoo).

### Änderungen und neue Module begutachten:
- **Bestehende Ansichten angepasst?** 
  Lade die Seite im Browser einfach mit `F5` oder `Strg + R` neu. Dank des integrierten Entwicklermodus werden XML- und Designanpassungen sofort angezeigt.
- **Neues Modul hinzugefügt?**
  1. Gehe im Hauptmenü auf **Apps**.
  2. Entferne den Suchfilter "Apps" in der Suchleiste, um alle Module zu sehen.
  3. Klicke auf **App-Liste aktualisieren** (im Entwicklermodus) oder suche direkt nach dem Modulnamen.
  4. Klicke bei dem entsprechenden Modul auf **Installieren** bzw. **Aktualisieren**.
  5. Teste die neue Maske, Felder oder Berechnungen.

---

## 5. Tests im Container ausführen (Qualitätskontrolle)

Möchtest du prüfen, ob alle automatisierten Tests für ein Modul erfolgreich durchlaufen, führe im Terminal einfach diesen Befehl aus (ersetze `<modul_name>` durch den Ordnernamen in `custom_addons/`):

```bash
docker compose exec web odoo -d postgres --test-enable --stop-after-init -i <modul_name>
```

Wenn am Ende `All tests passed` steht, ist alles fehlerfrei.

---

## 6. Odoo wieder beenden

Wenn du mit dem Testen fertig bist und Ressourcen auf deinem Rechner freigeben möchtest:

```bash
docker compose down
```

Deine Testdaten bleiben in den Docker-Volumes (`odoo-web-data` und `odoo-db-data`) sicher gespeichert und stehen beim nächsten Start mit `docker compose up -d` wieder zur Verfügung.

---

## 7. Schnelle Hilfe bei Problemen (FAQ)

- **Problem:** Die Webseite `http://localhost:8069` kann nicht erreicht werden.
  - **Lösung:** Prüfe, ob Docker Desktop läuft. Überprüfe die Logs im Terminal mit:
    ```bash
    docker compose logs web
    ```
- **Problem:** Änderungen an einem Python-Modell werden nicht sichtbar.
  - **Lösung:** Aktualisiere das Modul unter **Apps > [Modulname] > Aktualisieren** oder starte den Container kurz neu mit:
    ```bash
    docker compose restart web
    ```
