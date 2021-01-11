function opinion()
{
    let op = document.querySelector('#op').value;
    if (op === '')
    {
        op = '';
    }
    document.querySelector('#result').innerHTML = op;
}
