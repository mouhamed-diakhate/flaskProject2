// Fonction pour envoyer la requête AJAX au serveur Django
function executePythonCode() {
    // Envoi de la requête AJAX au serveur Django
    $.ajax({
        url: '/execute-python-code/',
        type: 'POST',
        dataType: 'json',
        data: {
            csrfmiddlewaretoken: '{{ csrf_token }}',  // Si vous utilisez la protection CSRF
        },
        success: function(response) {
            // Afficher le résultat renvoyé par la vue Django
            $('#result').html(response.result);
        },
        error: function(xhr, status, error) {
            console.error('Erreur lors de l\'envoi de la requête AJAX :', error);
        }
    });
}

// Écouteur d'événement pour le lien "Macky Sall"
$('#macky-sall-link').click(function(event) {
    event.preventDefault();
    executePythonCode();
});
