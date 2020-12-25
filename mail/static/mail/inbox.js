document.addEventListener('DOMContentLoaded', function() {

    // Use buttons to toggle between views
    document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
    document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
    document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
    document.querySelector('#compose').addEventListener('click', () => compose_email());

    // By default, load the inbox
    load_mailbox('inbox');
});

function compose_email(mail) {

	// Show compose view and hide other views
	document.querySelector('#emails-view').style.display = 'none';
	document.querySelector('#email-view').style.display = 'none';
	document.querySelector('#compose-view').style.display = 'block';

	// Clear out composition fields
	document.querySelector('#compose-recipients').value = '';
	document.querySelector('#compose-subject').value = '';
	document.querySelector('#compose-body').value = '';

	if (mail) {
		document.querySelector('#compose-recipients').value = mail.sender;
		if (mail.subject === 'Re:'){
			document.querySelector('#compose-subject').value = 'Re:';
		}
		else{
			var mail_subject = "Re:" + " " + mail.subject;
			document.querySelector('#compose-subject').value = mail_subject;
		}
		var body = "On" + " " + mail.timestamp + " " + mail.sender + " " + "wrote:" + " " + mail.body
		document.querySelector('#compose-body').value = body;
		};
  

	document.querySelector('form').onsubmit = function() {  
    fetch('/emails', {
		method: 'POST',
		body: JSON.stringify({
			recipients: document.querySelector('#compose-recipients').value,
			subject: document.querySelector('#compose-subject').value,
			body: document.querySelector('#compose-body').value
		})
    })
    .then(response => response.json())
    .then(result => {
        console.log(result);

		
		if(result['message'] == "Email sent successfully."){
            load_mailbox('sent');
        }
		else{
			const mess = document.querySelector("#message");
			mess.innerHTML = `<div class="alert alert-danger">${result.error}</div>`;
		}
		
    })
	.catch(error => {
        console.log('Error', error);
    });
	return false;
	}; 

}

function load_mailbox(mailbox) {
  
    // Show the mailbox and hide other views.
    document.querySelector('#emails-view').style.display = 'block';
    document.querySelector('#compose-view').style.display = 'none';
    document.querySelector('#email-view').style.display = 'none';

    // Clear the mailbox area of stale content.
    document.querySelector('#emails-view').innerHTML = "";

    // Show the mailbox name.
    document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;


    fetch(`/emails/${mailbox}`)
    .then(response => response.json())
    .then(emails => {
        console.log(emails);

        emails.forEach((email) => {
			const elem = document.createElement('div');
			elem.innerHTML = `<p><b>sender:</b> ${email.sender}</p>
			<p><b>subject:</b> ${email.subject}</p>
			<p><b>timestamp:</b> ${email.timestamp}</p>`;

			if (email.read === true){
				elem.style.background = "#E8E8E8";
			} 

            elem.className = "elem";
			document.querySelector('#emails-view').append(elem);
            
            elem.addEventListener('click', function() {
				console.log('This element has been clicked!');
                load_mail(email.id, mailbox);
            })

            
            
        })

    });
}


// Adding a new function to show the email.
function load_mail(email_id, mailbox) {

    // Show the selected email and hide other views.
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'none';
    document.querySelector('#email-view').style.display = 'block';

    // Clearing the previous stale content.
    document.querySelector('#email-view').innerHTML = "";


	fetch(`/emails/${email_id}`, {
		method: 'PUT',
		body: JSON.stringify({
			read: true
		})
	})

    fetch(`/emails/${email_id}`)
    .then(response => response.json())
    .then(email => {
		console.log(email);    
        		
		
				
        const el = document.createElement('div');
		el.innerHTML = `<div id="ar"></div>
		<div id="unar"></div>
		<hr>
		<p><b>sender:</b> ${email.sender}</p>
		<p><b>recipients:</b> ${email.recipients}</p>
		<p><b>subject:</b> ${email.subject}</p>
		<p><b>timestamp:</b> ${email.timestamp}</p>
		<hr>
		<p><b>body:</b></p>
		<p>${email.body}</p>
		<hr>
		<div id="repl"></div>
		`;
		
		el.className = "el";
		document.querySelector('#email-view').append(el);
		
		if (mailbox === 'inbox'){
			const arch = document.createElement('button');
			arch.innerHTML = `Archive`;
			arch.className = "btn btn-sm btn-outline-primary";

			document.querySelector('#ar').append(arch);
			
			arch.addEventListener('click', function() {
				console.log(`You press Archive button`);

				fetch(`/emails/${email_id}`, {
					method: 'PUT',
					body: JSON.stringify({
						archived: true
					})
				})
				load_mailbox('inbox')
			});

							
		
		
			const repl = document.createElement('button');
			repl.innerHTML = `Reply`;
			repl.addEventListener('click', function() {
				console.log(`You press Reply button`);
				compose_email(email)            
			});

			repl.className = "btn btn-sm btn-outline-primary";

			document.querySelector('#repl').append(repl);		
			
		}




	
		
		if (mailbox === 'archive'){
			const unarch = document.createElement('button');
			unarch.innerHTML = 'Unarchive';
			unarch.className = "btn btn-sm btn-outline-primary";

			document.querySelector('#unar').append(unarch);
			
			unarch.addEventListener('click', function() {
				console.log(`You press Unarchive button`);

				fetch(`/emails/${email_id}`, {
					method: 'PUT',
					body: JSON.stringify({
						archived: false
					})
				})
				load_mailbox('inbox')
			})

			
			
			
		}		
		
		
	})
}

