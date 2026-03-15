# Steg-för-steg guide: Elpris Dashboard → Render

## Steg 1 — Testa lokalt

Öppna terminalen och installera beroenden:

```bash
pip install streamlit plotly pandas requests pytz
```

Starta appen:

```bash
streamlit run app.py
```

Appen öppnas automatiskt på http://localhost:8501
Tryck Ctrl+C i terminalen för att stänga.

Nå från telefonen (samma wifi-nätverk):
- Mac/Linux: kör `ifconfig | grep "inet "` → hitta t.ex. 192.168.1.42
- Windows: kör `ipconfig` → hitta "IPv4-adress"
- Öppna http://192.168.1.42:8501 i telefonens webbläsare


## Steg 2 — Lägg upp koden på GitHub

1. Gå till https://github.com och skapa ett konto (gratis)
2. Klicka på "New repository" (grön knapp uppe till höger)
3. Namnge det t.ex. `elpris-dashboard`
4. Välj "Public" (krävs för gratis Render)
5. Klicka "Create repository"

Ladda upp filerna:
6. Klicka "uploading an existing file" på den tomma repo-sidan
7. Dra in BÅDA filerna: `app.py` och `requirements.txt`
8. Klicka "Commit changes"


## Steg 3 — Deploya till Render

1. Gå till https://render.com och klicka "Get Started for Free"
2. Välj "Sign up with GitHub" → logga in med ditt GitHub-konto
3. Klicka "New +" → välj "Web Service"
4. Under "Connect a repository" → välj ditt `elpris-dashboard`-repo
5. Fyll i inställningarna:

   | Fält | Värde |
   |------|-------|
   | Name | elpris-dashboard (valfritt) |
   | Region | Frankfurt (EU Central) |
   | Branch | main |
   | Runtime | Python 3 |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `streamlit run app.py --server.port $PORT --server.address 0.0.0.0` |
   | Instance Type | **Free** |

6. Klicka "Create Web Service"
7. Vänta 2–3 minuter medan Render bygger appen
8. Du får en URL som ser ut som: https://elpris-dashboard-xxxx.onrender.com
   → Öppna den i webbläsaren eller telefonen!


## Steg 4 — Sätt upp Uptime Robot (förhindrar fördröjning)

Utan detta "somnar" appen efter 15 min och tar 30 sek att vakna.

1. Gå till https://uptimerobot.com → klicka "Register for FREE"
2. Verifiera din e-post
3. Klicka "Add New Monitor"
4. Välj:
   - Monitor Type: HTTP(s)
   - Friendly Name: Elpris Dashboard
   - URL: din Render-URL (t.ex. https://elpris-dashboard-xxxx.onrender.com)
   - Monitoring Interval: Every 5 minutes
5. Klicka "Create Monitor"

Nu pingar Uptime Robot din app var 5:e minut → appen är alltid vaken!


## Steg 5 — Uppdatera appen i framtiden

När du vill ändra koden:
1. Redigera `app.py` på din dator
2. Gå till ditt GitHub-repo → klicka på `app.py` → klickpikonen (penna) → klistra in ny kod → "Commit changes"
3. Render upptäcker ändringen automatiskt och bygger om appen (tar ~2 min)


## Felsökning

**Appen startar inte på Render:**
→ Kolla "Logs" i Render-dashboarden för felmeddelanden
→ Vanligaste orsaken: fel i Start Command — kontrollera att det är exakt rätt

**"No module named X":**
→ Kontrollera att modulen finns i requirements.txt

**Appen visar gammal data:**
→ Data cachas i 15 min — vänta eller klicka "Rerun" uppe till höger i Streamlit

**Morgondagens priser saknas:**
→ Elprisetjustnu publicerar morgondagens priser ca kl 13:00 — normalt beteende
