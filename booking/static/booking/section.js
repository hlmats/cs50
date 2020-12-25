function showSect(value) {
	if (value=='rat'){
		document.querySelector('#sec_rat').style.display = 'block';
		document.querySelector('#sec_inc_price').style.display = 'none';
		document.querySelector('#sec_dec_price').style.display = 'none';
	}
	else if (value=='inc_price'){
		document.querySelector('#sec_rat').style.display = 'none';
		document.querySelector('#sec_inc_price').style.display = 'block';
		document.querySelector('#sec_dec_price').style.display = 'none';
	}
	else if (value=='dec_price'){
		document.querySelector('#sec_rat').style.display = 'none';
		document.querySelector('#sec_inc_price').style.display = 'none';
		document.querySelector('#sec_dec_price').style.display = 'block';
	}
	else {}
}





document.addEventListener('DOMContentLoaded', function() {
	document.querySelector('#sec_rat').style.display = 'block';
	document.querySelector('#sec_inc_price').style.display = 'none';
	document.querySelector('#sec_dec_price').style.display = 'none';
	document.querySelector('select').onchange = function() {
		vl=this.value;
		showSect(vl)
	}
})