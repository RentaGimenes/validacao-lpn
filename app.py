<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Validação com Alerta Automático</title>
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
</head>
<body class="bg-slate-100 min-h-screen flex items-center justify-center p-4">

    <div class="bg-white p-6 rounded-xl shadow-md w-full max-w-md">
        <h1 class="text-xl font-bold text-slate-800 mb-4">Sistema de Validação</h1>
        
        <div class="space-y-4">
            <div>
                <label for="codigoInput" class="block text-sm font-medium text-slate-600 mb-1">Código de Barras / Leitor</label>
                <input type="text" id="codigoInput" placeholder="Aguardando leitura..." class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
            </div>

            <button id="validarBtn" class="w-full bg-blue-600 text-white font-medium py-2 rounded-lg hover:bg-blue-700 transition-colors cursor-pointer">
                Validar
            </button>
        </div>

        <div id="statusMsg" class="mt-4 text-sm font-medium text-center hidden"></div>
    </div>

    <!-- Elemento de áudio para o bip -->
    <audio id="beepAudio" src="https://freesound.org/data/previews/80/80921_1022651-lq.mp3" preload="auto"></audio>

    <script>
        const codigoInput = document.getElementById('codigoInput');
        const validarBtn = document.getElementById('validarBtn');
        const beepAudio = document.getElementById('beepAudio');
        const statusMsg = document.getElementById('statusMsg');

        let ultimoValorBipado = '';

        // Função para tocar o som de alerta (bip automático)
        function tocarBip() {
            beepAudio.currentTime = 0;
            beepAudio.play().catch(error => {
                console.log("Reprodução automática bloqueada pelo navegador até haver interação:", error);
            });
        }

        // Detecta quando o valor muda ou recebe entrada do leitor
        codigoInput.addEventListener('input', (e) => {
            const valorAtual = e.target.value.trim();
            
            // Toca o bip apenas se houver conteúdo novo e diferente do último bipado
            if (valorAtual.length > 0 && valorAtual !== ultimoValorBipado) {
                tocarBip();
                ultimoValorBipado = valorAtual;
            } else if (valorAtual.length === 0) {
                ultimoValorBipado = '';
            }
        });

        // Função que realiza a validação (somente por Enter ou Botão)
        function executarValidacao() {
            const codigo = codigoInput.value.trim();
            if (!codigo) return;

            statusMsg.classList.remove('hidden', 'text-red-600', 'text-green-600');
            
            // Exemplo de validação
            statusMsg.textContent = `Código "${codigo}" validado com sucesso!`;
            statusMsg.classList.add('text-green-600');

            // Limpa o campo e reseta o controle para permitir ler o mesmo código novamente se necessário
            codigoInput.value = '';
            ultimoValorBipado = '';
            codigoInput.focus();
        }

        // Aciona a validação ao apertar Enter
        codigoInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                executarValidacao();
            }
        });

        // Aciona a validação ao clicar no botão
        validarBtn.addEventListener('click', () => {
            executarValidacao();
        });

        // Foco inicial no input
        window.onload = () => codigoInput.focus();
    </script>

</body>
</html>
