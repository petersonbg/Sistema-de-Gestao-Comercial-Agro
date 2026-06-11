document.addEventListener("DOMContentLoaded", () => {
  const categoria = document.getElementById("id_categoria");
  const chassi = document.getElementById("id_chassi");
  const container = document.getElementById("chassi-field");

  if (!categoria || !chassi || !container) return;

  const categoriasVeiculos = new Set(
    (categoria.dataset.categoriasVeiculos || "")
      .split(",")
      .filter(Boolean)
  );

  const atualizarChassi = () => {
    const veiculo = categoriasVeiculos.has(categoria.value);
    chassi.disabled = !veiculo;
    container.classList.toggle("opacity-50", !veiculo);
    if (!veiculo) chassi.value = "";
  };

  categoria.addEventListener("change", atualizarChassi);
  atualizarChassi();
});
