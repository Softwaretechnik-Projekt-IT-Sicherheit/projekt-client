# 📋 Wichtige Hinweise zur Arbeit

## 🎫 Features benötigen ein definiertes Ticket

Nutzt bitte das **Kanban Board** und verschiebt die Tickets nach ihrem Status.

Wenn ihr eine Feature-Branch erstellt, nutzt bitte einen Hinweis auf das Ticket, damit derjenige, der die Abnahme macht, weiß, was in diesem Ticket gefordert wird.

> [!NOTE]
> Hierfür bitte **fortlaufende Nummern** bei den Tickets nutzen, wie `T0001 - Name des Features`.

Bei den [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) am besten gleich das Ticket als Referenz hinter dem Typ angeben, beispielsweise:

```
feat(T0001): added multi-factor-auth
```

---

## 🌿 Neue Feature-Branch erstellen

Der Workflow zum Wechseln in die neue Feature-Branch sieht dann wie folgt aus:

```bash
git checkout develop                              # Wechseln in die Source-Branch develop
git pull origin develop                           # Neuesten Stand von develop pullen
git checkout -b feature/T0001-name-des-features   # Erstellen der neuen Branch
npm run setup                                     # Dependencies auf den neuesten Stand bringen
```

---

## 💻 Entwicklung

Entwickelt wird immer **lokal** und die Änderungen werden dann in eure Feature-Branch (GitFlow Workflow) gepusht.

- Denkt hierbei immer an die [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).
- Neue Funktionen bekommen passende Tests im Ordner `tests/`.

> [!IMPORTANT]
> **Immer nur ein Ticket pro Branch!**

---

## ✅ Vor dem PR: Code prüfen

Bevor ihr einen PR eröffnet, führt bitte lokal alle Prüfungen aus:

```bash
npm run check        # alle Prüfungen wie in der CI
npm run check:fix    # Format- und Lintfehler automatisch beheben
```

Erst wenn hier **„✅ Alle Prüfungen bestanden.“** erscheint, wird der PR eröffnet.

---

## 🔀 Pull Request (PR)

Wenn ihr der Meinung seid, das Feature ist fertig, eröffnet ihr über die Weboberfläche einen PR.

> [!IMPORTANT]
> **Ein PR hat als Base immer `develop` und als Vergleich eure Feature-Branch!**

Außerdem habt ihr nach der Erstellung auf der rechten Seite die Möglichkeit, einen **Assignee** auszuwählen. Dieser prüft den Code über die Oberfläche bitte noch einmal und gibt sein **Approve**, wenn der Code keine sichtbaren Fehler hat. So können wir uns Fehler auf dem laufenden Develop sparen!

### Der PR

Der PR-Titel folgt ebenfalls dem Conventional-Commit-Schema:

```
feat(T0001): my new feature description
```

### Automatische Prüfungen

Nach dem Erstellen laufen im PR automatisch die GitHub Actions (Commit-Lint, Code-Qualität und Tests auf allen drei Betriebssystemen). Ihr seht den Status unten im PR.

> [!WARNING]
> Ist eine Prüfung **rot**, wird nicht gemergt. Fehler in eurer Feature-Branch beheben und erneut pushen – die Prüfungen laufen dann automatisch neu.

> [!CAUTION]
> Wichtig, nochmal erwähnt, ist der Review – **NICHT EINFACH MERGEN!**

---

## 🚀 Release erstellen

```bash
git checkout develop
git pull origin develop
git checkout -b release/1.0.0

npm run check        # vor dem Release alles prüfen

git commit -am "chore(release): bump version to 1.0.0"
git push -u origin release/1.0.0
```

1. Öffne danach auf GitHub einen PR von `release/1.0.0` nach `main`.
2. Nach dem Merge in `main` erstellt ihr auf GitHub unter **Releases → Draft a new release** einen Tag `v1.0.0` auf `main`.
3. Danach `release/1.0.0` bzw. `main` wieder zurück nach `develop` mergen – das heißt neuer PR mit Base `develop` und Vergleich `release/1.0.0`.

> [!WARNING]
> **Schritt 3 unbedingt durchführen**, damit wir auf unserer Entwicklungsbranch nicht hinterherhängen!

> [!TIP]
> Die Versionsnummer steht in der `pyproject.toml` unter `version`. Vor dem Commit dort anpassen oder `uv version 1.0.0` ausführen.