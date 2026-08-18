# NAIC EU — volledig pakket naar P:\Jules\Apps\NAIC (zonder Artifacts)

Eén script installeert **alles**: Python NAIC, Android-app, deploy, config, docs.

## Stappen

1. Sla **`install-to-p-drive-all-in-one.ps1`** op (uit deze Cursor-sessie).
2. PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
& "P:\Jules\Apps\NAIC\install-to-p-drive-all-in-one.ps1"
```

3. Controleer:

```powershell
dir P:\Jules\Apps\NAIC\naic_eu
dir P:\Jules\Apps\NAIC\naic-android
dir P:\Jules\Apps\NAIC\deploy
```

## Integriteit

| Check | Waarde |
|-------|--------|
| Base64 lengte | **390992** |
| SHA256 `.tgz` | `06af451957bf8e54d957829f9ce70ef42eaf5bd76332870da9fa03e66bb9ad6c` |

Het script controleert dit automatisch.

## Daarna

Zie **[LOCAL-FIRST.md](../LOCAL-FIRST.md)** — lokaal verder werken in Cursor Desktop op `P:\Jules\Apps\NAIC`.

## Alternatief: 8 losse parts

Als het grote script niet te kopiëren is, gebruik `part1.b64` t/m `part8.b64` + `install-to-p-drive.ps1`.
