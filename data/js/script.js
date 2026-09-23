const pizzaData = {{ pizzas | tojson }};

function updatePrices() {
    const pizzaSelect = document.getElementById('pizza');
    const selectedPizza = pizzaSelect.value;
    const sizes = pizzaData[selectedPizza]['sizes'];

    document.getElementById('size-small').textContent = `Small - $${parseFloat(sizes['small']).toFixed(2)}`;
    document.getElementById('size-medium').textContent = `Medium - $${parseFloat(sizes['medium']).toFixed(2)}`;
    document.getElementById('size-large').textContent = `Large - $${parseFloat(sizes['large']).toFixed(2)}`;
}



 window.addEventListener('DOMContentLoaded', updatePrices);