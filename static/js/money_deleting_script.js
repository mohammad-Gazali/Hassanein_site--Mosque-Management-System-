const moneyDeletingTypeMoney = document.getElementById('money-deleting-type-money');
const moneyDeletingTypeMoney2 = document.getElementById('money-deleting-type-money-2');
const moneyDeletingTypePoints = document.getElementById('money-deleting-type-points');
const moneyDeletingTypePoints2 = document.getElementById('money-deleting-type-points-2');
const moneyDeletingFirstGroup = document.getElementById('money-deleting-first-group');
const moneyDeletingFirstGroup2 = document.getElementById('money-deleting-first-group-2');
const moneyDeletingSecondGroup = document.getElementById('money-deleting-second-group');
const moneyDeletingSecondGroup2 = document.getElementById('money-deleting-second-group-2');
const moneyDeletingStudentForm = document.getElementById('money-deleting-student-form');
const moneyDeletingMainForm = document.getElementById('money-deleting-main-form');
const moneyDeletingDisplayingStudents = document.getElementById('money-deleting-displaying-students');
const moneyDeletingDisplayingStudentsFormBody = document.getElementById('money-deleting-displaying-students-form-body');
const moneyDeletingHiddenInput = document.getElementById('money-deleting-hidden-input');
const moneyDeletingErrorNotStudentChoosed = document.getElementById('money-deleting-error-not-student-choosed');
const csrfToken = document.querySelector('#money-deleting-student-form input[name="csrfmiddlewaretoken"]');
const typeOfDeletingOneStudent = document.getElementById('type-of-deleting-one-student');
const typeOfDeletingCategory = document.getElementById('type-of-deleting-category');
const firstSectionForDisplayWithTypeOfDeleting = document.getElementById('first-section-for-display-with-type-of-deleting');
const secondSectionForDisplayWithTypeOfDeleting = document.getElementById('second-section-for-display-with-type-of-deleting');



/* Handling the Target of Money Deleting (One Student [or] Category) */

typeOfDeletingOneStudent.onchange = () => {
    if (typeOfDeletingOneStudent.checked) {
        firstSectionForDisplayWithTypeOfDeleting.classList.remove("d-none");
        secondSectionForDisplayWithTypeOfDeleting.classList.add("d-none");
    } else {
        firstSectionForDisplayWithTypeOfDeleting.classList.add("d-none");
        secondSectionForDisplayWithTypeOfDeleting.classList.remove("d-none");
    }
}

typeOfDeletingCategory.onchange = () => {
    if (typeOfDeletingOneStudent.checked) {
        firstSectionForDisplayWithTypeOfDeleting.classList.remove("d-none");
        secondSectionForDisplayWithTypeOfDeleting.classList.add("d-none");
    } else {
        firstSectionForDisplayWithTypeOfDeleting.classList.add("d-none");
        secondSectionForDisplayWithTypeOfDeleting.classList.remove("d-none");
    }
}



/* Handle Choosing the Type of Money Deleting */

/* First Form */
moneyDeletingTypeMoney.onchange = () => {
    if (moneyDeletingTypeMoney.checked) {
        moneyDeletingFirstGroup.classList.remove("d-none");
        moneyDeletingSecondGroup.classList.add("d-none");
        
        moneyDeletingFirstGroup.children[1].required = true;
        moneyDeletingSecondGroup.children[1].required = false;
    } else {
        moneyDeletingFirstGroup.classList.add("d-none");
        moneyDeletingSecondGroup.classList.remove("d-none");

        moneyDeletingFirstGroup.children[1].required = false;
        moneyDeletingSecondGroup.children[1].required = true;
    }
}

moneyDeletingTypePoints.onchange = () => {
    if (moneyDeletingTypeMoney.checked) {
        moneyDeletingFirstGroup.classList.remove("d-none");
        moneyDeletingSecondGroup.classList.add("d-none");
        
        moneyDeletingFirstGroup.children[1].required = true;
        moneyDeletingSecondGroup.children[1].required = false;
    } else {
        moneyDeletingFirstGroup.classList.add("d-none");
        moneyDeletingSecondGroup.classList.remove("d-none");

        moneyDeletingFirstGroup.children[1].required = false;
        moneyDeletingSecondGroup.children[1].required = true;
    }
}

