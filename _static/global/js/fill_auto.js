
function fill_auto(with_submit=true){
    // Dropdown menus
    let the_selects = document.querySelectorAll("select");
    for (let the_sel of the_selects) {
        let nb_options = the_sel.options.length;
        let choix_option = Math.floor(Math.random() * (nb_options - 1) + 1);
        the_sel.value = the_sel.options[choix_option].value;
        the_sel.dispatchEvent(new Event("change"));
    }

    // Numbers
    let the_input_numbers = document.querySelectorAll("input[type=number]");
    for (let the_num of the_input_numbers) {
        let the_min = Number(the_num.min);
        let the_max = Number(the_num.max);
        the_num.value = Math.floor(Math.random() * (the_max - the_min + 1) + the_min);
        the_num.dispatchEvent(new Event("input"));
    }

    // Radio buttons
    let myradios = document.querySelectorAll("input[type=radio]");
    let radio_names = [];
    for (let r of myradios) {
        if (!radio_names.includes(r.name))
            radio_names.push(r.name)
    }
    for (let r of radio_names) {
        let radios = document.querySelectorAll(`input[name=${r}]`);
        let selected = Math.floor(Math.random() * radios.length);
        radios[selected].click();
    }

    // checkbox
    let the_checkboxes = document.querySelectorAll("input[type=checkbox]");
    for (let check of the_checkboxes) {
        if (Math.random() > 0.5)
            check.click();
    }

    // slider
    let the_ranges = document.querySelectorAll("input[type=range]");
    for (let r of the_ranges) {
        if (r.disabled === false) {
            let the_min = Number(r.min);
            let the_max = Number(r.max);
            r.value = Math.floor(Math.random() * (the_max - the_min + 1) + the_min);
            r.dispatchEvent(new Event("input"));
        }
    }

    // string fields
    let the_texts = document.querySelectorAll("input[type=text]");
    for (let t of the_texts) {
        t.innerText = "message automatique";
        t.dispatchEvent(new Event("change"));
    }

    // long string field
    let the_long_area = document.querySelectorAll("textarea");
    for (let a of the_long_area) {
        a.innerText = "message automatique";
        a.dispatchEvent(new Event("change"));
    }

    if (with_submit) {
        setTimeout(function () {
            if (document.querySelector(".otree-btn-next") !== null)
                document.querySelector(".otree-btn-next").click();
            else
                document.querySelector("form").submit();
        }, 2000);
    }
}
