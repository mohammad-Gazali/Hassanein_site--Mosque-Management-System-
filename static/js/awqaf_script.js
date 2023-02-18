const awqafStudentForm = document.getElementById('awqaf-student-form');
const awqafStudentForm2 = document.getElementById('awqaf-student-form-2');
const awqafMainForm = document.getElementById('awqaf-main-form');
const awqafMainForm2 = document.getElementById('awqaf-main-form-2');
const awqafSectionsInput = document.getElementById('awqaf-q-sections');
const awqafDisplayingStudents = document.getElementById('awqaf-displaying-students');
const awqafDisplayingStudents2 = document.getElementById('awqaf-displaying-students-2');
const awqafDisplayingStudentsFormBody = document.getElementById('awqaf-displaying-students-form-body');
const awqafDisplayingStudentsFormBody2 = document.getElementById('awqaf-displaying-students-form-body-2');
const awqafHiddenInput = document.getElementById('awqaf-hidden-input');
const awqafHiddenInput2 = document.getElementById('awqaf-hidden-input-2');
const awqafErrorNotStudentChoosed = document.getElementById('awqaf-error-not-student-choosed');
const awqafErrorNotStudentChoosed2 = document.getElementById('awqaf-error-not-student-choosed-2');
const awqafErrorInvalidNumberForSectionsInput = document.getElementById('awqaf-error-invalid-number-for-sections-input');
const awqafHelpBtns = document.querySelectorAll('[data-help]');
const csrfToken = document.querySelector('#awqaf-student-form input[name="csrfmiddlewaretoken"]');
const typeOfAwqafTestQ = document.getElementById('type-of-awqaf-test-q');
const typeOfAwqafTestNoQ = document.getElementById('type-of-awqaf-test-no-q');
const firstSectionForDisplayWithTypeOfAwqafTest = document.getElementById('first-section-for-display-with-type-of-awqaf-test');
const secondSectionForDisplayWithTypeOfAwqafTest = document.getElementById('second-section-for-display-with-type-of-awqaf-test');


/* Handling the Type of Awqaf Test (Q [or] No-Q) */

typeOfAwqafTestQ.onchange = () => {
    if (typeOfAwqafTestQ.checked) {
        firstSectionForDisplayWithTypeOfAwqafTest.classList.remove("d-none");
        secondSectionForDisplayWithTypeOfAwqafTest.classList.add("d-none");
    } else {
        firstSectionForDisplayWithTypeOfAwqafTest.classList.add("d-none");
        secondSectionForDisplayWithTypeOfAwqafTest.classList.remove("d-none");
    }
}

typeOfAwqafTestNoQ.onchange = () => {
    if (typeOfAwqafTestQ.checked) {
        firstSectionForDisplayWithTypeOfAwqafTest.classList.remove("d-none");
        secondSectionForDisplayWithTypeOfAwqafTest.classList.add("d-none");
    } else {
        firstSectionForDisplayWithTypeOfAwqafTest.classList.add("d-none");
        secondSectionForDisplayWithTypeOfAwqafTest.classList.remove("d-none");
    }
}



/* Search Student */
    //? Search Student First Form

awqafStudentForm.onsubmit = async (e) => {

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

    awqafDisplayingStudents.innerHTML = '';

    if (data.students.length === 0) {

        const newError = document.createElement('div')
        const textError = document.createTextNode('لا يوجد طالب بهذا الاسم')
        
        newError.appendChild(textError)
        newError.className = 'alert alert-danger'

        awqafDisplayingStudents.appendChild(newError)

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

            awqafDisplayingStudents.appendChild(newDiv)
        })

        Array.from(awqafDisplayingStudents.children).forEach((div) => {
            const btn = div.children[0]

            btn.onclick = (e) => {
                awqafDisplayingStudentsFormBody.className = ''
                awqafDisplayingStudentsFormBody.innerHTML = ''

                const stuId = e.target.dataset.id;
                const stuName = e.target.dataset.name;

                const xIcon = document.createElement('i')
                xIcon.className = 'bi bi-x-lg'
                xIcon.style.cursor = 'pointer'

                const textContent = document.createTextNode(`[${stuId}] ${stuName}`)

                awqafHiddenInput.value = stuId;

                awqafDisplayingStudentsFormBody.className = 'alert alert-primary d-flex justify-content-between align-items-center'
                awqafDisplayingStudentsFormBody.appendChild(textContent);
                awqafDisplayingStudentsFormBody.appendChild(xIcon)

                xIcon.onclick = () => {
                    awqafHiddenInput.value = ''
                    awqafDisplayingStudentsFormBody.className = ''
                    awqafDisplayingStudentsFormBody.innerHTML = ''
                }
            }
        }) 
    }           
}

    //? Search Student Second Form

