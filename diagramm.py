import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Streamlit App Titel
st.title("Break-Even Analyse Ticketing/AnmeldePlattform (4 Jahre)")

# Eingabe der Variablen mit Sliders
stundenlohn = st.slider("Stundenlohn (€ pro Stunde)", 10, 50, 23)
entwicklung_stunden = st.slider("Entwicklungsstunden", 50, 200, 100)
wartung_erstes_jahr = st.slider("Wartungsstunden (Monat 1-6)", 10, 50, 25)
wartung_zweites_halbjahr = st.slider("Wartungsstunden (Monat 7-12)", 5, 30, 15)
wartung_ab_jahr_2 = st.slider("Wartungsstunden (ab Jahr 2)", 1, 20, 5)
vertrieb_stunden_pro_monat = st.slider("Vertriebsstunden pro Monat", 5, 50, 20)
ticket_preis = st.slider("Durchschnittlicher Ticketpreis (€)", 5, 50, 15)
gebuehr_prozent = st.slider("Ticketgebühr (%)", 1, 10, 4) / 100
gebuehr_fest = st.slider("Feste Gebühr pro Ticket (€)", 0.0, 5.0, 0.5, step=0.1)

# Checkbox zur Aktivierung/Deaktivierung von Stripe-Gebühren
stripe_aktiv = st.checkbox("Stripe-Gebühren berücksichtigen?", value=False)

# Stripe-Gebühren
stripe_gebuehr_prozent = 0.012  # 1.2% = 0.012
stripe_gebuehr_fest = 0.25  # 0.25€ pro Transaktion

# Ticket-Verkaufsprognose für 4 Jahre
tickets_jahr_1 = st.slider("Tickets pro Monat (Jahr 1)", 100, 2000, 500)
tickets_jahr_2 = st.slider("Tickets pro Monat (Jahr 2)", 500, 3000, 1000)
tickets_jahr_3 = st.slider("Tickets pro Monat (Jahr 3)", 1000, 5000, 1500)
tickets_jahr_4 = st.slider("Tickets pro Monat (Jahr 4)", 1500, 7000, 2000)

# Berechnungen
entwicklungskosten = entwicklung_stunden * stundenlohn
wartung_monate = [wartung_erstes_jahr] * 6 + [wartung_zweites_halbjahr] * 6
wartungskosten_erstes_jahr = sum(wartung_monate) * stundenlohn
wartungskosten_ab_jahr_2 = wartung_ab_jahr_2 * stundenlohn * 12
vertriebskosten_pro_jahr = vertrieb_stunden_pro_monat * stundenlohn * 12

# Einnahmen pro Ticket berechnen
if stripe_aktiv:
    stripe_kosten = ticket_preis * stripe_gebuehr_prozent + stripe_gebuehr_fest
else:
    stripe_kosten = 0.0

einnahmen_pro_ticket = ticket_preis * gebuehr_prozent + gebuehr_fest - stripe_kosten

# Ticketverkaufsprognose für 4 Jahre (48 Monate)
monate = np.arange(1, 49)  # 4 Jahre (48 Monate)
tickets_pro_monat = np.concatenate([
    np.full(12, tickets_jahr_1), 
    np.full(12, tickets_jahr_2), 
    np.full(12, tickets_jahr_3), 
    np.full(12, tickets_jahr_4)
])

# Berechnung der monatlichen Kosten für 4 Jahre
kosten_pro_monat = []
for i in range(48):
    if i < 12:
        wartungskosten = wartung_monate[i % 12] * stundenlohn
    else:
        wartungskosten = wartungskosten_ab_jahr_2 / 12  # Ab Jahr 2 konstante Wartungskosten
    
    kosten_pro_monat.append(wartungskosten + vertriebskosten_pro_jahr / 12)

# Berechnung der kumulierten Einnahmen und Kosten
einnahmen_kumuliert = np.cumsum(tickets_pro_monat * einnahmen_pro_ticket)
kosten_kumuliert = np.cumsum([entwicklungskosten] + kosten_pro_monat[:-1])

# Break-even Punkt berechnen (erstes Mal, wenn Einnahmen die Kosten überschreiten)
break_even_index = np.where(einnahmen_kumuliert >= kosten_kumuliert)[0]

if len(break_even_index) > 0:
    break_even_monat = break_even_index[0] + 1
else:
    break_even_monat = None  # Kein Break-Even innerhalb von 48 Monaten

# Diagramm erstellen
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(monate, einnahmen_kumuliert, label="Kumulierte Einnahmen", linewidth=2)
ax.plot(monate, kosten_kumuliert, label="Kumulierte Kosten", linewidth=2)

if break_even_monat is not None:
    ax.axvline(break_even_monat, color='r', linestyle="--", label=f"Break-Even Monat {break_even_monat}")

ax.set_xlabel("Monate")
ax.set_ylabel("€")
ax.set_title("Break-Even-Analyse über 4 Jahre")
ax.legend()
ax.grid(True)

# Diagramm in Streamlit anzeigen
st.pyplot(fig)

# Break-even-Punkt anzeigen
if break_even_monat:
    st.write(f"✅ **Break-Even Punkt wird im Monat {break_even_monat} erreicht.**")
else:
    st.write("⚠️ **Break-Even wird in den ersten 48 Monaten nicht erreicht!**")

# Anzeige der Gebührenberechnung
if stripe_aktiv:
    st.write(f"**Stripe-Gebühren sind aktiviert.**")
    st.write(f"**Stripe Gebühren pro Ticket: €{stripe_kosten:.2f}**")
else:
    st.write("❌ **Stripe-Gebühren sind deaktiviert.**")

st.write(f"**Einnahmen nach Abzug der Gebühren pro Ticket: €{einnahmen_pro_ticket:.2f}**")
