const determingAddingComingForm = document.getElementById("determing-adding-coming-form");
const comingPointsInput = determingAddingComingForm.querySelector("#coming-points");
const submitComingButtons = document.querySelectorAll(".submit-coming-button");
const studentIdHiddenInput = document.getElementById("student-id-hidden-input");
const warningModelComing = document.getElementById("warning-model-coming");

if (localStorage.getItem("coming-points")) {
    comingPointsInput.value = localStorage.getItem("coming-points");
}

determingAddingComingForm.addEventListener("submit", (e) => {
    e.preventDefault();

    const determingAddingModel = document.querySelector(".model.active");

    const comingPoints = comingPointsInput.value;

    localStorage.setItem("coming-points", comingPoints);

    closeModel(determingAddingModel);
});

submitComingButtons.forEach(btn => {
    btn.addEventListener("click", () => {
        if (!comingPointsInput.value) {
            openModel(warningModelComing);
        } else {
            studentIdHiddenInput.value = btn.dataset.studentId;
            determingAddingComingForm.submit();
        }
    })
})