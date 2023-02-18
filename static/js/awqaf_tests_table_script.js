const awqafTableSwitchStateBtn = document.getElementById('awqaf-table-switch-state-button');
const submitChangesAwqafBtn = document.getElementById('submit-changes-awqaf-btn');
const backAwqafBtn = document.getElementById('back-awqaf-btn');
const logCaseNoEdit = document.getElementById('log-case-no-edit');
const formCaseEdit = document.getElementById('form-case-edit');



awqafTableSwitchStateBtn.onclick = () => {
    awqafTableSwitchStateBtn.classList.add("d-none");
    submitChangesAwqafBtn.classList.remove("d-none");
    backAwqafBtn.classList.remove("d-none");
    logCaseNoEdit.classList.add("d-none");
    formCaseEdit.classList.remove("d-none");
}

submitChangesAwqafBtn.onclick = () => {
    formCaseEdit.children[0].submit();
}

backAwqafBtn.onclick = () => {
    location.reload();
}