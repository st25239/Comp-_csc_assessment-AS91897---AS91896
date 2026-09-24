    function updatePrices() {
        // 1. Get the dropdown and check which pizza option is currently clicked
        const pizzaSelect = document.getElementById('pizza');
        const selectedOption = pizzaSelect.options[pizzaSelect.selectedIndex];
        
        // 2. Safely grab the prices we stored inside those custom data tags
        const smallPrice = selectedOption.getAttribute('data-small');
        const mediumPrice = selectedOption.getAttribute('data-medium');
        const largePrice = selectedOption.getAttribute('data-large');

        // 3. Inject the text directly into our size labels
        document.getElementById('size-small').textContent = `Small - $${parseFloat(smallPrice).toFixed(2)}`;
        document.getElementById('size-medium').textContent = `Medium - $${parseFloat(mediumPrice).toFixed(2)}`;
        document.getElementById('size-large').textContent = `Large - $${parseFloat(largePrice).toFixed(2)}`;
    }

    // 4. Fire the function immediately when the page loads so the first pizza isn't blank
    window.addEventListener('DOMContentLoaded', updatePrices);