// Aguarda o HTML carregar completamente antes de rodar
document.addEventListener('DOMContentLoaded', function() {
    const selectPerfil = document.querySelector('select[name="is_gestor"]');
    const divGestor = document.getElementById('div-gestor');
    const inputNomeGestor = document.getElementById('nome_gestor');
    
    // Só adiciona o evento se os elementos existirem na tela
    if (selectPerfil && divGestor) {
        selectPerfil.addEventListener('change', function() {
            if (this.value === 'false') {
                // É colaborador: mostra o campo
                divGestor.style.display = 'block';
            } else {
                // É gestor: esconde o campo e limpa o que foi digitado
                divGestor.style.display = 'none';
                if (inputNomeGestor) {
                    inputNomeGestor.value = "";
                }
            }
        });
    }
});