/* Second Form */
moneyDeletingTypeMoney2.onchange = () => {
    if (moneyDeletingTypeMoney2.checked) {
        moneyDeletingFirstGroup2.classList.remove("d-none");
        moneyDeletingSecondGroup2.classList.add("d-none");
        
        moneyDeletingFirstGroup2.children[1].required = true;
        moneyDeletingSecondGroup2.children[1].required = false;
    } else {
        moneyDeletingFirstGroup2.classList.add("d-none");
        moneyDeletingSecondGroup2.classList.remove("d-none");

        moneyDeletingFirstGroup2.children[1].required = false;
        moneyDeletingSecondGroup2.children[1].required = true;
    }
}

moneyDeletingTypePoints2.onchange = () => {
    if (moneyDeletingTypeMoney2.checked) {
        moneyDeletingFirstGroup2.classList.remove("d-none");
        moneyDeletingSecondGroup2.classList.add("d-none");
        
        moneyDeletingFirstGroup2.children[1].required = true;
        moneyDeletingSecondGroup2.children[1].required = false;
    } else {
        moneyDeletingFirstGroup2.classList.add("d-none");
        moneyDeletingSecondGroup2.classList.remove("d-none");

        moneyDeletingFirstGroup2.children[1].required = false;
        moneyDeletingSecondGroup2.children[1].required = true;
    }
}



/* Search Student */

moneyDeletingStudentForm.onsubmit = async (e) => {

    e.preventDefault();

    const inputValue = e.target.children[4].value

    const response = await fetch('/json/students', {
        method: "POST",
        mode: 'same-origin',
        headers: {
            "Content-Type":"application/json",
            "X-CSRFToken": csrfToken.value
        },
        body: JSON.stringify({
            "content": inputValue
        })
    });

    const data = await response.json();

    moneyDeletingDisplayingStudents.innerHTML = '';

    if (data.students.length === 0) {

        const newError = document.createElement('div')
        const textError = document.createTextNode('لا يوجد طالب بهذا الاسم')
        
        newError.appendChild(textError)
        newError.className = 'alert alert-danger'

        moneyDeletingDisplayingStudents.appendChild(newError)

    } else {
        Array.from(data.students).forEach((student) => {
            const newDiv = document.createElement('div')
            const innerButton = document.createElement('button')
            
            const textDiv = document.createTextNode(`[${student.id}] ${student.name}`)
            const textButton = document.createTextNode('اختيار')
    
            innerButton.appendChild(textButton)
            innerButton.className = 'btn btn-primary'
            innerButton.dataset.id = student.id
            innerButton.dataset.name = student.name

            newDiv.appendChild(textDiv)
            newDiv.appendChild(innerButton)
            newDiv.className = 'alert alert-primary flex-wrap d-flex gap-3 align-items-center justify-content-between'
            newDiv.id = `student-in-edit-points-form-id-${student.id}`
            newDiv.role = 'alert'

            moneyDeletingDisplayingStudents.appendChild(newDiv)
        })

        Array.from(moneyDeletingDisplayingStudents.children).forEach((div) => {
            const btn = div.children[0]

            btn.onclick = (e) => {
                moneyDeletingDisplayingStudentsFormBody.className = ''
                moneyDeletingDisplayingStudentsFormBody.innerHTML = ''

                const stuId = e.target.dataset.id;
                const stuName = e.target.dataset.name;

                const xIcon = document.createElement('i')
                xIcon.className = 'bi bi-x-lg'
                xIcon.style.cursor = 'pointer'

                const textContent = document.createTextNode(`[${stuId}] ${stuName}`)

                moneyDeletingHiddenInput.value = stuId;

                moneyDeletingDisplayingStudentsFormBody.className = 'alert alert-primary d-flex justify-content-between align-items-center'
                moneyDeletingDisplayingStudentsFormBody.appendChild(textContent);
                moneyDeletingDisplayingStudentsFormBody.appendChild(xIcon)

                xIcon.onclick = () => {
                    moneyDeletingHiddenInput.value = ''
                    moneyDeletingDisplayingStudentsFormBody.className = ''
                    moneyDeletingDisplayingStudentsFormBody.innerHTML = ''
                }
            }
        }) 
    }           
}


// error no student choosed in the main form
moneyDeletingMainForm.onsubmit = (e) => {
    e.preventDefault();
    if (!moneyDeletingHiddenInput.value) {
        moneyDeletingErrorNotStudentChoosed.innerHTML = ''
        moneyDeletingErrorNotStudentChoosed.className = ''

        moneyDeletingErrorNotStudentChoosed.className = 'alert alert-danger'
        moneyDeletingErrorNotStudentChoosed.role = 'alert'
        moneyDeletingErrorNotStudentChoosed.textContent = 'يجب اختيار الطالب قبل إضافة الغرامة'
    } else {
        e.target.submit();
    }
}