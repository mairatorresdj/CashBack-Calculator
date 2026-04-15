const API_URL = ""; // depois troca no deploy

const form = document.getElementById("formulario_cashback"); 
const resultado = document.getElementById("resultado"); 
const historico = document.getElementById("historico");

// carrega o histórico quando abro a página
form.addEventListener("submit", async (envio) => {
    envio.preventDefault(); // 🚨 impede reload

    const valor = document.getElementById("valor").value;
    const cupom = document.getElementById("cupom").value;

    const vip = document.querySelector('input[name="vip"]:checked')?.value;

    try {
        // POST → calcular
        const response = await fetch(`${API_URL}/`, {
        method: "POST",
        headers: {
        "Content-Type": "application/json"
            },
            body: JSON.stringify({ valor, vip, cupom })
        });

            if (!response.ok) {
                const errorData = await response.json();
                resultado.innerText = errorData.erro || "Erro ao calcular";
                return;
            }

            const data = await response.json();
            resultado.innerText = `Cashback: R$ ${data.cashback}`;

        //  atualiza meu historico
        carregarHistorico();

    } catch (error) {
        resultado.innerText = "Erro ao calcular.";
    }
});


// GET no histórico
async function carregarHistorico() {
    try {
        const response = await fetch(`${API_URL}/`);
        const data = await response.json();

        console.log("HISTORICO:", data);

        const historico = document.getElementById("historico"); // 👈 pega aqui dentro
        historico.innerHTML = "";

        data.forEach(item => {
            const li = document.createElement("li");

            li.innerHTML = `
                <strong>Valor:</strong> R$ ${item.valor} <br>
                <strong>VIP:</strong> ${item.tipo_cliente} <br>
                <strong>Cashback:</strong> R$ ${item.cashback}
            `;

            historico.appendChild(li);
        });

    } catch (error) {
        console.log("Erro ao carregar histórico", error);
    }
}