const addingPointsForm = document.getElementById('form-adding-points');
const addingPointsHiddenInput = document.getElementById('hidden-input-for-student-id-adding-points')
const addingPointsErrorNotStudentChoosed = document.getElementById('error-section-for-not-choosing-student')
const addingPointsFormSearchStudent = document.getElementById('form-adding-points-search-student');
const addingPointsSearchInput = document.getElementById('adding-points-search-student')
const addingPointsDisplayingStudents = document.getElementById('displaying-students-adding-points')
const addingPointsDisplayingStudentsFormBody = document.getElementById('div-for-displaying-student-in-form-body-adding-points')
const csrfMiddlewareToken = document.querySelector('#form-adding-points-search-student input[name="csrfmiddlewaretoken"]')

addingPointsForm.onsubmit = (e) => {
    e.preventDefault();
    if (!addingPointsHiddenInput.value) {
        addingPointsErrorNotStudentChoosed.innerHTML = ''
        addingPointsErrorNotStudentChoosed.className = ''

        addingPointsErrorNotStudentChoosed.className = 'alert alert-danger'
        addingPointsErrorNotStudentChoosed.role = 'alert'
        addingPointsErrorNotStudentChoosed.textContent = 'يجب اختيار الطالب قبل الإضافة أو الخصم'
    } else {
        e.target.submit();
    }
}


//* Dealing with AJAX

const handleFetchAddingPoints = async () => {
    const csrfToken = csrfMiddlewareToken.value
    
    const res = await fetch('/json/students', {
        method: "POST",
        mode: 'same-origin',
        headers: {
            "Content-Type":"application/json",
            "X-CSRFToken": csrfToken
        },
        body: JSON.stringify({
            "content": addingPointsSearchInput.value
        })
    })
    
    const data = await res.json()
    
    return data
}

addingPointsFormSearchStudent.onsubmit = async (e) => {
    e.preventDefault();
    const data = await handleFetchAddingPoints();
    
    addingPointsDisplayingStudents.innerHTML = ''

    if (data.students.length === 0) {

        const newError = document.createElement('div')
        const textError = document.createTextNode('لا يوجد طالب بهذا الاسم')
        
        newError.appendChild(textError)
        newError.className = 'alert alert-danger'

        addingPointsDisplayingStudents.appendChild(newError)

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
            newDiv.id = `student-in-adding-points-form-id-${student.id}`
            newDiv.role = 'alert'

            addingPointsDisplayingStudents.appendChild(newDiv)
        })

        Array.from(addingPointsDisplayingStudents.children).forEach((div) => {
            const btn = div.children[0]

            btn.onclick = (e) => {
                addingPointsDisplayingStudentsFormBody.className = ''
                addingPointsDisplayingStudentsFormBody.innerHTML = ''

                const stuId = e.target.dataset.id;
                const stuName = e.target.dataset.name;

                const xIcon = document.createElement('i')
                xIcon.className = 'bi bi-x-lg'
                xIcon.style.cursor = 'pointer'

                const textContent = document.createTextNode(`[${stuId}] ${stuName}`)

                addingPointsHiddenInput.value = stuId;

                addingPointsDisplayingStudentsFormBody.className = 'alert alert-primary d-flex justify-content-between align-items-center'
                addingPointsDisplayingStudentsFormBody.appendChild(textContent);
                addingPointsDisplayingStudentsFormBody.appendChild(xIcon)

                // scroll to the bottom of the page
                window.scrollTo(0, document.body.scrollHeight);

                xIcon.onclick = () => {
                    addingPointsHiddenInput.value = ''
                    addingPointsDisplayingStudentsFormBody.className = ''
                    addingPointsDisplayingStudentsFormBody.innerHTML = ''
                }
            }
        })
    }
}


