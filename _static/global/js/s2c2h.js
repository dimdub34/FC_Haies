function fill_payment_form() {
    const devis_id = `${js_vars.devis_id}`;
    const subject_id = `${js_vars.subject_id}`;
    const amount = `${js_vars.subject_payoff}`;

    console.log(devis_id, subject_id, amount);
    const domain = 'https://s2ch-gestion.huma-num.fr'

    fetch(domain, {
            method: 'POST',
            headers: {
                'X-Devis-Id': devis_id,
                'X-Subject-Id': subject_id,
                'X-Amount': amount
            }
        }
    ).then(
        response => response.text()
    ).then(
        text => {
            window.location.href = domain + '/' + text
        }
    ).catch(error => {
        console.log(error)
    });
}
