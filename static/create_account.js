const form = document.getElementById('form')   


form.addEventListener('submit', (e) => {
    
    //create_account
    const email = document.querySelector('#email').value
    const pass = document.querySelector('#password').value
    const fname = document.querySelector('#firstname').value
    const minit = document.querySelector('#minit').value
    const lname = document.querySelector('#lastname').value
    const address = document.querySelector('#address').value
    const ssn = document.querySelector('#ssn').value

    let dept = document.querySelector('#dept')
    let masters = document.querySelector('#masters')
    let phd = document.querySelector('#phd')
    let ad_id = document.querySelector('#ad_id')

    let messages = []

    if (dept) {
        dept = dept.value
    }

    if (ad_id) {
        ad_id = ad_id.value
    }
    

    if (!/^.+@.+$/.test(email) || email.length > 50) {
        messages.push('Invalid email')
    }
    if (pass.length > 50) {
        messages.push('Password is too long')
    }
    if (fname.length > 50) {
        messages.push('Name cannot be longer than 50 characters')
    }
    if (!/^[a-zA-Z]+$/.test(fname)) {
        messages.push('First name must be letters only')
    }

    if (minit.length > 1) {
        messages.push('Middle initial can only be one letter')
    }
    if (minit !== '') {
        if (!/^[a-zA-Z]+$/.test(minit)) {
            messages.push('Middle initial must be a letter')
        }
    }
    if (lname.length > 50) {
        messages.push('Last name cannot be longer than 50 characters')
    }
    if (!/^[a-zA-Z-\s]+$/.test(lname)) {
        messages.push('Last name must be letters only')
    }
   
    if (address.length > 100) {
        messages.push('Address cannot be longer than 100 characters')
    }

    if (ssn.length !== 9 || !/^\d+$/.test(ssn)) {
        messages.push('SSN is invalid. Must be 9 numbers')
    }
    if (dept !== null) {
        if (!/^[a-zA-Z]+$/.test(dept)) {
            messages.push('Department must be letters only')
        }
        if (dept.length > 50) {
            messages.push('Department must be max 50 characters')
        }
    }

    if (masters) {
        if (phd) {
            if (masters.checked || phd.checked) {
                if (ad_id) {
                    if (ad_id.length !== 8 || !/^\d+$/.test(ad_id)) {
                        messages.push('Advisor ID must be a valid advisor id')
                    }
                }
                if (masters.checked && phd.checked) {
                    messages.push('Student can only be Masters or PhD')
                }
            }
        }
    }
    if (phd) {
        if (masters) {
            if (masters.checked || phd.checked) {
                if (ad_id) {
                    if (ad_id.length !== 8 || !/^\d+$/.test(ad_id)) {
                        messages.push('Advisor ID must be a valid advisor id')
                    }
                }
                if (masters.checked && phd.checked) {
                    messages.push('Student can only be Masters or PhD')
                }
            }
        }
    }

    if (messages.length > 0 ) {
        e.preventDefault()
        messages = messages.join('\n')
        alert(messages)
    }
})
