const editSpecializationsBtn = document.getElementById('edit-specializations-btn');
const submitChangesSpecializationsBtn = document.getElementById('submit-changes-specializations-btn');
const backSpecializationsBtn = document.getElementById('back-specializations-btn');
const displayTypeSpecializationsBtn = document.getElementById('display-type-specializations-btn')
const mainTbodyAdminSpecializations = document.getElementById('main-tbody-admin-specializations');
const formTbodyAdminSpecializations = document.getElementById('form-tbody-admin-specializations');
const changesFormSSpecializations = document.querySelector('#form-tbody-admin-specializations form');
const mainTableSpecializations = document.getElementById('main-table-specializations');
const logTableSpecializations = document.getElementById('log-table-specializations');
const basicBtnsSpecializations = document.getElementById('basic-buttons-specializations');
const specializationsFilteringBtns = document.querySelectorAll('[data-sp]');
const filteringCells = document.querySelectorAll('[data-sp-item]');
const buttonsFiltersBar = document.getElementById('buttons-filters-bar');



editSpecializationsBtn.onclick = () => {
    mainTbodyAdminSpecializations.classList.add("d-none");

    formTbodyAdminSpecializations.classList.remove("d-none");
    submitChangesSpecializationsBtn.classList.remove("d-none");
    backSpecializationsBtn.classList.remove("d-none");

    editSpecializationsBtn.classList.add("d-none");
}


submitChangesSpecializationsBtn.onclick = () => {
    changesFormSSpecializations.submit();
}


backSpecializationsBtn.onclick = () => {
    location.reload();
}


displayTypeSpecializationsBtn.onclick = () => {
    if (displayTypeSpecializationsBtn.dataset.type === "main") {
        mainTableSpecializations.classList.add("d-none");
        logTableSpecializations.classList.remove("d-none");
        basicBtnsSpecializations.classList.add("d-none");
        buttonsFiltersBar.classList.add("d-none");

        displayTypeSpecializationsBtn.innerHTML = 'عرض معلومات الاختصاصات <i class="bi bi-clipboard2-data"></i>';
        displayTypeSpecializationsBtn.classList.remove('btn-dark')
        displayTypeSpecializationsBtn.classList.add('btn-primary')
        displayTypeSpecializationsBtn.dataset.type = "log";
    } else {
        mainTableSpecializations.classList.remove("d-none");
        logTableSpecializations.classList.add("d-none");
        basicBtnsSpecializations.classList.remove("d-none");
        buttonsFiltersBar.classList.remove("d-none");


        displayTypeSpecializationsBtn.classList.add('btn-dark')
        displayTypeSpecializationsBtn.classList.remove('btn-primary')
        displayTypeSpecializationsBtn.innerHTML = 'عرض السجل لتسجيل الاختصاص <i class="bi bi-journal-bookmark-fill"></i>';
        displayTypeSpecializationsBtn.dataset.type = "main";
    }
}


specializationsFilteringBtns.forEach(btn => {
    btn.onclick = () => {

        specializationsFilteringBtns.forEach(b => {
            b.classList.remove("btn-primary");
            b.classList.add("btn-success");
        })
        
        btn.classList.remove("btn-success");
        btn.classList.add("btn-primary");

        if (btn.dataset.sp === "-1") {
            filteringCells.forEach(cell => {
                cell.classList.remove("d-none");
            })
        } else {
            filteringCells.forEach(cell => {
                if (cell.dataset.spItem == btn.dataset.sp) {
                    cell.classList.remove("d-none");
                } else {
                    cell.classList.add("d-none");
                }
            })
        }
    }
})