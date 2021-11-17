const search_input = document.getElementById('search');
let search_term = '';

search_input.addEventListener('input', e => {
    // saving the input value
    search_term = e.target.value;

    // re-displaying countries based on the new search_term
    showResults(search_term);
});

var searchResults = document.querySelector("#searchResults");
let results;

const fetchResults = async (query) => {
    if (query.length > 0) {
        results = await fetch(
            'http://localhost:5000/search_spotify',
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    "query": query
                })
            }
        ).then(
            res => res.json()
        );
    }
    else {
        results = Object();
        results.items = Array();
    }
};

const showResults = async (query) => {
    searchResults.innerHTML = '';
    await fetchResults(query);
    const ul = document.createElement('ul');
    ul.classList.add('results');
    results.items.forEach(result => {
        const li = document.createElement('li');
        li.classList.add('result-item');
        const track_name = document.createElement('div');
        track_name.innerText = result.name;
        li.appendChild(track_name);
        ul.appendChild(li);
    });
    searchResults.appendChild(ul);

};
