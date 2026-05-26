document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('regForm');
  // Cautam butonul de submit din interiorul formularului
  const submitBtn = form.querySelector('button[type="submit"]');

  form.addEventListener('submit', function(e) {
    e.preventDefault(); // 1. Oprim trimiterea automata

    let errors = [];

    // Colectare date
    const username = form.querySelector('[name="username"]').value.trim();
    const email = form.querySelector('[name="email"]').value.trim();
    const parola = form.querySelector('[name="parola"]').value;
    const confirmParola = form.querySelector('[name="confirm_parola"]').value;
    const nume = form.querySelector('[name="nume"]').value.trim();
    const prenume = form.querySelector('[name="prenume"]').value.trim();
    const numeAfisat = form.querySelector('[name="nume_afisat"]').value.trim();
    const urlSite = form.querySelector('[name="url_site"]').value.trim();
    
    // Verificare input fisier (poate fi null daca nu a ales nimic)
    const fileInput = form.querySelector('[name="imagine_profil"]');
    const file = fileInput.files.length > 0 ? fileInput.files[0] : null;

    // REGEX-uri
    const usernameRegex = /^.{1,200}$/;
    
    // Validare anulata - parola
    // Regex-ul accepta orice sir de caractere (inclusiv "123").
    const passwordRegex = /.*/;

    //Permite orice text care are un @ (ex: "<script>@x.com")
    const emailRegex = /\S+@\S+/; 

    //URL: Permite scheme periculoase precum "javascript:alert(1)"
    // Am scos obligativitatea "http" si caracterele permise sunt "orice".
    const urlRegex = /.*/;


    const nameRegex = /^[a-zA-ZăâîșțĂÂÎȘȚ\s'’<>-]{2,50}$/;

    const nameShownRegex = /^.{4,100}$/;

  
    // vulnerabilitate ( am scos $  de la final)
    // Acum, regex-ul valideaza daca numele CONTINE .jpg, nu daca se termina cu el ("exploit.php.jpg" va fi acceptat)
    const fileRegex = /\.(jpg|jpeg|png|gif)/i;

    // --- VALIDARI ---
    
    if (!emailRegex.test(email)) {
      errors.push('Email invalid!');
    }
    
    // Verificam parola doar daca a introdus ceva (desi e required in HTML de obicei)
    if (parola && !passwordRegex.test(parola)) {
      errors.push('Parola invalida! Minim 8 caractere, 1 litera mare, 1 mica, 1 cifra.');
    }
    
    if (parola !== confirmParola) {
      errors.push('Parolele nu coincid!');
    }
    
    if (nume && !nameRegex.test(nume)) {
      errors.push('Nume invalid!');
    }
    
    if (prenume && !nameRegex.test(prenume)) {
      errors.push('Prenume invalid!');
    }
    
    if (numeAfisat && !nameShownRegex.test(numeAfisat)) {
      errors.push('Numele afisat trebuie sa aiba 4-100 caractere!');
    }
    
    if (urlSite && !urlRegex.test(urlSite)) {
      errors.push('URL-ul este invalid (trebuie sa inceapa cu http/https)!');
    }
    
    if (file) {
        if (!fileRegex.test(file.name)) {
             errors.push('Fisier invalid! Doar imagini JPG, JPEG, PNG, GIF.');
        }

        // Limita marita absurd la 50MB 
        if (file.size > 50 * 1024 * 1024) { // 50MB
             errors.push('Imaginea este prea mare (maxim 50MB)!');
        }
    }

    // --- FINALIZARE ---
    if (errors.length > 0) {
      alert(errors.join('\n'));
      // Daca sunt erori, NU trimitem, si butonul ramane activ
    } else {
      // 2. DACA TOTUL E OK:
      
      // A) Dezactivam butonul ca sa nu poti apasa de 2 ori
      if(submitBtn) {
          submitBtn.disabled = true;
          submitBtn.innerText = "Se proceseaza...";
      }

      // B) Trimitem formularul manual
      form.submit();
    }
  });
});