const form = document.querySelector("#releve-form");
const message = document.querySelector("#form-message");
const dateInput = document.querySelector("#date");

dateInput.value = new Date().toLocaleDateString("en-CA");

function cookie(name) {
  return document.cookie.split("; ").find(part => part.startsWith(name + "="))?.split("=")[1] || "";
}

form.addEventListener("submit", async event => {
  event.preventDefault();
  if (!form.reportValidity()) return;

  const data = Object.fromEntries(new FormData(form));
  const button = form.querySelector("button");
  button.disabled = true;
  message.classList.remove("error");
  message.textContent = "Enregistrement…";

  try {
    if (location.protocol === "file:") {
      const existing = JSON.parse(localStorage.getItem("tp1-releves") || "[]");
      existing.push(data);
      localStorage.setItem("tp1-releves", JSON.stringify(existing));
      message.textContent = "Relevé enregistré dans ce navigateur. Lancez Django pour l’ajouter au CSV.";
    } else {
      const response = await fetch("/api/prix", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": cookie("csrftoken") },
        body: JSON.stringify(data),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.erreur || "Impossible d’enregistrer le relevé.");
      message.textContent = result.message;
    }
    form.reset();
    dateInput.value = new Date().toLocaleDateString("en-CA");
  } catch (error) {
    message.classList.add("error");
    message.textContent = error.message || "Une erreur est survenue.";
  } finally {
    button.disabled = false;
  }
});

if (location.protocol !== "file:") {
  fetch("/api/population/TCD")
    .then(response => response.json().then(data => ({ ok: response.ok, data })))
    .then(({ ok, data }) => {
      if (!ok) throw new Error(data.erreur);
      document.querySelector("#population-value").textContent = new Intl.NumberFormat("fr-FR").format(data.population);
      document.querySelector("#population-year").textContent = `Habitants · données ${data.annee}`;
    })
    .catch(() => {
      document.querySelector("#population-value").textContent = "Indisponible";
      document.querySelector("#population-year").textContent = "Vérifiez votre connexion Internet.";
    });
} else {
  document.querySelector("#population-value").textContent = "Serveur requis";
  document.querySelector("#population-year").textContent = "Lancez Django pour charger cette donnée.";
}