awqafStudentForm2.onsubmit = async (e) => {

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

    awqafDisplayingStudents2.innerHTML = '';

    if (data.students.length === 0) {

        const newError = document.createElement('div')
        const textError = document.createTextNode('لا يوجد طالب بهذا الاسم')
        
        newError.appendChild(textError)
        newError.className = 'alert alert-danger'

        awqafDisplayingStudents2.appendChild(newError)

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

            awqafDisplayingStudents2.appendChild(newDiv)
        })

        Array.from(awqafDisplayingStudents2.children).forEach((div) => {
            const btn = div.children[0]

            btn.onclick = (e) => {
                awqafDisplayingStudentsFormBody2.className = ''
                awqafDisplayingStudentsFormBody2.innerHTML = ''

                const stuId = e.target.dataset.id;
                const stuName = e.target.dataset.name;

                const xIcon = document.createElement('i')
                xIcon.className = 'bi bi-x-lg'
                xIcon.style.cursor = 'pointer'

                const textContent = document.createTextNode(`[${stuId}] ${stuName}`)

                awqafHiddenInput2.value = stuId;

                awqafDisplayingStudentsFormBody2.className = 'alert alert-primary d-flex justify-content-between align-items-center'
                awqafDisplayingStudentsFormBody2.appendChild(textContent);
                awqafDisplayingStudentsFormBody2.appendChild(xIcon)

                xIcon.onclick = () => {
                    awqafHiddenInput2.value = ''
                    awqafDisplayingStudentsFormBody2.className = ''
                    awqafDisplayingStudentsFormBody2.innerHTML = ''
                }
            }
        }) 
    }           
}


// error no student choosed in the main form 
    //? First Form

awqafMainForm.onsubmit = (e) => {
    e.preventDefault();

    let go = true;

    if (!awqafHiddenInput.value) {

        go = false;

        awqafErrorNotStudentChoosed.innerHTML = '';
        awqafErrorNotStudentChoosed.className = '';

        awqafErrorNotStudentChoosed.className = 'alert alert-danger';
        awqafErrorNotStudentChoosed.role = 'alert';
        awqafErrorNotStudentChoosed.textContent = 'يجب اختيار الطالب قبل إضافة السبر';

    } else {
        awqafErrorNotStudentChoosed.innerHTML = '';
        awqafErrorNotStudentChoosed.className = '';
    }

    if (!validate_value_for_q_test_awqaf(awqafSectionsInput.value)) {

        go = false;

        awqafErrorInvalidNumberForSectionsInput.innerHTML = '';
        awqafErrorInvalidNumberForSectionsInput.className = '';

        awqafErrorInvalidNumberForSectionsInput.className = 'alert alert-danger';
        awqafErrorInvalidNumberForSectionsInput.role = 'alert';
        awqafErrorInvalidNumberForSectionsInput.innerHTML = 'يجب أن يكون رقم الجزء أقل من 30 <i class="bi bi-emoji-smile"></i>';
    } else {

        awqafErrorInvalidNumberForSectionsInput.innerHTML = '';
        awqafErrorInvalidNumberForSectionsInput.className = '';

    }

    if (go) {
        e.target.submit();
    }
}


    //? Second Form
awqafMainForm2.onsubmit = (e) => {
    e.preventDefault();

    if (!awqafHiddenInput2.value) {

        awqafErrorNotStudentChoosed2.innerHTML = '';
        awqafErrorNotStudentChoosed2.className = '';

        awqafErrorNotStudentChoosed2.className = 'alert alert-danger';
        awqafErrorNotStudentChoosed2.role = 'alert';
        awqafErrorNotStudentChoosed2.textContent = 'يجب اختيار الطالب قبل إضافة السبر';

    } else {

        e.target.submit();
        
    }
}

function validate_value_for_q_test_awqaf(value) {
    const my_regex = /\s+/g;
    const my_arr = value.split(my_regex);
    return my_arr.every(item => parseInt(item) <= 30 || item === '')
}


/* Help Buttons */

awqafHelpBtns.forEach((btn) => {
    btn.onclick = () => {
        const start = parseInt(btn.dataset.start);
        const end = parseInt(btn.dataset.end);
        
        let result;

        for (let i = start; i <= end; i++) {
            if (i === start) {
                result = `${i}`
            } else {
                result += ` ${i}`
            }
        }

        awqafSectionsInput.value = result;
    }
})