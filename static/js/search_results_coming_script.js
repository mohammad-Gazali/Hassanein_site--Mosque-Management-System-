const determingAddingComingForm = document.getElementById("determing-adding-coming-form");
const comingPointsInput = determingAddingComingForm.querySelector("#coming-points");
const comingCategoryInput = determingAddingComingForm.querySelector("#coming-category");
const submitComingButtons = document.querySelectorAll(".submit-coming-button");
const studentIdHiddenInput = document.getElementById("student-id-hidden-input");
const warningModelComing = document.getElementById("warning-model-coming");

if (localStorage.getItem("coming-points")) {
    comingPointsInput.value = localStorage.getItem("coming-points");
}

if (localStorage.getItem("coming-category")) {
    comingCategoryInput.value = localStorage.getItem("coming-category");
}

determingAddingComingForm.addEventListener("submit", (e) => {
    e.preventDefault();

    const determingAddingModel = document.querySelector(".model.active");

    const comingPoints = comingPointsInput.value;
    const comingCategory = comingCategoryInput.value;

    localStorage.setItem("coming-points", comingPoints);
    localStorage.setItem("coming-category", comingCategory);

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