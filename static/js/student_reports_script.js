const studentsReportsSearchStudentSection = document.getElementById('search-student-section-students-reports');
const studentsReportsFormSearchStudent = document.querySelector('#search-student-section-students-reports form');
const studentsReportsTitle = studentsReportsSearchStudentSection.closest('h3');
const studentsReportsRadioInputs = document.querySelectorAll('#reports-form-students-reports input[name="type"]');
const studentsReportsSearchInput = document.getElementById('students-reports-search-student');
const studentsReportsHiddenInput = document.querySelector('#reports-form-students-reports input[name="student-id"]');
const studentsReportsDisplayingStudents = document.getElementById('displaying-students-students-reports') ;
const studentsReportsDisplayingStudentsFormBody = document.getElementById('div-for-displaying-student-in-form-body-students-reports');
const studentsReportsErrorNotStudentChoosed = document.getElementById('error-section-for-not-choosing-student-students-reports');
const studentsReportsReportsForm = document.getElementById('reports-form-students-reports');
const csrfMiddlewareToken = document.querySelector('#reports-form-students-reports input[name="csrfmiddlewaretoken"]');


Array.from(studentsReportsRadioInputs).forEach((item, index) => {
    item.onchange = () => {
        if (index !== 2) {
            studentsReportsSearchStudentSection.classList.add('d-none')
            studentsReportsDisplayingStudentsFormBody.classList.add('d-none')
            studentsReportsReportsForm.onsubmit = (e) => {
                e.target.submit()
            }
        } else {
            studentsReportsSearchStudentSection.classList.remove('d-none')
            studentsReportsDisplayingStudentsFormBody.classList.remove('d-none')
        }
    }
})

studentsReportsReportsForm.onsubmit = (e) => {
    e.preventDefault();
    if (!studentsReportsHiddenInput.value && studentsReportsRadioInputs[2].checked) {
        studentsReportsErrorNotStudentChoosed.innerHTML = ''
        studentsReportsErrorNotStudentChoosed.className = ''

        studentsReportsErrorNotStudentChoosed.className = 'alert alert-danger'
        studentsReportsErrorNotStudentChoosed.role = 'alert'
        studentsReportsErrorNotStudentChoosed.textContent = 'يجب اختيار الطالب قبل إيجاد التقرير'
    } else {
        e.target.submit();
    }
}

//* Handling AJAX
const handleFetchEditPoints = async () => {
    const csrfToken = csrfMiddlewareToken.value
    
    const res = await fetch('/json/students', {
        method: "POST",
        mode: 'same-origin',
        headers: {
            "Content-Type":"application/json",
            "X-CSRFToken": csrfToken
        },
        body: JSON.stringify({
            "content": studentsReportsSearchInput.value
        })
    })
    
    const data = await res.json()
    
    return data
}


studentsReportsFormSearchStudent.onsubmit = async (e) => {
    e.preventDefault();
    const data = await handleFetchEditPoints();
    
    studentsReportsDisplayingStudents.innerHTML = ''

    if (data.students.length === 0) {

        const newError = document.createElement('div')
        const textError = document.createTextNode('لا يوجد طالب بهذا الاسم')
        
        newError.appendChild(textError)
        newError.className = 'alert alert-danger'

        studentsReportsDisplayingStudents.appendChild(newError)

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

            studentsReportsDisplayingStudents.appendChild(newDiv)
        })

        Array.from(studentsReportsDisplayingStudents.children).forEach((div) => {
            const btn = div.children[0]

            btn.onclick = (e) => {
                studentsReportsDisplayingStudentsFormBody.className = ''
                studentsReportsDisplayingStudentsFormBody.innerHTML = ''

                const stuId = e.target.dataset.id;
                const stuName = e.target.dataset.name;

                const xIcon = document.createElement('i')
                xIcon.className = 'bi bi-x-lg'
                xIcon.style.cursor = 'pointer'

                const textContent = document.createTextNode(`[${stuId}] ${stuName}`)

                studentsReportsHiddenInput.value = stuId;

                studentsReportsDisplayingStudentsFormBody.className = 'alert alert-primary d-flex justify-content-between align-items-center'
                studentsReportsDisplayingStudentsFormBody.appendChild(textContent);
                studentsReportsDisplayingStudentsFormBody.appendChild(xIcon)

                xIcon.onclick = () => {
                    studentsReportsHiddenInput.value = ''
                    studentsReportsDisplayingStudentsFormBody.className = ''
                    studentsReportsDisplayingStudentsFormBody.innerHTML = ''
                }
            }
        })

    }

}