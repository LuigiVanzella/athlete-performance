const form = document.getElementById("formLogin");
const mensagem = document.getElementById("mensagem");
const botao = document.getElementById("botao");

form.addEventListener("submit", async (evento) => {
  evento.preventDefault();

  mensagem.textContent = "";
  botao.disabled = true;
  botao.textContent = "Entrando...";

  try {
    const email = document.getElementById("email").value;
    const senha = document.getElementById("senha").value;

    const resposta = await fetch("/api/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, senha }),
    });

    if (!resposta.ok) {
      throw new Error("E-mail ou senha inválidos.");
    }

    const dados = await resposta.json();

    mensagem.style.color = "#86efac";
    mensagem.textContent = "Login realizado com sucesso!";

    // A navegação será adicionada após
    // configurarmos a sessão autenticada.
  } catch (erro) {
    mensagem.style.color = "#fca5a5";
    mensagem.textContent = erro.message;
  } finally {
    botao.disabled = false;
    botao.textContent = "Entrar";
  }
});
