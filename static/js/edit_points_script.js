let editPointsForm = document.getElementById('form-edit-points');
let editPointsTypeChecks = Array.from(document.querySelectorAll('#form-edit-points div input[type="radio"]'))
let editPointsAddOptions = Array.from(document.querySelectorAll('#form-edit-points .edit-point-cause-add-option'))
let editPointsDeleteOptions = Array.from(document.querySelectorAll('#form-edit-points .edit-point-cause-delete-option'))
let editPointsSubmitBtn = document.querySelector('#form-edit-points button')
let editPointsHiddenInput = document.getElementById('hidden-input-for-student-id-edit-points')
let editPointsErrorNotStudentChoosed = document.getElementById('error-section-for-not-choosing-student')
let editPointsFormSearchStudent = document.getElementById('form-edit-points-search-student');
let editPointsSearchInput = document.getElementById('edit-points-search-student')
let editPointsDisplayingStudents = document.getElementById('displaying-students-edit-points')
let editPointsDisplayingStudentsFormBody = document.getElementById('div-for-displaying-student-in-form-body-edit-points')
let csrfMiddlewareToken = document.querySelector('#form-edit-points-search-student input[name="csrfmiddlewaretoken"]')



editPointsForm.onsubmit = (e) => {
    e.preventDefault();
    if (!editPointsHiddenInput.value) {
        editPointsErrorNotStudentChoosed.innerHTML = ''
        editPointsErrorNotStudentChoosed.className = ''

        editPointsErrorNotStudentChoosed.className = 'alert alert-danger'
        editPointsErrorNotStudentChoosed.role = 'alert'
        editPointsErrorNotStudentChoosed.textContent = 'يجب اختيار الطالب قبل الإضافة أو الخصم'
    } else {
        e.target.submit();
    }
}


editPointsTypeChecks.forEach((item) => {
    item.onchange = () => {
        if (editPointsTypeChecks[0].checked) {
            editPointsAddOptions.forEach((item, index) => {
                item.classList.remove("d-none")
                if (index === 0) {
                    item.selected = true
                }
            })
        
            editPointsDeleteOptions.forEach((item) => {
                item.classList.add("d-none")
            })
        
            editPointsSubmitBtn.classList.remove('btn-danger')
            editPointsSubmitBtn.classList.add('btn-success')
            editPointsSubmitBtn.innerHTML = 'إضافة <i class="bi bi-plus-circle"></i>'
        
        } else {
        
            editPointsAddOptions.forEach((item) => {
                item.classList.add("d-none")
            })
        
            editPointsDeleteOptions.forEach((item, index) => {
                item.classList.remove("d-none")
                if (index === 0) {
                    item.selected = true
                }
            })
        
            editPointsSubmitBtn.classList.remove('btn-success')
            editPointsSubmitBtn.classList.add('btn-danger')
            editPointsSubmitBtn.innerHTML = 'خصم <i class="bi bi-dash-circle"></i>'
        
        }
    }
})



//* Dealing with AJAX

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
            "content": editPointsSearchInput.value
        })
    })
    
    const data = await res.json()
    
    return data
}

editPointsFormSearchStudent.onsubmit = async (e) => {
    e.preventDefault();
    const data = await handleFetchEditPoints();
    
    editPointsDisplayingStudents.innerHTML = ''

    if (data.students.length === 0) {

        const newError = document.createElement('div')
        const textError = document.createTextNode('لا يوجد طالب بهذا الاسم')
        
        newError.appendChild(textError)
        newError.className = 'alert alert-danger'

        editPointsDisplayingStudents.appendChild(newError)

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

            editPointsDisplayingStudents.appendChild(newDiv)
        })

        Array.from(editPointsDisplayingStudents.children).forEach((div) => {
            const btn = div.children[0]

            btn.onclick = (e) => {
                editPointsDisplayingStudentsFormBody.className = ''
                editPointsDisplayingStudentsFormBody.innerHTML = ''

                const stuId = e.target.dataset.id;
                const stuName = e.target.dataset.name;

                const xIcon = document.createElement('i')
                xIcon.className = 'bi bi-x-lg'
                xIcon.style.cursor = 'pointer'

                const textContent = document.createTextNode(`[${stuId}] ${stuName}`)

                editPointsHiddenInput.value = stuId;

                editPointsDisplayingStudentsFormBody.className = 'alert alert-primary d-flex justify-content-between align-items-center'
                editPointsDisplayingStudentsFormBody.appendChild(textContent);
                editPointsDisplayingStudentsFormBody.appendChild(xIcon)

                xIcon.onclick = () => {
                    editPointsHiddenInput.value = ''
                    editPointsDisplayingStudentsFormBody.className = ''
                    editPointsDisplayingStudentsFormBody.innerHTML = ''
                }
            }
        })

    }


}


